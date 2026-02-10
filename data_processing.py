"""
Project: Misinformation and AI (YouTube)
Module: data_processing.py
==============================
"""

import pandas as pd
import statistics
import matplotlib.pyplot as plt
import mpld3

vader_tscript_cols = [
    'video_id',
    'type',
    'hook_stdev',
    'hook_category',
    'overall_stdev',
    'overall_category',
    'pos_count',
    'neu_count',
    'neg_count'
]

# vader_comments_cols = [
#     'video_id',
#     'comment_count',
#     'pos_count',
#     'neu_count',
#     'neg_count'
# ]

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


def clean_agg(remove_list):

    video_df = pd.read_csv("data/yt_doordash_girl_video_finalAGGR.csv")
    comments_df = pd.read_csv("data/yt_doordash_girl_comments_AGGR.csv")

    print(f"Num rows (video_df): {video_df.shape[0]}")
    print(f"Num rows (comments_df): {comments_df.shape[0]}")
    print("Starting data cleaning...\n")

    # remove irrelevant rows
    video_df = video_df[~video_df['video_id'].isin(remove_list)]
    video_df.reset_index(drop=True, inplace=True)

    comments_df = comments_df[~comments_df['video_id'].isin(remove_list)]
    comments_df.reset_index(drop=True, inplace=True)

    # remove duplicates
    video_df.drop_duplicates(subset=['video_id'], inplace=True)

    print(f"Num rows (video_df): {video_df.shape[0]}")
    print(f"Num rows (comments_df): {comments_df.shape[0]}")

    video_df.to_csv("yt_dordash_girl_video_finalAGGR_clean.csv", index=False)
    comments_df.to_csv("yt_doordash_girl_comments_AGGR_clean.csv", index=False)


def vader_tscript_processing():
    """
    Data cleaning and analysis for vader video transcript results.

    Analysis:
    - isolate first 5 sentences, find average compound score & standard dev
    - find standard deviation
    - average compound score across video
    - count # neutral, positive, negative
    - graph how the compound score changes across the video??
    - scatter plot with the distribution of the youtube transcript results

    Categories (based on vader github):
    - positive sentiment: compound score >= 0.05 "sympathetic"
    - neutral sentiment: 0.05 > compound score > -0.05 "neutral"
    - negative sentiment: compound score <= -0.05 "inflammatory"
    """
    # 1) read in data
    df = pd.read_csv("data/yt_transcript_vader.csv")

    # 2) transcripts analysis
    # - hook (first 5 sentences, if applicable)
    #   - iterate through indices 0 to 4, inclusive. find the average and stdv

    print("=" * 80)
    print("Youtube Transcripts Analysis\n")

    grouped = df.groupby('video_id')
    results = []
    error = []
    
    for name, group in grouped:
        try:
            print(f"Analysis for {name}...")

            head = group.head()
            hook_avg = head['compound'].mean()
            overall_avg = group['compound'].mean()
            hook_category = categorize(hook_avg)
            overall_category = categorize(overall_avg)

            # make graph plotting progression of compound scores
            print('Creating plot...')
            ax = group.plot(x='sentence_index', y='compound', kind='line')
            fig = ax.get_figure()
            
            ax.set_title(f'{name} Transcript Graph')
            ax.set_xlabel('Sentence Index')
            ax.set_ylabel('Compound Score')

            mpld3.save_html(fig, f'{name}_tscript_graph.html')
            print('Plot saved!\n')

            # save all other data in a row
            row = {
                'video_id': name,
                'type': 'transcript',
                'hook_stdev': statistics.stdev(head['compound']),
                'hook_category': hook_category,
                'overall_stdev': statistics.stdev(group['compound']),
                'overall_category': overall_category,
                'pos_count': (group['compound'] >= 0.05).sum(),
                'neu_count': ((group['compound'] < 0.05) & (group['compound'] > -0.05)).sum(),
                'neg_count': (group['compound'] <= -0.05).sum()
            }

            results.append(row)
        except:
            print(f"\nError for {name}\n")
            error.append(name)
    
    results_df = pd.DataFrame(results, columns=vader_tscript_cols)
    results_df.to_csv('yt_vader_tscript_analysis.csv')

    error_df = pd.DataFrame(error)
    error_df.to_csv('vader_tscript_error_list.csv')

    return None


def vader_comments_processing():
    """
    [INCOMPLETE]

    Data Cleaning:
    - drop the rows where video_id = IgQK3tz-fKM (language is in russian so
        results are skewed to neutral)
    
    Analysis:
    - find average for compound score for each nest of responses and how
        they relate to the compound score of the parent comment
    - standard dev for all coomments under a particular video id
    """
    # # 1) read in data
    # df = pd.read_csv("data/yt_comments_vader.csv")

    # # 2) filter out video id that has commnets in another langugae
    # df = df[df['video_id'] != 'IgQK3tz-fKM']
    # df.to_csv("yt_comments_vader_clean.csv")

    # # 3) analysis
    # print("\n", "=" * 80)
    # print("Youtube Comments Analysis\n")
    # grouped = df.groupby('video_id')


def categorize(compound):
    """
    Categorizes the sentiment of a given sentence beased on compound score.
    """

    if compound >= 0.05:
        category = "sympathetic"
    elif compound <= -0.05:
        category = "inflammatory"
    else:
        category = "neutral"

    return category
