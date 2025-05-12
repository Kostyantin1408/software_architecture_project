import json
import os
import pika
from pika.exceptions import AMQPConnectionError
import time
import boto3

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

while True:
    try:
        conn = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
        break
    except AMQPConnectionError:
        print("RabbitMQ not ready, retrying in 5s…")
        time.sleep(5)

ch = conn.channel()
ch.exchange_declare(exchange="events", exchange_type="topic", durable=True)

ch.queue_declare(queue="messages", durable=True)
ch.queue_bind(
  exchange="events",
  queue="messages",
  routing_key="user.registered"
)

ses = boto3.client("ses", region_name=os.getenv("AWS_REGION", "eu-west-1"))

def send_email(to: str, subject: str, body: str):
    print("GOING TO SEND EMAIL TO: ", to)
    ses.send_email(
      Source = "kostyantin1408@gmail.com",
      Destination = {"ToAddresses": [to]},
      Message     = {
        "Subject": {"Data": subject},
        "Body":    {"Text": {"Data": body}}
      }
    )

def on_message(ch, method, props, body):
    print("RECEIVED MESSAGE")
    evt = json.loads(body)
    rk  = method.routing_key
    print(rk)
    try:
        if rk == "user.registered":
            handle_registration(evt)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("❌ NotificationService error:", e)


def handle_registration(evt):
    user = evt["user"]
    send_email(
        to=user["email"],
        subject="Welcome to Timely!",
        body=f"Hi {user['name']}, thanks for signing up!"
    )

if __name__ == "__main__":
    print("🟢 Mail‑sender connected to RabbitMQ, bound to queue 'messages'")
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue="messages", on_message_callback=on_message)
    ch.start_consuming()
