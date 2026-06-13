import json
import os

# Define script and pipeline paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_DIR = os.path.dirname(SCRIPT_DIR)

def flatten_lastfm_data():
    input_path = os.path.join(PIPELINE_DIR, "raw_data", "sample_response.json")

    # Read the raw JSON data from the file
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    # Drill down to the actual array of tracks
    tracks = raw_data.get("tracks", {}).get("track", [])

    dim_track = []
    dim_artist = []
    fact_metrics = []

    for track in tracks:
        # Extract raw values
        track_name = track.get("name")
        artist_name = track.get("artist", {}).get("name")
        rank = track.get("@attr", {}).get("rank")

        # Generate the surrogate keys to ensure uniqueness for the dimension tables
        artist_id = artist_name.lower().replace(" ", "_")
        track_id = f"{artist_id}_{track_name.lower().replace(' ', '_')}"

        # Build the dimension tables
        # 1. Build the Artist dimension table
        dim_artist.append({
            "Artist_ID": artist_id,
            "Name": artist_name
        })

        # 2. Build the Track dimension table
        dim_track.append({
            "Track_ID": track_id,
            "Artist_ID": artist_id,
            "Title": track_name,
            "Genre": "amapiano"
        })

        # 3. Build the Fact table
        fact_metrics.append({
            "Track_ID": track_id,
            "Chart_Rank": int(rank),
            "Platform": "lastfm"
        })
    
    return dim_track, dim_artist, fact_metrics

if __name__ == "__main__":
    # Basic extraction test based on tracks, artists, and other relevant data
    tracks, artists, metrics = flatten_lastfm_data()
    print(f"Successfully flattened {len(tracks)} tracks for loading into the data warehouse.")
