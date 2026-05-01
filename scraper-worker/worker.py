import os
import json
import time
from kafka import KafkaConsumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:29092")

print("Starting Scraper Worker...")
print("Attempting to connect to Kafka...")

consumer = None
attempt = 1

# --- THE PERMANENT FIX: Infinite Retry Loop ---
while True:
    try:
        consumer = KafkaConsumer(
            'urls-to-scrape',
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='scraper-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print(f"✅ Worker successfully connected to Kafka at {KAFKA_BROKER} on attempt {attempt}")
        break # Break out of the infinite loop ONLY when successful
    except Exception as e:
        print(f"⏳ Kafka not ready yet. Retrying in 5 seconds... (Attempt {attempt} - {e})")
        time.sleep(5)
        attempt += 1

# -----------------------------------------------

print("🎧 Listening for URLs on queue 'urls-to-scrape'...")

try:
    for message in consumer:
        data = message.value
        url = data.get('url')
        print(f"\n[+] Picked up task from queue: {url}")
        print("[+] Pretending to scrape...")
        time.sleep(2) # Simulate the time it takes to scrape
        print("[+] Scrape complete! Ready for next task.")

except Exception as e:
    print(f"Worker crashed during scraping: {e}")