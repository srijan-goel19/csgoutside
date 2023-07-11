from fastapi import APIRouter, HTTPException, WebSocket
from models.user import User, Hardware, Shot
from config.db import conn
from schemas.user import userEntity, usersEntity
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import json
import asyncio
# import requests

user = APIRouter()

@user.get('/api')
async def find_all_users():
    return usersEntity(conn.csgoutside.user.find())
    
@user.post('/send-shot')
async def insert_user(shot: Shot):
    user_id = shot.playerID
    player = conn.csgoutside.user.find_one({"_id": ObjectId(user_id)})
    if int(player["health"]) <= 0:
        # player is dead
        return ("Shot too late you're dead")
    else:
        # Send shot thru socket to sarth then store in db
        # Do we need to store in db?
        ml_shot = dict(shot)
        ml_shot["ml_method"] = "shot"
        ml_shot["user_id"] = ml_shot.pop("playerID")
        await asyncio.gather(*[ml.send_text(json.dumps(ml_shot)) for ml in connected_ml])
        conn.csgoutside.shot.insert_one(dict(shot))
        return ("Sent Shot")

@user.post('/create-user')
async def create_user(user: User):
    existing_user = conn.csgoutside.user.find_one({"name": user.name})
    if existing_user:
        update_query = {"$set": {"team": user.team, "shirt": user.shirt}}
        conn.csgoutside.user.update_one({"_id": existing_user["_id"]}, update_query)
        # send updated user to ML model
        updated_user = dict(conn.csgoutside.user.find_one({"name": user.name}))
        updated_user["ml_method"] = "user"
        updated_user["user_id"] = str(updated_user["_id"])
        del updated_user["_id"]
        await asyncio.gather(*[ml.send_text(json.dumps(updated_user)) for ml in connected_ml])
        return {"id": str(existing_user['_id'])}
    result = conn.csgoutside.user.insert_one(dict(user))
    # send new user to ML model
    new_user = dict(conn.csgoutside.user.find_one({"_id": result.inserted_id}))
    new_user["ml_method"] = "user"
    new_user["user_id"] = str(new_user["_id"])
    del new_user["_id"]
    await asyncio.gather(*[ml.send_text(json.dumps(new_user)) for ml in connected_ml])
    return {"id": str(result.inserted_id)}

@user.get('/find-user/{user_id}')
async def find_user(user_id: str):
    user = conn.csgoutside.user.find_one({"_id": ObjectId(user_id)})
    return json.loads(json.dumps(user["name"], default=str))

@user.post('/update-health/{user_id}/{damage}/{shooter_id}')
async def update_health(user_id: str, damage: str, shooter_id: str):
    user = conn.csgoutside.user.find_one({'_id': ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if int(user["health"]) <= 0:
        return 1 # return positive for update kills bug
    new_health = int(user["health"]) - int(damage)
    if new_health <= 0:
        new_health = 0
        # update killed by
        update_query = {"$set": {"health": new_health, "killedby": shooter_id}}
        conn.csgoutside.user.update_one({'_id': ObjectId(user_id)}, update_query)
    else:
        conn.csgoutside.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'health': new_health}})
    game_state["players"] = usersEntity(conn.csgoutside.user.find())
    await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients
    # return {"message": "User health updated successfully"}
    return new_health

@user.post('/update-kills/{user_id}/{kills}')
async def update_kills(user_id: str, kills: str):
    user = conn.csgoutside.user.find_one({'_id': ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    new_kills = int(user["kills"]) + int(kills)
    conn.csgoutside.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'kills': str(new_kills)}})
    game_state["players"] = usersEntity(conn.csgoutside.user.find())
    await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients
    await updateTeamStatus()
    return {"message": "User kills updated successfully"}

# @user.post('/update-killedby/{user_id}/{killedby}')
# async def update_killedby(user_id: str, killedby: str):
#     user = conn.csgoutside.user.find_one({'_id': ObjectId(user_id)})
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     conn.csgoutside.user.update_one({'_id': ObjectId(user_id)}, {'$set': {'killedby': killedby}})
#     game_state["players"] = usersEntity(conn.csgoutside.user.find())
#     await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients
#     return {"message": "User killedby updated successfully"}
    
@user.post('/')
async def create_bomb(message: Hardware):
    conn.csgoutside.hardware.insert_one(dict(message))
    return ("Created User")

@user.post('/resetDB')
async def resetDB():
    global state, end_time, game_over, connected_clients, connected_ml
    state = "preround"
    game_state["state"] = state
    await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients
    connected_clients = set()
    end_time = 0
    game_over = False
    ml_reset = {}
    ml_reset["reset"] = "reset"
    print(ml_reset)

    await asyncio.gather(*[ml.send_text(json.dumps(ml_reset)) for ml in connected_ml])
    conn.csgoutside.user.drop()
    conn.csgoutside.shot.drop()
    return ("DB Reset")

async def send_message(websocket: WebSocket):
    time = 0 
    while True:
        await asyncio.sleep(5)  # wait for 5 seconds
        time = datetime.utcnow().strftime("%H:%M:%S")
        message = {"text": f"Hello from backend {time}"}
        print('Sent message:', message)
        await websocket.send_text(json.dumps(message))
        
connected_clients = set()
state = "preround"
end_time = 0
game_state = {}
game_over = False

def playerJoinHandler(data):
    print('Player Joined:', data)

def gameStartHandler(data):
    global state, end_time
    # if the game has already been started do nothing
    if state != "preround":
        return
    # end_time = (datetime.utcnow() + timedelta(minutes=4)).timestamp()
    end_time = (datetime.utcnow() + timedelta(seconds=100)).timestamp()
    game_state["winners"] = "Defusers"
    if data == True:
        state = "attack"

def hardwareHandler(data):
    global state, end_time, game_over
    # if the game has already been started do nothing
    # if state != "preround":
    #     return
    if data:
        if data == "planted":
            state = data
            end_time = (datetime.utcnow() + timedelta(seconds=45)).timestamp() # give 45 secs to defuse
            game_state["winners"] = "Planters"
        if data == "defused":
            state = data
            game_state["winners"] = "Defusers"
            game_over = True
        if data == "exploded":
            state = data
            game_state["winners"] = "Planters"
            game_over = True


@user.websocket("/fe-ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket) # Add the new client to the set of connected clients
    # task = asyncio.create_task(send_message(websocket))
    try:
        while True:
            message = json.loads(await websocket.receive_text())
            print(message)
            if message["id"] == "playerJoin":
                playerJoinHandler(message["data"])
            elif message["id"] == "gameStart":
                gameStartHandler(message["data"])
            elif message["id"] == "backend":
                #do hardware stuff and update states and send to users
                # print("printing in socket before handler:" + message["data"])
                hardwareHandler(message["data"])
            game_state["players"] = usersEntity(conn.csgoutside.user.find())
            game_state["state"] = state
            game_state["end_time"] = end_time
            game_state["game_over"] = game_over
            # print(game_state["state"])
            await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients

    except Exception as e: print(e)
        # task.cancel()  # stop the send_message task when the client disconnects
    finally:
        connected_clients.remove(websocket) # Remove the client from the set of connected clients when the connection is closed

async def updateTeamStatus():
    global game_over, game_state
    # queryPlanters = {"health": {"$gt": 0}, "team": "Planters"}
    # queryPlanters = {"team": "Planters", "$expr": {"$gt": [{"$toInt": "$health"}, 0]}}
    # queryDefusers = {"team": "Defusers", "$expr": {"$gt": [{"$toInt": "$health"}, 0]}}
    # # queryDefusers = {"health": {"$gt": 0}, "team": "Defusers"}
    # countAlivePlanters = conn.csgoutside.user.count_documents(queryPlanters)
    # countAliveDefusers = conn.csgoutside.user.count_documents(queryDefusers)
    queryPlanters = {"team": "Planter"}
    queryDefusers = {"team": "Defuser"}
    projection = {"health": 1, "_id": 0}
    # Fetch documents from MongoDB
    # planters = conn.csgoutside.user.find(queryPlanters).to_list(length=None)
    # defusers = conn.csgoutside.user.find(queryDefusers).to_list(length=None)
    planters = []
    for doc in conn.csgoutside.user.find(queryPlanters, projection):
        planters.append(doc)

    defusers = []
    for doc in conn.csgoutside.user.find(queryDefusers, projection):
        defusers.append(doc)
    # print(planters)
    # print(defusers)
    # Perform numeric comparison in Python code
    countAlivePlanters = sum(1 for doc in planters if int(doc["health"]) > 0)
    countAliveDefusers = sum(1 for doc in defusers if int(doc["health"]) > 0)
    # print("outer Alive Planters:", countAlivePlanters)
    # print("outer Alive Defusers:", countAliveDefusers)
    if countAlivePlanters == 0 and state != "planted":
        print("Alive Planters:", countAlivePlanters)
        game_over = True 
        game_state["winners"] = "Defusers"
        game_state["game_over"] = game_over
        await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients
    elif countAliveDefusers == 0:
        print("Alive Defusers:", countAliveDefusers)
        game_state["winners"] = "Planters"
        game_over = True
        game_state["game_over"] = game_over
        await asyncio.gather(*[client.send_text(json.dumps(game_state)) for client in connected_clients]) # Send the message to all connected clients
    



async def mlResponseHandler(message):
    # might cause concurrency issues
    # print(message["shooter_id"])
    # print(message["victim_id"])
    # print(message["damage"])
    loop = asyncio.get_event_loop()
    new_health = await loop.create_task(update_health(message["victim_id"], message["damage"], message["shooter_id"]))
    # new_health = task.result()
    # print(new_health)
    # new_health = await update_health(message["victim_id"], message["damage"], message["shooter_id"])
    if new_health <= 0:
        loop.create_task(update_kills(message["shooter_id"], "1"))
        # await update_kills(message["shooter_id"], "1")
    

connected_ml = set()
@user.websocket("/ml-ws")
async def websocket_endpoint_ml(websocket: WebSocket):
    await websocket.accept()
    connected_ml.add(websocket) # Add the new ml to the set of connected clients
    try:
        while True:
            message = json.loads(await websocket.receive_text())
            # print(message)
            if message["id"]:
                if message["id"] == "shot_response":
                    await mlResponseHandler(message)
                    print(message)
    except Exception as e: print(e)
        # task.cancel()  # stop the send_message task when the client disconnects
    finally:
        connected_ml.remove(websocket) # Remove the ml from the set of connected clients when the connection is closed