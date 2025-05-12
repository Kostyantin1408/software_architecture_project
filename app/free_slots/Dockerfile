FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "app.free_slots.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]