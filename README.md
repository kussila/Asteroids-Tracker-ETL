# 🛰️ Near-Earth Asteroid Tracker: ETL & Dashboard

## Table of Contents

1.  Project Overview
2.  Features
3.  Architecture
4.  Getting Started
      * Prerequisites
      * Installation
5.  Usage
6.  Data Model
7.  File Structure
8.  Next Steps

-----

## 1\. Project Overview

This project is an end-to-end Data Engineering pipeline designed to **Extract, Transform, and Load (ETL)** information about Near-Earth Objects (NEOs) from the NASA NEOWs API.

The processed data is persisted in a **PostgreSQL** database and visualized through an interactive **Streamlit** dashboard, making it accessible to astronomy enthusiasts and analysts.

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Data Source** | NASA NeoWs API | Provides raw asteroid data |
| **Orchestration** | Python (`main.py`) | Executes the ETL process steps |
| **Processing** | Python, Pandas | Handles data transformation and cleaning |
| **Database** | PostgreSQL (Docker) | Persistent storage for cleaned data |
| **Frontend** | Streamlit | Interactive web dashboard for visualization |
| **Containerization** | Docker, Docker Compose | Bundles and manages all services |

## 2\. Features

  * **Automated Data Ingestion:** Extracts data for a defined date range from a public API.
  * **Data Validation and Cleaning:** Transforms raw JSON into a structured, clean format (e.g., converts miles to kilometers, validates data types).
  * **Database Persistence:** Loads clean data into a PostgreSQL table.
  * **Interactive Dashboard:** Provides a user-friendly interface to filter, sort, and analyze asteroid approach data, including distance, velocity, and hazard status.

-----

## 3\. Architecture

The entire application runs as a multi-container environment managed by **Docker Compose**.

1.  The **ETL Processor** container executes the ETL logic.
2.  The **PostgreSQL DB** container stores the final, clean data.
3.  The **Streamlit App** container connects to the DB and serves the web interface.

-----

## 4\. Getting Started

### Prerequisites

You must have the following software installed on your machine:

  * **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Includes Docker and Docker Compose)
  * **Python 3.8+** (Optional, but useful for local development)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/kussila/Asteroids-Tracker-ETL.git
    cd Asteroids-Tracker-ETL
    ```

2.  **Create `.env` file:**
    Create a file named **`.env`** in the root directory and fill in your credentials and API key. **DO NOT** commit this file to GitHub (it is excluded by `.gitignore`).

    ```env
    # NASA API Key (Get a key here: https://api.nasa.gov/)
    NASA_API_KEY=YOUR_API_KEY_HERE

    # Database Credentials
    DB_HOST=postgres-db
    DB_PORT=5432
    DB_NAME=neo_tracker_db
    DB_USER=neo_user
    DB_PASSWORD=secretpassword
    ```

3.  **Run the ETL Pipeline (Initial Load):**
    First, you must run the ETL script once to populate the database with data. This stops the Streamlit app's continuous command and runs the ETL script.

    ```bash
    # Temporarily run the ETL script and exit
    docker-compose run etl-app python main.py
    ```

    *Check your terminal logs to ensure the data was extracted, transformed, and loaded successfully.*

4.  **Start the Dashboard:**
    Now, start all services, including the Streamlit frontend.

    ```bash
    docker-compose up --build -d
    ```

-----

## 5\. Usage

Once the containers are running (Step 4), open your web browser and navigate to:

**Dashboard URL:** `http://localhost:8501`

The Streamlit application will connect to the PostgreSQL database and display the asteroid data.

To stop the services:

```bash
docker-compose down
```

## 6\. Data Model

The `asteroids` table created in the PostgreSQL database has the following schema:

| Column Name | Data Type | Description | Source Field |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR` | NASA JPL ID for the NEO | `id` |
| `name` | `VARCHAR` | Asteroid common name | `name` |
| `is_potentially_hazardous` | `BOOLEAN` | True if NASA lists it as hazardous | `is_potentially_hazardous_asteroid` |
| `close_approach_date` | `DATE` | Date of the closest approach | `close_approach_date` |
| `diameter_min_km` | `DOUBLE PRECISION` | Minimum estimated diameter in kilometers | `estimated_diameter` |
| `diameter_max_km` | `DOUBLE PRECISION` | Maximum estimated diameter in kilometers | `estimated_diameter` |
| `velocity_kps` | `DOUBLE PRECISION` | Relative velocity in kilometers per second | `relative_velocity` |
| `miss_distance_km` | `DOUBLE PRECISION` | Miss distance from Earth in kilometers | `miss_distance` |

-----

## 7\. File Structure

```
.
├── .env                  # Environment variables (IGNORED by Git)
├── .gitignore            # Specifies files/folders to ignore
├── app.py                # Streamlit dashboard application
├── docker-compose.yml    # Defines the multi-container application
├── Dockerfile            # Instructions to build the Python image
├── main.py               # Main orchestration script (calls ETL functions)
├── extract.py            # Logic to fetch data from NASA API
├── transform.py          # Logic to clean and structure data
├── load.py               # Logic to load data into PostgreSQL
└── requirements.txt      # Python dependencies (Streamlit, Pandas, etc.)
```

-----

## 8\. Next Steps

Possible enhancements and features for future development:

  * **Scheduler:** Integrate **Apache Airflow** (or a similar tool) to automatically run the ETL pipeline daily.
  * **Data Visualization:** Add interactive charts (e.g., using Plotly) to the Streamlit dashboard for better analysis.
  * **Error Handling:** Implement robust retry logic and notification services (e.g., email alerts) for ETL failures.