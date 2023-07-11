import uvicorn
import websockets
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import user
import threading
app = FastAPI()
app2 = FastAPI()
# app2 = FastAPI()
app.include_router(user)
app2.include_router(user)


origins = [
    "http://206.87.112.30:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# def run_app():
#     uvicorn.run(app, host="10.0.0.248", port=8000)

# def run_app2():
#     uvicorn.run(app2, host="10.0.0.248", port=8002)

# if __name__ == "__main__":
#     thread1 = threading.Thread(target=run_app)
#     thread2 = threading.Thread(target=run_app2)

#     thread1.start()
#     thread2.start()

#     thread1.join()
#     thread2.join()

if __name__ == "__main__":
    uvicorn.run(app, host="206.87.112.30", port=8000)
    # uvicorn.run(app, host="10.0.0.248", port=8000)
    # uvicorn.run(app2, host="192.168.43.140", port=8002)
    # uvicorn.run(app2, host="10.0.0.248", port=8002)
