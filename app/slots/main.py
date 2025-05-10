import datetime
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from app.models.time_slots import TimeSlotIn, TimeSlotOut
import uuid, os, asyncio
import aioboto3
from dotenv import load_dotenv, find_dotenv
from app.database import database
from app.models.user import revoked_tokens

load_dotenv(find_dotenv())

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("SLOTS_TABLE", "TimeSlots")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://dynamodb-local:8000")

app = FastAPI(title="TimeSlot Service")


async def get_current_user_email(auth_token: str = Header(...)) -> str:
    from utils import generate_jwt
    try:
        payload = generate_jwt.decode_access_token(auth_token)
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

@app.post("/slots", response_model=TimeSlotOut)
async def create_slot(
    slot: TimeSlotIn,
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
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
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
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
    
@app.get("/slots/free", response_model=list[TimeSlotOut])
async def get_free_slots(
    time_interval: TimeSlotIn,
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
    start_time = time_interval.start_time
    end_time = time_interval.end_time
    
    resp = await table.query(
        KeyConditionExpression="userEmail = :u",
        ExpressionAttributeValues={":u": user_email}
    )
    
    booked_slots = [
        TimeSlotIn(
            start_time=i["startTime"],
            end_time=i["endTime"],
        ) for i in resp.get("Items", [])
    ]

    print("booked_slots", booked_slots)
    
    booked_slots = sorted(booked_slots, key=lambda x: x.start_time)
    booked_slots = list(filter(lambda x: x.end_time < end_time and x.start_time > start_time, booked_slots))
    free_slots: list[TimeSlotOut] = []
    for i in range(len(booked_slots) - 2):
        free_slots.append(
            TimeSlotOut(
                slot_id=str(uuid.uuid4()),
                start_time = booked_slots[i].end_time,
                end_time = booked_slots[i + 1].start_time,
            )
        )
    
    return free_slots
    

@app.delete("/slots/{slot_id}")
async def delete_slot(
    slot_id: str,
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
    await table.delete_item(Key={"userEmail": user_email, "slotId": slot_id})
    return {"deleted": slot_id}
