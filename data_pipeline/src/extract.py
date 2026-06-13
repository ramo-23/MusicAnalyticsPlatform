import os
import requests
import json
from dotenv import load_dotenv

# Check where script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define parent directory
PIPLINE_DIR = os.path.dirname(SCRIPT_DIR)

# Load the environment variables from the .env file
load_dotenv(os.path.join(PIPLINE_DIR, ".env"))

def fetch_top_tracks(tag="amapiano", limit=5):
    api_key = os.getenv("LASTFM_API_KEY")
    """
    Fetches the top amapiano tracks from the Last.fm API.
    """

    if not api_key:
        raise ValueError("API key is not set. Please set the LASTFM_API_KEY environment variable.")
    
    # According to the Last.fm API documentation, the endpoint for fetching top tracks by tag is as follows:
    url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={tag}&limit={limit}&api_key={api_key}&format=json"

    print(f"Fetching top {limit} trending tracks for '{tag}'...")
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Save the raw JSON into the raw_data directory
        output_path = os.path.join(PIPLINE_DIR, "raw_data", f"sample_response.json")

        # Ensure the raw_data directory exists before saving
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Data saved to {output_path}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f"Response: {response.text}")
    
if __name__ == "__main__":
    fetch_top_tracks()