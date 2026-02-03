"""
Project: Misinformation and AI (YouTube)
Module: data_processing.py
==============================
"""

import pandas as pd

def aggregate(key_word, query_list):
    df = []

    for query in query_list:
        df.append(pd.read_csv(f"data/doordash_girl_{key_word}_{'_'.join(query.split())}.csv"))

    df_save = pd.concat(df, ignore_index=True) # as to not have list of df
    df_save.to_csv(f"yt_doordash_girl_{key_word}_AGGR.csv", index=False)

    return None
    

def clean_get_url_data(df, remove_list):
    """
    Cleans the data in a pandas data frame for get_url.
    """
    # remove irrelevant rows
    df = df[~df['video_id'].isin(remove_list)]
    df.reset_index(drop=True, inplace=True)

    # remove duplicate rows
    df.drop_duplicates(inplace=True)

    # standardize dates based on MM-DD-YY
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    df['publish_date'] = df['publish_date'].dt.strftime('%m-%d-%y')

    df.to_csv("yt_doordash_girl_url_AGGR_clean.csv", index=False)

    return None
