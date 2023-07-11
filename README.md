# CSGOutside
## L2A-08-bitsonebyte
![plot](./my-app/public/CSGOutside-logo.png) <br>

## Project Description
CSGOutside is a real life tactical shooter game based off the game CSGO. Players play this game using their phones<br>
How it works<br>
-Players are divided into two teams - Planters or Defusers.<br>
-Planters must attempt to activate the bomb while Defusers attempt to deactivate it.<br>
-Players on both teams try to achieve their objective while using their phones to eliminate the other team.<br>

## Cloud Component Server - Srijan
Docker Container Setup<br>
`docker run -d -p 27018:27017 --name csgoutside-db -v csgoutside-data:/data/db mongo:latest` <br>
PYTHON VIRTUAL ENVIRONMENT SETUP <br>
`python -m venv .venv` <br>
`.venv/Scripts/activate` (Mac: `source .venv/bin/activate` ) <br>
`pip install -r requirements.txt` <br>
The Server runs from csgoutsidedb/index.py by running `python index.py`<br>
NOTE: The host IP for the server app has to be the IP of the computer <br>

## User Component - Marc
The App runs from the my-app/ by running `npm start` <br>
The frontend app files are in my-app. <br>
NOTE: The IP adress for the sockets and POST/GET requests has to be same as that of server <br>

## Cloud Component ML Model - Sarthak
The ML Model is in model and can be deployed by running `python webapp.py` <br>
Note: All directory names must be changed as they point to the local dev computer. Also, model weights can be supplied on request if required (since its a huge folder and is unfeasible to push)<br>

## Hardware Component - Peter
Hardware component i.e. De1-Soc and the rest of the physical components was done by Peter<br>
To run: Load sof in quarutus. <br>
Set up lua: via the explorer and set ip address<br>
Load code: through nios explorer<br>
