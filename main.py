"""
Project: Misinformation and AI (YouTube)
Module: main.py
==============================
"""

import pandas as pd
# from youtube_scrape import *
from data_processing import *
from vader import *


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

    queries = [
        'Doordash girl',
        'Doordash girl case',
        'Doordash girl deepfake',
        'Doordash girl AI',
        'Olivia Henderson',
        'Olivia Henderson deepfake',
        'Olivia Henderson AI',
        'Olivia Henderson court'
    ]

    '''
    The list remove_id includes video ids for YouTube videos unrelated to the
    doordash girl case that were a part of the top 10 videos for a query for
    a date range. They were manually identifed and checked to be irrelevant.
    '''

    remove_id = [
        'RZvmqLnz3Cs',
        'M9vmSPKBSzE',
        'UvFii2zv3SU',
        'N7sbCbrli-s',
        '0L2x9_SRpMM',
        'xOfSTOLeijk',
        'JeorPuxvEOU',
        'dMXPFQpqKPQ',
        'zrnQVP7pMds',
        'MJmjh_Mgp10',
        'xqjKErnpycA',
        'uPAwqaiNekA',
        'xmJ-USPfau8',
        'Hq8sU3kU914',
        '5N2JnGKlk34',
        'aJC4thspVUs',
        'g3VCmRseGTk',
        '4Sl5NEcHu2M',
        'rWFdvIXiI',
        'R0IAtFlRPq4',
        'NMFZjDfe5C8',
        '5No0Io1vBho', # unavail video
        '_0lUbqA1d24', # irrelevant
        'jR1UyOGWUE0',
        'oSKuK4xNPFs',
    ]
    # 'IgQK3tz-fKM' -> in foreign lang, added after main processing


    # df = pd.read_csv("data/yt_doordash_girl_comments_AGGR_clean.csv")
    # fetch_vader(df, 'comments')
    vader_comments_processing()


def fetch_comments(id_list):
    batch_size = 10
    batch_num = 13
    # problem so re-ran batch 13
    # to start from first video -> batch_num = 1, and range(0, len(id), batch_size)

    for i in range(120, len(id_list), batch_size):
        lst = id_list[i:(i + batch_size)]

        print(f"Running get_comments_data for batch {batch_num}...")

        get_comments_data(lst, batch_num)

        print(f"Successfully ran get_comments_data for batch {batch_num}!\n")
        batch_num += 1
        time.sleep(5)


def fetch_transcript(id_list):
    batch_size = 10
    batch_num = 2

    for i in range(10, len(id_list), batch_size):
        lst = id_list[i:(i+batch_size)]

        print(f"\nRunning get_transcripts_data for batch {batch_num}...")

        get_transcript_data(lst, batch_num)

        print(f"Successfully ran get_trancsripts_data for batch {batch_num}!\n")
        batch_num += 1
        time.sleep(5)


def fetch_vader(df, type):

    if type == 'transcript':
        df.dropna(subset=['transcript'], inplace=True)
        results = pd.concat([vader(r.video_id, r.transcript, type) for r in df.itertuples()], ignore_index=True)
    else:
        df.dropna(subset=['text_display'], inplace=True)
        results = pd.concat([vader(r.video_id, r.text_display, type, r.comment_id, r.parent_id) for r in df.itertuples()], ignore_index=True)

    results.to_csv(f"yt_{type}_vader.csv", index=False)
    print(f"Success for {type}!")

    return None

if __name__ == "__main__":
    main()
