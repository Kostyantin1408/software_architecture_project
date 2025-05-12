"""
Basic authentication flow on Fast API.
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, Body, Header
from app.models.user import users, revoked_tokens
from app.database import database, engine, metadata
from utils import generate_jwt
from fastapi.middleware.cors import CORSMiddleware
from app.rabbit_listener.publisher import publish_user_registered
import uuid

metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow all origins
    allow_credentials=True,  # ⚠️ Cannot be used with "*" in some cases (see below)
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """
    Startup function for connecting to db.
    """
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """
    Shutdown function for reconnecting from db.
    """
    await database.disconnect()

@app.get("/some_info")
async def some_info(auth_token: Optional[str] = Header(None)):
    """
    Example handler for route, that requires user authorization and takes auth-token in header.
    If header is invalid or missing, doesn't return required info.
    """
    if not auth_token:
        raise HTTPException(status_code=403, detail="Unauthorized")
    desoded_token = generate_jwt.decode_access_token(auth_token)
    user_id = desoded_token.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=403,
            detail="Invalid token: subject missing"
    )

    query = users.select().where(users.c.id == int(user_id))
    current_user = await database.fetch_one(query)
    if not current_user:
        raise HTTPException(
            status_code=403,
            detail="User not found"
    )

    return "Hello world!"



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
    jwt_uuid = str(uuid.uuid4())

    query = users.select().where(
        (users.c.email == email) &
        (users.c.password == password)
    )
    existing_user = await database.fetch_one(query)
    if not existing_user:
        raise HTTPException(status_code=400, detail="No such user! Check your email and password!")

    token = generate_jwt.create_access_token({
            "sub": str(existing_user["id"]),
            "name": existing_user["name"],
            "email": existing_user["email"],
            "jit": jwt_uuid
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
    jwt_uuid = str(uuid.uuid4())
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
        "jit": jwt_uuid
    })
    publish_user_registered({
      "id":    new_user["id"],
      "email": new_user["email"],
      "name":  new_user["name"]
    })

    return {"access_token": token, "user": new_user}

@app.post("/logout")
async def logout_user(auth_token: str = Header(...)):
    """
    Endpoint handler for user logout.
    Expects <email> in body.
    """
    payload = generate_jwt.decode_access_token(auth_token)
    jwt_uuid = payload.get("jit")
    query = revoked_tokens.insert().values(jti=jwt_uuid)
    await database.execute(query)
