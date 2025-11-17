import os
import requests
from dotenv import load_dotenv
from datetime import date, timedelta
import json 

# Load environment variables for local testing
load_dotenv()

# --- Core Pipeline Function ---

def extract_neo_data(start_date: str, end_date: str) -> dict | None:
    """
    Fetches Near-Earth Object data from the NASA NeoWs API using 
    the specified date range. Returns the raw JSON data.
    """
    API_KEY = os.getenv("NASA_API_KEY")
    API_URL = os.getenv("NEO_FEED_URL")
    
    if not API_KEY or not API_URL:
        print("🔴 ERROR: NASA_API_KEY or NEO_FEED_URL not found.")
        return None

    # API Request Parameters
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'api_key': API_KEY
    }

    print(f"🌍 Starting data extraction for {start_date} to {end_date}...")

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        print("✅ Extraction successful.")
        
        # Save raw JSON temporarily for next step (Transform)
        raw_data_path = 'data/raw_neo_data.json'
        with open(raw_data_path, 'w') as f:
             json.dump(data, f, indent=4)
        print(f"💾 Raw JSON saved to {raw_data_path}.")
        
        # KEY CHANGE: Return the data for the next stage (Transform)
        return data

    except requests.exceptions.RequestException as err:
        print(f"🔴 ERROR during API request: {err}")
        
    return None

# ------------------------------------------------
# --- Helper/Test Functions (for running extract.py directly) ---

def get_date_range(days=7):
    """
    Calculates the start and end dates (YYYY-MM-DD format).
    """
    # NOTE: This is only used when running this file directly for testing.
    start_date = date.today()
    end_date = start_date + timedelta(days=days - 1)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


if __name__ == '__main__':
    # This block runs only when you execute 'python extract.py' directly
    print("\n--- Running extract.py Standalone Test ---")
    
    start_date, end_date = get_date_range(days=7)
    
    neo_data = extract_neo_data(start_date, end_date)
    
    if neo_data:
        count = neo_data.get('element_count', 0)
        print(f"Summary: Found **{count}** NEOs in the 7-day period.")
    print("------------------------------------------\n")