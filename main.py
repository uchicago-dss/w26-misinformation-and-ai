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
        'NMFZjDfe5C8'
    ]

    # df = pd.read_csv("data/doordash_girl_url_AGGR.csv")
    # clean_get_url_data(df, remove_id)

    df = pd.read_csv("data/doordash_girl_url_AGGR_clean.csv")
    video_id_list = df['video_id']

    # GET COMMENTSL:
    def fetch_comments_batch():
        batch_size = 5
        batch_num = 1

        for i in range(0, len(video_id_list), batch_size):
            lst = video_id_list[i:(i + batch_size)]

            print(f"Running get_comments_data for batch {batch_num}...")

            get_comments_data(lst, batch_num)

            print(f"Successfully ran get_comments_data for batch {batch_num}!\n")
            batch_num += 1
            time.sleep(1)

        # test_list = ['f1B2uJK2REk']
        # get_comments_data(test_list, 'test')

        # ENDED AFTER BATCH 2



if __name__ == "__main__":
    main()
