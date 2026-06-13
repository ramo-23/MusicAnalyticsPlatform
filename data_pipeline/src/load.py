import duckdb
import os
from transform import flatten_lastfm_data

# Define script, pipeline, and database paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PIPELINE_DIR, "lastfm_data.db")

def init_db():
    # Connect to DuckDB (it will create the database file if it doesn't exist)
    conn = duckdb.connect(DB_PATH)

    # Create the dimension and fact tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_artist (
            Artist_ID VARCHAR PRIMARY KEY,
            Name VARCHAR
        );
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dim_track (
            Track_ID VARCHAR PRIMARY KEY,
            Artist_ID VARCHAR,
            Title VARCHAR,
            Genre VARCHAR,
        );
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fact_metrics (
            Track_ID VARCHAR,
            Chart_Rank INTEGER,
            Platform VARCHAR,
            Date_Inserted DATE DEFAULT CURRENT_DATE
        );
    """)
    
    return conn

def load_data():
    conn = init_db()

    # Grab the transformed data from the transform script
    dim_track, dim_artist, fact_metrics = flatten_lastfm_data()

    print("Inserting Artists...")
    for artist in dim_artist:
        conn.execute("""
            INSERT INTO Dim_Artist (Artist_ID, Name)
            VALUES (?, ?)
            ON CONFLICT (Artist_ID) DO NOTHING
        """, (artist["Artist_ID"], artist["Name"]))

    print("Inserting Tracks...")
    for track in dim_track:
        conn.execute("""
            INSERT INTO Dim_Track (Track_ID, Artist_ID, Title, Genre)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (Track_ID) DO NOTHING
        """, (track["Track_ID"], track["Artist_ID"], track["Title"], track["Genre"]))

    print("Inserting Metrics...")
    for metric in fact_metrics:
        conn.execute("""
            INSERT INTO Fact_Metrics (Track_ID, Chart_Rank, Platform)
            VALUES (?, ?, ?)
        """, (metric["Track_ID"], metric["Chart_Rank"], metric["Platform"]))
    
    print(f"\nSuccessfully loaded data into the warehouse at {DB_PATH}")

    # Run a simple query to verify the data was loaded correctly
    print("\n--- Analytics Warehouse: Top Tracks ---")
    result = conn.execute("""
        SELECT t.Title, a.Name AS Artist, m.Chart_Rank
        FROM Fact_Metrics m
        JOIN Dim_Track t ON m.Track_ID = t.Track_ID
        JOIN Dim_Artist a ON t.Artist_ID = a.Artist_ID
        ORDER BY m.Chart_Rank ASC
        LIMIT 5;
    """).fetchall()

    for row in result:
        print(f"Rank {row[2]}: {row[0]} by {row[1]}")

if __name__ == "__main__":
    load_data()
