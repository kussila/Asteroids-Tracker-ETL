import pandas as pd
import json
import os

# Define constants for file paths
CLEAN_DATA_PATH = 'data/clean_neo_data.csv'
RAW_DATA_PATH = 'data/raw_neo_data.json'

# --- Core Pipeline Function ---

def transform_neo_data(raw_json_data: dict) -> pd.DataFrame:
    """
    Transforms raw NASA NEO JSON data (dictionary) into a clean Pandas DataFrame 
    by flattening the nested structure and cleaning units.
    """
    if not raw_json_data:
        print("🟡 No raw data provided for transformation. Returning empty DataFrame.")
        return pd.DataFrame()

    print("✅ Starting data transformation...")

    # The data is nested under a 'near_earth_objects' dictionary, keyed by date
    neo_by_date = raw_json_data.get('near_earth_objects', {})
    
    # This list will hold all our flattened records (one dict per asteroid)
    flattened_records = []

    # Iterate through the nested structure
    for date_key, neos_on_date in neo_by_date.items():
        for neo in neos_on_date:
            
            # NASA API structure guarantees at least one close approach
            # We use the first (index 0) close approach for the main record
            approach_data = neo['close_approach_data'][0]
            
            # Extract and structure the required fields
            record = {
                # CORE IDENTIFIERS
                'id': neo['id'],
                'name': neo['name'],
                'is_potentially_hazardous': neo['is_potentially_hazardous_asteroid'],
                'close_approach_date': date_key, 
                
                # DIAMETER (Extracting kilometers values)
                'diameter_min_km': neo['estimated_diameter']['kilometers']['estimated_diameter_min'],
                'diameter_max_km': neo['estimated_diameter']['kilometers']['estimated_diameter_max'],
                
                # VELOCITY (Extracting km/s value)
                'relative_velocity_km_s': float(approach_data['relative_velocity']['kilometers_per_second']),
                
                # DISTANCE (Extracting km value)
                'miss_distance_km': float(approach_data['miss_distance']['kilometers']),
            }
            
            flattened_records.append(record)

    # Create DataFrame
    df = pd.DataFrame(flattened_records)
    
    # Optional: save the clean DataFrame to a CSV for manual inspection
    df.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"💾 Clean DataFrame saved to {CLEAN_DATA_PATH}.")

    print(f"✅ Transformation successful. DataFrame shape: {df.shape}")
    
    # Return the clean DataFrame for the Load step
    return df

# ------------------------------------------------
# --- Standalone Test Block ---

if __name__ == '__main__':
    # This block allows you to run 'python transform.py' directly for testing
    print("\n--- Running transform.py Standalone Test ---")
    
    if os.path.exists(RAW_DATA_PATH):
        try:
            # 1. Load the raw JSON data from file (only in standalone mode)
            with open(RAW_DATA_PATH, 'r') as f:
                raw_data = json.load(f)
                
            # 2. Run the core transformation function
            df_clean = transform_neo_data(raw_data)
            
            if not df_clean.empty:
                 print(f"Preview:\n{df_clean.head(2).to_markdown(index=False)}")
        except Exception as e:
            print(f"🔴 ERROR loading raw JSON for test: {e}")
    else:
        print(f"🔴 Cannot run transform.py standalone: {RAW_DATA_PATH} not found. Run extract.py first.")
    print("------------------------------------------\n")