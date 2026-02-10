import requests
import pandas as pd

API_KEY = 'Yayyv88MDqf7Rm37VXPSSQL3acE2'

def get_transcript(video_url):
    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    params = {
        'url': video_url,
        'language': 'en',
        'use_ai_as_fallback': 'true'  # Only get native captions
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
            'segments': data.get('segments', [])
        }
    return None

# Process multiple videos
video_urls = [
    'https://www.tiktok.com/@_/video/7502525122545225003',
    # ... more URLs
]

results = []
for url in video_urls:
    transcript_data = get_transcript(url)
    if transcript_data:
        results.append(transcript_data)

# Save to CSV
df = pd.DataFrame(results)
df.to_csv('transcripts.csv', index=False)
print("done")