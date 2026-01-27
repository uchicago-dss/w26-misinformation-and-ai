import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


API_KEY = "AIzaSyA8yb4Y9EdSTJ2CJoMcKDq2AFRB7CjQEzU"
youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_url(search_term, published_after, published_before, max_results=10):
    """
    DOCSTRING HERE
    """

    search_results = []

    request = youtube.search().list(
        q=search_term,
        part='snippet',
        type='video',
        publishedAfter=published_after,
        publishedBefore=published_before,
        order="viewCount",
        relevanceLanguage="en",
        maxResults=max_results
    )
    
    response = request.execute()

    print("Response request successfully executed!")
    
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        snippet = item['snippet']

        rows = {
            'video_id': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'video_title': snippet['title'],
            'channel_id': snippet['channelId'],
            'channel_title': snippet['channelTitle'],
            'publish_date': snippet['publishedAt'],
            'description': snippet['description']
        }
        search_results.append(rows)

    print("API Request Success!\n")

    return search_results


def get_transcript(video_id):
    """
    DOCSTRING HERE
    """

    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)

        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = next(iter(transcript_list)).translate('en')
               
        tx = transcript.fetch()

        out_ls = []

        for i in tx:
            out_txt = i.text
            out_ls.append(out_txt)

        full_text = " ".join(out_ls)

        print(f"Success for {video_id}!\n")
        return full_text

    except TranscriptsDisabled:
        return "ERROR: Transcripts disabled for this video."
    except NoTranscriptFound:
        return "ERROR: No english transcript found."
    except Exception as e:
        return f"ERROR: {e}"
