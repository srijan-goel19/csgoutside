def userEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": str(item["name"]),
        "team": str(item["team"]),
        "health": str(item["health"]),
        # "shirt": str(item["shirt"]),
        "killedby": str(item["killedby"]),
        "kills": str(item["kills"])
    }


def usersEntity(entity) -> list:
    return [userEntity(item) for item in entity]
