"""
Project: Misinfo and AI (YouTube)
Module: youtube_scrape.py
==============================
"""

import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import time
import random
from datetime import datetime
from googleapiclient.errors import HttpError


API_KEY = "" # DO NOT UPLOAD KEY TO GITHUB
youtube = build('youtube', 'v3', developerKey=API_KEY)


video_columns = [
    'video_id',
    'url',
    'video_title',
    'channel_id',
    'channel_title',
    'publish_date',
    'description'
]

comments_columns = [
    'video_id',
    'comment_id',
    'parent_id',
    'author_display_name',
    'text_display',
    'like_count',
    'published_at',
    'updated_at',
    'accessed_at'
]

transcript_columns = [
    'video_id',
    'transcript'
]


def get_url(search_term, published_after, published_before, max_results=10):
    """
    Uses the YouTube API to get information about the top 10 videos for a given
    search term and publication date range.

    Args:
        - search_term (string): search term of interst
        - published_after (string): lower bound for video date, ISO 8601 format
        - pushed_before (string): upper bound for video date, ISO 8601 format
    
    Returns (string[]):
        - returns a string array with the following data:
            - video_id
            - url
            - video_title
            - channel_id
            - channel_title
            - publish_date
            - description
    """

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

    search_results = []

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

    print(f"get_url for {search_term} from {published_before} to {published_after} success!")

    return search_results


def get_url_data(query_list):
    """
    Calls the get_url() function from youtube_scrape.py for a series of search
    terms and a range of dates (1 month intervals, starts the day of the door
    dash girl incident and ends on 2026-01-25T23:59:59Z). Saves the information
    as multiple csvs, grouped by search term.

    Args:
        - query_list (String[]): a list of search terms of interest

    Returns:
        - None
    """

    date_list = [
        ['2025-10-12T00:00:00Z', '2025-11-12T23:59:59Z'],
        ['2025-11-13T00:00:00Z', '2025-12-12T23:59:59Z'],
        ['2025-12-13T00:00:00Z', '2026-01-12T23:59:59Z'],
        ['2026-01-13T00:00:00Z', '2026-01-25T23:59:59Z']
    ]

    for query in query_list:
        video_data = []
        for date in date_list:
            video_data.extend(get_url(query, date[0], date[1])) # EXTEND NOT APPEND

        df = pd.DataFrame(video_data, columns=video_columns)
        df.to_csv(f"doordash_girl_url_{'_'.join(query.split())}.csv", index=False)
        print(f"Successfully ran get_url for {query}")

    return None


def get_transcript(video_id):
    """
    Gets the transcript of a YouTube video based on its ID.

    Args:
        - video_id (string): a YouTube video's ID

    Returns (string):
        - returns the english transcript for the video, if available
        - if unable to get english transcript or encounter other isuses,
            returns an error message
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

    # error handling
    except TranscriptsDisabled:
        return "ERROR: Transcripts disabled for this video."
    except NoTranscriptFound:
        return "ERROR: No english transcript found."
    except Exception as e:
        return f"ERROR: {e}"


def get_transcript_data(url_df):
    """
    Calls the get_transcript() function from youtube_scrape.py for a series of
    urls. Saves the transcripts as a csv with 2 columns: video_id and transcript

    Args:
        - url_df: a data frame with a series of YouTube video IDs

    Returns:
        - None
    """
    # print("Running get_transcript_data function...\n")

    temp = url_df.head()

    row = []

    for id in temp['video_id']:
        print(f"Running get_transcript for {id}...")
        row.append([id, get_transcript(id)])

        time.sleep(random.uniform(10, 30)) # wait time to prevent IP ban

    df = pd.DataFrame(row, columns=transcript_columns)
    df.to_csv("doordash_girl_text_data.csv", index=False)

    return None


def get_stats(video_id):
    """
    Gets stats for video.
    """


def get_comments(video_id, max_results=100):
    """
    COLUMNS FOR COMMENT DATA:
    video_id
    comment_id
    parent_id (if it's a response to smth else)
    author_display_name
    text_display
    like_count
    published_at
    updated_at
    accessed_at

    Returns:
        - comments (string[]) lol?
    """
    print(f"Running get_comments for {video_id}....")
    next_page_token = None
    comments = []

    while True:
        request = youtube.commentThreads().list(
            videoId=video_id,
            part='snippet',
            maxResults=max_results,
            textFormat='plainText',
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            # get top comment
            top_snippet = item['snippet']['topLevelComment']['snippet']
            top_comment_id = item['snippet']['topLevelComment']['id']

            top_row = {
                'video_id': video_id,
                'comment_id': top_comment_id,
                'parent_id': None,
                'reply_count': item['snippet']['totalReplyCount'],
                'author_display_name': top_snippet['authorDisplayName'],
                'text_display': top_snippet['textDisplay'],
                'like_count': top_snippet['likeCount'],
                'published_at': top_snippet['publishedAt'],
                'updated_at': top_snippet['updatedAt'],
                'accessed_at': datetime.now()
            }
            comments.append(top_row)

            if top_row['reply_count'] > 0:

                reply_request = youtube.comments().list(
                    part='snippet',
                    parentId=top_comment_id,
                    maxResults=100
                )
                reply_response = reply_request.execute()

                for reply in reply_response['items']:
                    snippet = reply['snippet']

                    reply_row = {
                        'video_id': video_id,
                        'comment_id': reply['id'],
                        'parent_id': top_comment_id,
                        'reply_count': None,
                        'author_display_name': snippet['authorDisplayName'],
                        'text_display': snippet['textDisplay'],
                        'like_count': snippet['likeCount'],
                        'published_at': snippet['publishedAt'],
                        'updated_at': snippet['updatedAt'],
                        'accessed_at': datetime.now()
                    }
                    comments.append(reply_row)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    
    print(f"Successfully ran get_comments for {video_id}!\n")

    return comments


def get_comments_data(video_id_df, key_num):
    """
    Calls the get_comments() function from youtube_scrape.py for a series of
    video ids. Combines the comments data for all video ids of interest into
    one pandas data frame and saves it as a csv.

    Args:
        - video_id_df (string[]): list of video ids

    Returns:
        - None
    """

    data = []
    for id in video_id_df:
        data.extend(get_comments(id))

    df = pd.DataFrame(data, columns=comments_columns)
    df.to_csv(f"doordash_girl_comments_batch{key_num}.csv", index=False)

    # df.to_csv("comments.csv", index=False)

    return None
