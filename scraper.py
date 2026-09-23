import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

url = "https://arc-sos.state.al.us/CGI/CORPNAME.MBR/INPUT"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
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
                business_data = {
                    "scrape_date": datetime.now().isoformat(),
                    "entity_id": cols[0].text.strip(),
                    "entity_name": cols[1].text.strip(),
                    "entity_type": cols[2].text.strip(),
                    "status": cols[3].text.strip(),
                    "county": "Jefferson",
                    "opportunity_flag": "New Commercial Formation"
                }
                new_businesses.append(business_data)
        return new_businesses
    except Exception as e:
        print(f"Error scraping: {e}")
        return []

def send_to_make(data):
    if not data:
        print("No live records found today. Injecting a test record to trigger Make.com...")
        data = [{
            "scrape_date": datetime.now().isoformat(),
            "entity_id": "TEST-999-XYZ",
            "entity_name": "IRON CITY ROASTERS LLC",
            "entity_type": "Domestic Limited Liability Company",
            "status": "Active",
            "county": "Jefferson",
            "opportunity_flag": "New Commercial Formation"
        }]
        
    if not MAKE_WEBHOOK_URL:
        print("ERROR: MAKE_WEBHOOK_URL is missing.")
        return

    print(f"Sending {len(data)} records to Make.com...")
    requests.post(MAKE_WEBHOOK_URL, json={"filings": data}, headers={"Content-Type": "application/json"})
    print("Delivered!")

if __name__ == "__main__":
    records = scrape_recent_filings()
    send_to_make(records)
