import pandas as pd
from youtube_scrape import get_url, get_transcript
import time
import random

video_columns = [
    'video_id',
    'url',
    'video_title',
    'channel_id',
    'channel_title',
    'publish_date',
    'description'
]

transcript_columns = [
    'video_id',
    'transcript'
]

def main():
    # url_df = get_url_data()
    # print(url_df.head())

    url_df = pd.read_csv("data/doordash_girl_url_data.csv")

    transcript_df = get_transcript_data(url_df)


def get_url_data():
    """
    DOCSTRING HERE
    """

    print("Running get_url function...\n")

    term = "Doordash girl"
    video_data = []

    date_list = [
        ['2025-10-12T00:00:00Z', '2025-11-12T23:59:59Z'],
        ['2025-11-13T00:00:00Z', '2025-12-12T23:59:59Z'],
        ['2025-12-13T00:00:00Z', '2026-01-12T23:59:59Z'],
        ['2026-01-13T00:00:00Z', '2026-01-25T23:59:59Z']
    ]

    for row in date_list:
        print(f"Running get_url for {row}\n")

        video_data.extend(get_url(term, row[0], row[1])) # EXTEND NOT APPEND

        print(f"Success get_url for {row}\n")

    df = pd.DataFrame(video_data, columns=video_columns)

    df.to_csv("doordash_girl_url_data.csv", index=False)

    return df


def get_transcript_data(url_df):
    """
    DOCSTRING HERE
    """

    print("Running get_transcript_data function...\n")

    temp = url_df.head()


    row = []

    for id in temp['video_id']:
        print(f"Running get_transcript for {id}...")
        row.append([id, get_transcript(id)])

        time.sleep(random.uniform(10, 30)) # wait time to prevent IP ban

    df = pd.DataFrame(row, columns=transcript_columns)
    df.to_csv("doordash_girl_text_data.csv", index=False)

    return df


if __name__ == "__main__":
    main()
