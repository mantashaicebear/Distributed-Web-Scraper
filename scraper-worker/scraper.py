import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import os
from datetime import datetime

def scrape_url(url):
    print(f"[🌐] Visiting: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"[❌] Failed to reach {url} - Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        paragraphs = soup.find_all("p")
        text_content = " ".join([p.get_text() for p in paragraphs])

        result = {
            "url": url,
            "title": title,
            "content": text_content[:2000],
            "scraped_at": datetime.now().isoformat()
        }

        print(f"[✅] Successfully scraped: {title}")
        return result

    except Exception as e:
        print(f"[❌] Error scraping {url}: {e}")
        return None


def save_to_db(data):
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "scraper_db"),
            user=os.getenv("POSTGRES_USER", "scraper_user"),
            password=os.getenv("POSTGRES_PASSWORD", "scraper_password")
        )
        cursor = conn.cursor()

        # Create table if it doesn't exist yet
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_results (
                id SERIAL PRIMARY KEY,
                url TEXT,
                title TEXT,
                content TEXT,
                scraped_at TIMESTAMP
            )
        """)

        # Insert the scraped data
        cursor.execute("""
            INSERT INTO scraped_results (url, title, content, scraped_at)
            VALUES (%s, %s, %s, %s)
        """, (data["url"], data["title"], data["content"], data["scraped_at"]))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[💾] Data saved to PostgreSQL database!")

    except Exception as e:
        print(f"[❌] Database error: {e}")