import datetime
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from app.models.time_slots import TimeSlotIn, TimeSlotOut
import uuid, os, asyncio
import aioboto3
from dotenv import load_dotenv, find_dotenv
from app.database import database
from app.models.user import revoked_tokens
import consul
import socket
from pydantic import BaseModel
from pydantic import Field
from typing import List
from fastapi import Body
from boto3.dynamodb.conditions import Key

load_dotenv(find_dotenv())

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("SLOTS_TABLE", "TimeSlots")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://dynamodb-local:8000")

app = FastAPI(title="TimeSlot Service")

CONSUL_HOST  = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT  = int(os.getenv("CONSUL_PORT", 8500))
SERVICE_NAME = os.getenv("SERVICE_NAME", "slots-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8007))

consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

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

async def get_current_user_email(Authorization: str = Header(...)) -> str:
    from utils import generate_jwt
    try:
        authorization = Authorization[7:].strip()
        payload = generate_jwt.decode_access_token(authorization)
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

async def get_dynamo():
    session = aioboto3.Session()
    async with session.resource("dynamodb", region_name=AWS_REGION, endpoint_url=DYNAMODB_ENDPOINT) as dynamo:
      table = await dynamo.Table("TimeSlots")
      yield table

class TimeSlotBody(BaseModel):
    start_time: str
    end_time: str

@app.post("/slots", response_model=TimeSlotOut)
async def create_slot(
    slot: TimeSlotBody,
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
    if slot.start_time >= slot.end_time:
        raise HTTPException(
            status_code=400,
            detail="The start time must be earlier than the end time."
        )

    resp = await table.query(
        KeyConditionExpression="userEmail = :u",
        ExpressionAttributeValues={":u": user_email}
    )

    for existing_slot in resp.get("Items", []):
        if not (
            slot.end_time <= existing_slot["startTime"] or
            slot.start_time >= existing_slot["endTime"]
        ):
            raise HTTPException(
                status_code=400,
                detail="The provided time slot overlaps with an existing slot."
            )

    slot_id = str(uuid.uuid4())
    item = {
        "userEmail":    user_email,
        "slotId":    slot_id,
        "startTime": slot.start_time,
        "endTime":   slot.end_time,
    }
    await table.put_item(Item=item)
    return {**slot.dict(), "slot_id": slot_id}

@app.get("/slots", response_model=list[TimeSlotOut])
async def list_slots(
    user_email:str,
    table = Depends(get_dynamo),
):
    print(user_email)
    resp = await table.query(
        KeyConditionExpression="userEmail = :u",
        ExpressionAttributeValues={":u": user_email}
    )
    return [
        TimeSlotOut(
            slot_id=i["slotId"],
            start_time=i["startTime"],
            end_time=i["endTime"],
        ) for i in resp.get("Items", [])
    ]
    

@app.delete("/slots/{slot_id}")
async def delete_slot(
    slot_id: str,
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
    await table.delete_item(Key={"userEmail": user_email, "slotId": slot_id})
    return {"deleted": slot_id}


class BookingResponse(BaseModel):
    success: bool


@app.post("/booking", response_model=BookingResponse)
async def create_booking(
    data: dict,
    current_user_email: str = Depends(get_current_user_email),
    reservations_table = Depends(get_dynamo_reservations),
    slot_table = Depends(get_dynamo),
):
    print("Input book", data["slot_id"])

    resp = await slot_table.query(
        KeyConditionExpression="userEmail = :u",
        ExpressionAttributeValues={":u": data["host_email"]}
    )
    slot_found = None
    for i in resp.get("Items", []):
        if i["slotId"] == data["slot_id"]:
            slot_found = i
    
    slot_id = data["slot_id"]
    
    for participant in data["participants"]:
        item={
            "participantEmail": participant,
            "creatorEmail":     current_user_email,
            "slotId":           slot_id,
            "startTime":        slot_found["startTime"],
            "endTime":          slot_found["endTime"],
        }
        await reservations_table.put_item(Item=item)
    
    await reservations_table.put_item(Item={
        "participantEmail": current_user_email,
        "creatorEmail":     current_user_email,
        "slotId":           slot_id,
        "startTime":        slot_found["startTime"],
        "endTime":          slot_found["endTime"],
    })
    
    await slot_table.delete_item(Key={"userEmail": data["host_email"], "slotId": slot_id})

    return BookingResponse(success = True)


@app.get("/booking", response_model=list[BookingOut])
async def list_bookings(
    current_user_email: str = Depends(get_current_user_email),
    reservations_table = Depends(get_dynamo_reservations),
):
    print("Booking request here")
    resp = await reservations_table.query(
        KeyConditionExpression=Key("participantEmail").eq(current_user_email)
    )
    items = resp.get("Items", [])

    slots_map = {}
    for it in items:
        sid = it["slotId"]
        if sid not in slots_map:
            slots_map[sid] = {
                "slot_id":    sid,
                "user_email": it["creatorEmail"],
                "start_time": it["startTime"],
                "end_time":   it["endTime"],
                "participants": set(),
            }
        slots_map[sid]["participants"].add(it["participantEmail"])

    result = []
    for data in slots_map.values():
        result.append(
            BookingOut(
                slot_id=data["slot_id"],
                user_email=data["user_email"],
                start_time=data["start_time"],
                end_time=data["end_time"],
                participants=list(data["participants"]),
            )
        )

    return result