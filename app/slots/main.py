from fastapi import FastAPI, Header, HTTPException, Depends
from app.models.time_slots import TimeSlotIn, TimeSlotOut
import uuid, os, asyncio
import aioboto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("SLOTS_TABLE", "TimeSlots")

app = FastAPI(title="TimeSlot Service")


def get_current_user(auth_token: str = Header(...)) -> str:
    from utils import generate_jwt
    try:
        payload = generate_jwt.decode_access_token(auth_token)
    except Exception:
        raise HTTPException(401, "Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Token has no subject")
    return user_id

async def get_dynamo():
    session = aioboto3.Session()
    async with session.resource("dynamodb", region_name=AWS_REGION, endpoint_url=os.getenv("DYNAMODB_ENDPOINT")) as dynamo:
      table = await dynamo.Table(TABLE_NAME)
      yield table

@app.post("/slots", response_model=TimeSlotOut)
async def create_slot(
    slot: TimeSlotIn,
    user_id: str = Depends(get_current_user),
    table = Depends(get_dynamo),
):
    slot_id = str(uuid.uuid4())
    item = {
        "userId":    user_id,
        "slotId":    slot_id,
        "startTime": slot.start_time,
        "endTime":   slot.end_time,
    }
    await table.put_item(Item=item)
    return {**slot.dict(), "slot_id": slot_id}

@app.get("/slots", response_model=list[TimeSlotOut])
async def list_slots(
    user_id: str = Depends(get_current_user),
    table = Depends(get_dynamo),
):
    resp = await table.query(
        KeyConditionExpression="userId = :u",
        ExpressionAttributeValues={":u": user_id}
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
    user_id: str = Depends(get_current_user),
    table = Depends(get_dynamo),
):
    await table.delete_item(Key={"userId": user_id, "slotId": slot_id})
    return {"deleted": slot_id}
