import datetime
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from app.models.time_slots import TimeSlotIn, TimeSlotOut
from pydantic import BaseModel, Field
import uuid, os, asyncio
import aioboto3
from dotenv import load_dotenv, find_dotenv
from app.database import database
from app.models.user import revoked_tokens
from boto3.dynamodb.conditions import Key
from typing import List
from fastapi import Body
import consul
import socket

load_dotenv(find_dotenv())

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("SLOTS_TABLE", "TimeSlots")
RESERVATIONS_TABLE = os.getenv("RESERVATIONS_TABLE", "Reservations")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://dynamodb-local:8000")

app = FastAPI(title="Booking Service")

CONSUL_HOST  = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT  = int(os.getenv("CONSUL_PORT", 8500))
SERVICE_NAME = os.getenv("SERVICE_NAME", "booking-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8005))

consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

@app.on_event("startup")
async def startup():
    svc_addr = socket.gethostname()
    svc_id   = f"{SERVICE_NAME}-{svc_addr}"
    consul_client.agent.service.register(
        name=SERVICE_NAME,
        service_id=svc_id,
        address=svc_addr,
        port=SERVICE_PORT,
        check=consul.Check.http(
            url=f"http://{svc_addr}:{SERVICE_PORT}/health",
            interval="10s",
            timeout="5s"
        )
    )
    app.state.consul_service_id = svc_id

@app.on_event("shutdown")
async def shutdown():
    consul_client.agent.service.deregister(app.state.consul_service_id)

@app.get("/health")
async def health():
    return {"status": "ok"}

class BookingIn(BaseModel):
    timeslot:     TimeSlotIn
    participants: List[str] = Field(..., example=["alice@example.com", "bob@example.com"])

class BookingOut(BaseModel):
    slot_id: str
    user_email: str
    start_time: str
    end_time: str
    participants: List[str]

async def get_dynamo_slots():
    session = aioboto3.Session()
    async with session.resource("dynamodb", region_name=AWS_REGION, endpoint_url=DYNAMODB_ENDPOINT) as dynamo:
      table = await dynamo.Table("TimeSlots")
      yield table

async def get_dynamo_reservations():
    session = aioboto3.Session()
    async with session.resource("dynamodb", region_name=AWS_REGION, endpoint_url=DYNAMODB_ENDPOINT) as dynamo:
      table = await dynamo.Table("Reservations")
      yield table

async def get_current_user_email(Authorization: str = Header(...)) -> str:
    from utils import generate_jwt
    try:
        Authorization = Authorization[7:].strip()
        payload = generate_jwt.decode_access_token(Authorization)
    except Exception:
        raise HTTPException(401, "Invalid token")
    jwt_uuid = payload.get("jit")
    query = revoked_tokens.select().where(revoked_tokens.c.jti == jwt_uuid)
    revoked_token = await database.fetch_one(query)
    if revoked_token:
        raise HTTPException(401, "Token is revoked")
    user_email = payload.get("email")
    if not user_email:
        raise HTTPException(401, "Token has no subject")
    return user_email

