import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import time

load_dotenv()

# --- Helper Function: Database Connection ---

def create_db_engine():
    """Constructs the SQLAlchemy engine using environment variables, with retries."""
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")

    # PostgreSQL connection string format: postgresql://user:password@host:port/database_name
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    print(f"Connecting to database at {DB_HOST}:{DB_PORT}...")

    # The PostgreSQL container might take a second to start, so we retry connection
    max_retries = 5
    for attempt in range(max_retries):
        try:
            engine = create_engine(db_url)
            # Test connection immediately
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection successful.")
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"🔴 Connection failed (Attempt {attempt + 1}/{max_retries}). Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"🔴 Failed to connect to database after {max_retries} attempts: {e}")
                # Re-raise the exception so the caller knows the pipeline failed
                raise 

# --- Verification Function ---

def verify_data_count(engine, table_name='asteroids'):
    """Verifies the number of rows in the loaded table."""
    try:
        with engine.connect() as conn:
            # Execute a simple SQL COUNT query
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"\n✨ SUCCESS! Found {result} records in the '{table_name}' table.")
            return True
    except Exception as e:
        print(f"\n🔴 Verification failed. Table might not exist yet: {e}")
        return False

# --- Core Pipeline Function ---

def load_neo_data(df: pd.DataFrame, table_name='asteroids'):
    """
    Loads a Pandas DataFrame into the specified SQL table.
    NOTE: Renamed from load_data_to_sql for main.py compatibility.
    """
    if df.empty:
        print("🟡 DataFrame is empty. Skipping load step.")
        return

    try:
        # Create engine, handling connection retries
        engine = create_db_engine()
    except Exception:
        return # Exit if engine creation failed

    print(f"Attempting to load {len(df)} records into table '{table_name}'...")
    
    try:
        # Load the DataFrame to PostgreSQL
        df.to_sql(
            table_name,
            engine,
            if_exists='replace', # Creates a new table every time
            index=False,
            method='multi' # Use the faster multi-row insert method
        )
        print(f"✅ Data successfully loaded into the '{table_name}' table.")
    
    except Exception as e:
        print(f"🔴 ERROR during data load: {e}")


if __name__ == '__main__':
    # --- Running load.py Standalone Test ---
    print("\n--- Running load.py Standalone Test ---")
    
    clean_data_path = 'data/clean_neo_data.csv'
    if os.path.exists(clean_data_path):
        try:
            # Load the clean CSV created by the transform script
            test_df = pd.read_csv(clean_data_path)
            
            # 1. Run the core load function
            load_neo_data(test_df)
            
            # 2. Run the verification check
            engine = create_db_engine()
            verify_data_count(engine)

        except Exception as e:
            print(f"🔴 Test failed: {e}")
            
    else:
        print("🔴 Cannot test load.py directly: clean_neo_data.csv not found. Run extract.py and transform.py first.")
    print("------------------------------------------\n")