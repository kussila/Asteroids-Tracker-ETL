# app.py
import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables (for use outside the Docker environment if needed, and for clarity)
load_dotenv()

# --- Helper Function to Connect to Database ---

def get_db_engine():
    """Constructs the SQLAlchemy engine using environment variables."""
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT")
    
    # Use the Docker service name 'postgres-db' for the host
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(db_url)

# --- Core Data Fetching Function (Cached for performance) ---

@st.cache_data(ttl=600) # Cache data for 10 minutes to reduce database load
def fetch_asteroid_data():
    """Fetches all data from the 'asteroids' table."""
    try:
        engine = get_db_engine()
        
        # Use a SQL query to select all columns
        query = text("SELECT * FROM asteroids ORDER BY close_approach_date DESC;")
        
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            
        return df, None # Return DataFrame and no error
    
    except Exception as e:
        error_message = f"🔴 Error fetching data from database. Has the ETL run? Details: {e}"
        return pd.DataFrame(), error_message # Return empty DataFrame and error

# --- Streamlit Frontend Layout ---

def main():
    st.set_page_config(layout="wide")
    st.title("🛰️ Near-Earth Asteroid Tracker")
    st.markdown("---")

    # Fetch data
    df_asteroids, error = fetch_asteroid_data()

    if error:
        st.error(error)
        st.info("The database may not be running or the 'asteroids' table is empty. Please run `docker-compose up` to ensure the ETL pipeline loads the data first.")
        return

    st.subheader(f"Data from NASA NEOWs API ({len(df_asteroids)} Close Approaches)")

    # 1. Key Metrics (Optional, but useful)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hazardous_count = df_asteroids['is_potentially_hazardous'].sum()
        st.metric(label="Potentially Hazardous NEOs", value=hazardous_count)

    with col2:
        max_diameter = df_asteroids['diameter_max_km'].max()
        st.metric(label="Largest Max Diameter (km)", value=f"{max_diameter:.2f}")
        
    with col3:
        min_distance = df_asteroids['miss_distance_km'].min()
        st.metric(label="Closest Approach Distance (km)", value=f"{min_distance:,.0f}")
        
    st.markdown("---")

    # 2. Main Data View (Interactive Table)
    st.subheader("Raw Data Table")
    
    # Hide the index column and format numbers nicely for display
    display_df = df_asteroids.drop(columns=['index'], errors='ignore')
    
    # Rename columns for readability
    display_df.columns = [
        'ID', 'Name', 'Hazardous', 'Approach Date', 'Min Diameter (km)', 
        'Max Diameter (km)', 'Velocity (km/s)', 'Miss Distance (km)'
    ]
    
    # Display the interactive table
    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()