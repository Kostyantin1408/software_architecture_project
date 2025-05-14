import os, random
import consul
import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
app = FastAPI(title="API Gateway / Façade")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

def pick(service_name: str) -> str:
    _, nodes = consul_client.health.service(service_name, passing=True)
    if not nodes:
        raise HTTPException(503, f"No healthy `{service_name}` instances")
    svc = random.choice(nodes)["Service"]
    return f"http://{svc['Address']}:{svc['Port']}"

async def verify(token: str) -> bool:
    print("Token ", token)
    url = pick("auth-service") + "/verify"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={"auth-token": f"{token}"})
        print("Response ", r)
        return r.status_code == 200

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/login")
async def login(payload: dict):
    url = pick("auth-service") + "/login"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json()

@app.post("/register")
async def register(payload: dict):
    url = pick("auth-service") + "/register"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json()

@app.post("/booking")
async def book(booking: dict, authorization: str = Header(...)):
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("slots-service") + "/booking"
    # print("Book boo", booking)
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=booking, headers={"Authorization": authorization})
        return r.json()
    
@app.get("/bookings")
async def user_bookings(authorization: str = Header(...)):
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("slots-service") + "/booking"
    print("Found uri slots")

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={"Authorization": authorization})
        r.raise_for_status()
        return r.json()

@app.get("/slots")
async def slots(email:str, authorization: str = Header(...)):
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("slots-service") + "/slots"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params={"user_email": email},
                              headers={"Authorization": authorization})
        return r.json()
    
class TimeSlotIn(BaseModel):
    start_time: str
    end_time: str

@app.post("/slots")
async def slots_pos(
    slot: dict,
    authorization: str = Header(...)
):
    print("slots recieved", slot)
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("slots-service") + "/slots"
    async with httpx.AsyncClient() as client:
        print("Sended slots")
        r = await client.post(url, json=slot,
                              headers={"Authorization": authorization})
        return r.json()
    

@app.delete("/slots/{slot_id}")
async def delete_slot(
    slot_id: str,
    authorization: str = Header(...)
):  
    url = pick("slots-service") + f"/slots/{slot_id}"
    async with httpx.AsyncClient() as client:
        r = await client.delete(url,
                              headers={"Authorization": authorization})
        return r.json()
