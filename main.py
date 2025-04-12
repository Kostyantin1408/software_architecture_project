"""
Basic authentication flow on Fast API.
"""
from fastapi import FastAPI, HTTPException, Body
from starlette.responses import JSONResponse
from app.database import database, engine, metadata
from models.user import users
from utils import generate_jwt


metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/login")
async def login_user(user: dict = Body(...)):
    """
    Endpoint handler for usage auth.
    Expects <password> and <email> in body.
    """
    if "email" not in user or "password" not in user:
        raise HTTPException(status_code=405, detail="Missing name or email in request body")

    email = user["email"]
    password = user["password"]

    query = users.select().where(users.c.email == email and users.c.password == password)
    existing_user = await database.fetch_one(query)
    if not existing_user:
        raise HTTPException(status_code=400, detail="No such user! Check your email and password!")


    token = generate_jwt.create_access_token({
            "sub": str(existing_user["id"]),
            "name": existing_user["name"],
            "email": existing_user["email"]
        })

    return {"access_token": token, "user": existing_user}


@app.post("/register")
async def register_user(user: dict = Body(...)):
    """
    Endpoint handler for user registration.
    Expects <name>, <password> and <email> in body.
    """
    if "name" not in user or "email" not in user or "password" not in user:
        raise HTTPException(status_code=405, detail="Invalid number of arguments!")

    name = user["name"]
    email = user["email"]
    password = user["password"]
    query = users.select().where(users.c.email == email)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=403, detail="Email already registered")

    insert_query = users.insert().values(name=name, email=email, password=password)
    user_id = await database.execute(insert_query)

    query = users.select().where(users.c.id == user_id)
    new_user = await database.fetch_one(query)
    token = generate_jwt.create_access_token({
        "sub": str(new_user["id"]),
        "name": new_user["name"],
        "email": new_user["email"],
    })

    return {"access_token": token, "user": new_user}
