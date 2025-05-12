import datetime
from fastapi import FastAPI, Header, HTTPException, Depends, Query
from app.models.time_slots import TimeSlotIn, TimeSlotOut
import uuid, os, asyncio
import aioboto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("SLOTS_TABLE", "TimeSlots")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", "http://dynamodb-local:8000")

app = FastAPI(title="TimeSlot Service")


def get_current_user_email(auth_token: str = Header(...)) -> str:
    from utils import generate_jwt
    try:
        payload = generate_jwt.decode_access_token(auth_token)
    except Exception:
        raise HTTPException(401, "Invalid token")
    user_email = payload.get("email")
    if not user_email:
        raise HTTPException(401, "Token has no subject")
    return user_email

async def get_dynamo():
    session = aioboto3.Session()
    async with session.resource("dynamodb", region_name=AWS_REGION, endpoint_url=DYNAMODB_ENDPOINT) as dynamo:
      table = await dynamo.Table("TimeSlots")
      yield table


@app.get("/free-slots", response_model=list[TimeSlotOut])
async def get_free_slots(
    time_interval: TimeSlotIn,
    user_email: str = Depends(get_current_user_email),
    table = Depends(get_dynamo),
):
    req_start = time_interval.start_time
    req_end = time_interval.end_time

    resp = await table.query(
        KeyConditionExpression="userEmail = :u",
        ExpressionAttributeValues={":u": user_email}
    )

    booked_slots = [
        TimeSlotIn(start_time=i["startTime"], end_time=i["endTime"])
        for i in resp.get("Items", [])
        if i["endTime"] > req_start and i["startTime"] < req_end
    ]
    booked_slots.sort(key=lambda x: x.start_time)

    free_slots: list[TimeSlotOut] = []

    if not booked_slots:
        free_slots.append(
            TimeSlotOut(
                slot_id=str(uuid.uuid4()),
                start_time=req_start,
                end_time=req_end,
            )
        )
        return free_slots

    first = booked_slots[0]
    if req_start < first.start_time:
        free_slots.append(
            TimeSlotOut(
                slot_id=str(uuid.uuid4()),
                start_time=req_start,
                end_time=first.start_time,
            )
        )

    for prev, curr in zip(booked_slots, booked_slots[1:]):
        if prev.end_time < curr.start_time:
            free_slots.append(
                TimeSlotOut(
                    slot_id=str(uuid.uuid4()),
                    start_time=prev.end_time,
                    end_time=curr.start_time,
                )
            )

    last = booked_slots[-1]
    if last.end_time < req_end:
        free_slots.append(
            TimeSlotOut(
                slot_id=str(uuid.uuid4()),
                start_time=last.end_time,
                end_time=req_end,
            )
        )

    return free_slots