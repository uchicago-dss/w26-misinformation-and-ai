import requests
import pandas as pd
from pathlib import Path
import json
import sys

API_KEY = 'RImoCIugWlbuFGiFqGc2K3FIa9n2'
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FOLDER = BASE_DIR / "data"

FILE_PATH = DATA_FOLDER / "video_ids_left"

def get_transcript(video_url):
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    params = {
        'url': video_url,
        'language': 'en',
        'use_ai_as_fallback': 'false'  # Only get native captions
    }
    
    response = requests.get(
        'https://api.scrapecreators.com/v1/tiktok/video/transcript',
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()
        return {
            'url': video_url,
            'transcript': data.get('transcript', ''),
        }
    raise ValueError("Out of Credits")

def retrieve_ids(path: str) -> dict[str, str]:
    #if it is saved, the load the existing
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
        
    else:
        df = pd.read_csv(DATA_FOLDER / "tiktok_clean_data.csv")
        df["transcript"] = None
        return df[["video_id", "transcript"]].to_dict(orient="records")

def main():
    video_list = retrieve_ids(FILE_PATH)
    
    for record in video_list:
        if record['transcript'] is not None:
            continue

        try:
            url = f"https://www.tiktok.com/@_/video/{record['video_id']}"
            transcript_data = get_transcript(url)
            if transcript_data:
                record['transcript'] = transcript_data['transcript']
        except Exception as e:
            with open(FILE_PATH, "w") as f:
                json.dump(video_list, f, indent=4)
            print(f"Error occurred: {e}. Progress saved.")
            sys.exit()

    with open(FILE_PATH, "w") as f:
        json.dump(video_list, f, indent=4)
    print(f"Finished. Progress saved.")
    
    df = pd.read_csv(DATA_FOLDER / "tiktok_clean_data.csv")
    transcript_map = {record['video_id']: record['transcript'] for record in video_list}
    df['transcripts'] = df['video_id'].map(transcript_map)
    df.to_csv(DATA_FOLDER / "tiktok_clean_data_transcripts.csv")


if __name__ == "__main__":
    main()