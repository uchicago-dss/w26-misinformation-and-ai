"""
Project: Misinformation and AI (YouTube)
Module: data_processing.py
==============================
"""

import pandas as pd

def aggregate_batch(key_word, query_list):
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


def clean_transcripts(df):
    is_error = df['transcript'].str.startswith('ERROR', na=False)
    error_df = df.loc[is_error, 'video_id']

    df.loc[is_error, 'transcript'] = None
    df.to_csv("yt_doordash_girl_tscript_AGGR_clean.csv", index=False)

    error_df.to_csv("transcript_error_list.csv", index=False)

    return None


def clean_stats(df):
    """
    fix formatting for duration to HH:MM:SS
    """
    df['duration'] = pd.to_timedelta(df['duration'])

    df['duration'] = df['duration'].dt.components.apply(
        lambda x: f"{x.hours:02}:{x.minutes:02}:{x.seconds:02}", axis=1
    )

    df.to_csv("yt_doordash_girl_stats_clean.csv", index=False)


def final_aggregate():
    url_df = pd.read_csv("data/yt_doordash_girl_url_AGGR_clean.csv")
    
    stats_df = pd.read_csv("data/yt_doordash_girl_stats_clean.csv")
    tscript_df = pd.read_csv("data/yt_doordash_girl_tscript_AGGR_clean.csv")
    channel_df = pd.read_csv("data/yt_doordash_girl_channel.csv")

    # combine stats_df and url_df based on video_id column
    # combine channel_df and url_df based on chanel_id column
    # combine tscript_df and url_df based on video_id column

    url_df = url_df.merge(channel_df, on='channel_id')
    url_df = url_df.merge(stats_df, on='video_id')
    url_df = url_df.merge(tscript_df, on='video_id')

    url_df.to_csv("yt_doordash_girl_video_finalAGGR.csv", index=False)

    print("Success!")
    return None
