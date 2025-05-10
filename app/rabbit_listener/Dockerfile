FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY app/rabbit_listener    /app/rabbit_listener
COPY app/models             /app/models
COPY app/slots              /app/slots

ENV PYTHONPATH=/app

CMD ["python", "rabbit_listener/publisher.py"]
