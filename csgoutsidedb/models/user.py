from pydantic import BaseModel


class User(BaseModel):
    name: str
    team: str
    health: str
    shirt: str
    killedby: str
    kills: str

class Hardware(BaseModel):
    message: str

class Shot(BaseModel):
    playerID: str
    playerShot: str