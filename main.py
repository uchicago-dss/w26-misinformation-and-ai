"""
Project: Misinformation and AI (YouTube)
Module: main.py
==============================
"""

import pandas as pd
from youtube_scrape import *
from data_processing import *

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

    # aggregate("url", queries[:])

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
        '5No0Io1vBho' # unavail video
    ]

    # df = pd.read_csv("data/doordash_girl_url_AGGR.csv")
    # clean_get_url_data(df, remove_id)

    df = pd.read_csv("data/yt_doordash_girl_url_AGGR_clean.csv")
    video_id_list = df['video_id']

    # GET COMMENTS:
    # fetch_comments(video_id_list)

    # AGGREGATE COMMENTS:
    batch_list = []
    for i in range(1, 14):
        batch_list.append(f'batch{i}')

    aggregate('comments', batch_list)


def fetch_comments(id):
    batch_size = 10
    batch_num = 13
    # problem so re-ran batch 13
    # to start from first video -> batch_num = 1, and range(0, len(id), batch_size)

    for i in range(120, len(id), batch_size):
        lst = id[i:(i + batch_size)]

        print(f"Running get_comments_data for batch {batch_num}...")

        get_comments_data(lst, batch_num)

        print(f"Successfully ran get_comments_data for batch {batch_num}!\n")
        batch_num += 1
        time.sleep(5)


if __name__ == "__main__":
    main()
