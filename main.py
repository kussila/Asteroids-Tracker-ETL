# main.py
import os
from dotenv import load_dotenv

# Import the core functions from your modularized scripts
# Note: Ensure these files (extract.py, transform.py, load.py) are in the same directory.
from extract import extract_neo_data 
from transform import transform_neo_data
# We import the load function and the helper functions (engine creation, verification) from load.py
from load import load_neo_data, create_db_engine, verify_data_count 

load_dotenv()

def run_etl_pipeline():
    """
    The main orchestration function for the NEO Asteroids ETL pipeline.
    Runs Extract -> Transform -> Load sequentially.
    """
    print("=" * 50)
    print("✨ Starting Asteroids Tracker ETL Pipeline ✨")
    print("=" * 50)

    # 1. Configuration (Getting dates from .env)
    # The START_DATE and END_DATE are read directly from the .env file
    start_date = os.getenv("START_DATE")
    end_date = os.getenv("END_DATE")
    
    if not start_date or not end_date:
        print("🔴 ERROR: START_DATE or END_DATE not found in .env. Exiting.")
        return

    # --- 2. EXTRACT (E) ---
    # The extract function fetches data and returns the raw JSON dictionary.
    raw_data = extract_neo_data(start_date, end_date)
    if raw_data is None:
        print("🔴 Pipeline failed during Extraction. Exiting.")
        return

    # --- 3. TRANSFORM (T) ---
    # The transform function accepts the raw dictionary and returns a clean DataFrame.
    clean_df = transform_neo_data(raw_data)
    if clean_df.empty:
        print("🔴 Pipeline failed during Transformation. Exiting.")
        return
        
    # --- 4. LOAD (L) ---
    # The load function accepts the clean DataFrame and inserts it into the database.
    load_neo_data(clean_df)
    
    # --- 5. VERIFY ---
    # We verify the load was successful by checking the row count in the database.
    try:
        engine = create_db_engine()
        verify_data_count(engine)
    except Exception:
        # The verify function itself handles connection errors and prints messages.
        pass 

    print("=" * 50)
    print("🎉 ETL Pipeline Completed Successfully! 🎉")
    print("=" * 50)


if __name__ == '__main__':
    run_etl_pipeline()