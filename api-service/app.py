from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os
import time

app = FastAPI(title="Distributed Scraper API")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:29092")

# --- THE FIX: Infinite Retry Loop for API ---
producer = None
print("Attempting to connect to Kafka...")
attempt = 1

while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"✅ Successfully connected to Kafka at {KAFKA_BROKER} on attempt {attempt}")
        break # Exit the loop if connection is successful
    except Exception as e:
        print(f"⏳ Kafka not ready yet. Retrying in 5 seconds... (Attempt {attempt} - {e})")
        time.sleep(5)
        attempt += 1

# ---------------------------------

class URLRequest(BaseModel):
    url: str

@app.post("/scrape")
async def submit_url(request: URLRequest):
    if not producer:
        raise HTTPException(status_code=503, detail="API is not connected to Kafka queue")
        
    try:
        producer.send('urls-to-scrape', {'url': request.url})
        producer.flush()
        return {"status": "success", "message": f"Added {request.url} to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))