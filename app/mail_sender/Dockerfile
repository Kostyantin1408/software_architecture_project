FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY app/mail_sender/main.py /app/main.py
COPY app/models       /app/models
ENV PYTHONPATH=/app

CMD ["python", "main.py"]
