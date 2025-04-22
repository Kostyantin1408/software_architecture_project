import os
import json
import pika
from pika.exceptions import AMQPConnectionError
import time
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

def get_channel():
    while True:
        try:
            conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
            ch = conn.channel()
            return ch, conn
        except AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 5s…")
            time.sleep(5)

def publish_user_registered(user: dict):
    ch, conn = get_channel()
    ch.exchange_declare(
        exchange    = "events",
        exchange_type = "topic",
        durable     = True
    )
    payload = json.dumps({"user": user})
    ch.basic_publish(
        exchange    = "events",
        routing_key = "user.registered",
        body        = payload,
        properties  = pika.BasicProperties(content_type="application/json",
                                           delivery_mode=2)
    )
    print("✅ Published user.registered:", user["email"])
    conn.close()
