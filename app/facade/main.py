import os, random
import consul
import httpx
from fastapi import FastAPI, HTTPException, Header

app = FastAPI(title="API Gateway / Façade")

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
    url = pick("auth-service") + "/verify"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers={"Authorization": f"Bearer {token}"})
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


@app.post("/book")
async def book(booking: dict, authorization: str = Header(...)):
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("booking-service") + "/booking"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=booking, headers={"Authorization": authorization})
        return r.json()

@app.get("/slots")
async def slots(service_type: str, date: str, authorization: str = Header(...)):
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("slots-service") + "/slots"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params={"service_type": service_type, "date": date},
                              headers={"Authorization": authorization})
        return r.json()

@app.get("/bookings/{user_id}")
async def user_bookings(user_id: str, authorization: str = Header(...)):
    if not await verify(authorization):
        raise HTTPException(401, "Invalid token")
    url = pick("booking-service") + f"/bookings/{user_id}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers={"Authorization": authorization})
        return r.json()
