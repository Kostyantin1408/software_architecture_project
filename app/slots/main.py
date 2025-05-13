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
