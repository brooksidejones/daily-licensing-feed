import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 1. Configuration & Webhook Setup
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

yesterday = datetime.now() - timedelta(days=1)
search_date = yesterday.strftime("%m/%d/%Y")

print(f"Starting scrape for new business filings on: {search_date}")

# 2. Alabama SOS Business Entity Search
url = "https://arc-sos.state.al.us/CGI/CORPNAME.MBR/INPUT"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

payload = {
    "searchType": "entityName",
    "entityName": "%",
    "type": "LLC",
    "county": "Jefferson",
    "status": "Active"
}

def scrape_recent_filings():
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')[1:] 
        
        new_businesses = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                entity_id = cols[0].text.strip()
                entity_name = cols[1].text.strip()
                entity_type = cols[2].text.strip()
                status = cols[3].text.strip()
                
                business_data = {
                    "scrape_date": datetime.now().isoformat(),
                    "entity_id": entity_id,
                    "entity_name": entity_name,
                    "entity_type": entity_type,
                    "status": status,
                    "county": "Jefferson",
                    "opportunity_flag": "New Commercial Formation"
                }
                new_businesses.append(business_data)

        return new_businesses

    except Exception as e:
        print(f"Error scraping AL SOS: {e}")
        return []

def send_to_make(data):
    if not data:
        print("No new records found today. Exiting.")
        return
        
    if not MAKE_WEBHOOK_URL:
        print("ERROR: MAKE_WEBHOOK_URL environment variable is not set.")
        return

    print(f"Sending {len(data)} records to Make.com pipeline...")
    
    response = requests.post(
        MAKE_WEBHOOK_URL, 
        json={"filings": data},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        print("Successfully delivered to Make.com!")
    else:
        print(f"Delivery failed with status code: {response.status_code}")

if __name__ == "__main__":
    records = scrape_recent_filings()
    send_to_make(records)
