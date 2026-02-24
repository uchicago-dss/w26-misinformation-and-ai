"""
Project: Misinformation and AI (YouTube)
Module: data_processing.py
==============================
"""

import pandas as pd
import statistics
import matplotlib.pyplot as plt
import mpld3
import seaborn as sns

vader_tscript_cols = [
    'video_id',
    'type',
    'hook_stdev',
    'hook_compound',
    'hook_category',
    'overall_stdev',
    'overall_compound',
    'overall_category',
    'pos_count',
    'neu_count',
    'neg_count'
]

vader_comment_byparent_cols = [
    'video_id',
    'parent_id',
    'parent_avg',
    'parent_category',
    'replies_avg',
    'replies_category',
    'replies_stdev'
]
vader_comment_byvideo_cols = [
    'video_id',
    'comments_avg',
    'comments_category',
    'comments_stdev',
    'comments_pos_count',
    'comments_neu_count',
    'comments_neg_count'
]

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
    
    return None

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

    return None

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
    print("YouTube Transcripts Analysis\n")

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

            # save all other data in a row
            row = {
                'video_id': name,
                'type': 'transcript',
                'hook_stdev': statistics.stdev(head['compound']),
                'hook_compound': hook_avg,
                'hook_category': hook_category,
                'overall_stdev': statistics.stdev(group['compound']),
                'overall_compound': overall_avg,
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


def categorize(compound):
    """
    Categorizes the sentiment of a given sentence beased on compound score.
    """

    if compound >= 0.05:
        return 'sympathetic'
    elif compound <= -0.05:
        return 'inflammatory'

    return 'neutral'


def vader_tscript_sum_stats():
    df = pd.read_csv('data/yt_vader_tscript_analysis.csv')
    print(f'sympathetic hooks count: {(df['hook_category'] == 'sympathetic').sum()}')
    print(f'neutral hooks count: {(df['hook_category'] == 'neutral').sum()}')
    print(f'Inflammatory hooks count: {(df['hook_category'] == 'inflammatory').sum()}')

    print('=' * 80)

    print(f'sympathetic overall count: {(df['overall_category'] == 'sympathetic').sum()}')
    print(f'neutral overall count: {(df['overall_category'] == 'neutral').sum()}')
    print(f'Inflammatory overall count: {(df['overall_category'] == 'inflammatory').sum()}')

    return None

def vader_comments_processing():
    """
    Data cleaning and analysis for vader video transcript results.

    Analysis:
    - for every comment, find average compound score
    - count total # positive, negative, neutral (avg) comments for each video ID
    - also for the replies, count # positive, negative, neutral

    Categories (based on vader github):
    - positive sentiment: compound score >= 0.05 "sympathetic"
    - neutral sentiment: 0.05 > compound score > -0.05 "neutral"
    - negative sentiment: compound score <= -0.05 "inflammatory"
    """
    # 1) read in data
    df = pd.read_csv("data/yt_comments_vader.csv")

    # 2) analysis by parent comment
    print("Starting analysis by parent comment...")

    by_parent = []
    grouped = df.groupby('parent_id')

    for name, group in grouped:
        # try:
        print(f"Analyzing comments for {name}...")
        replies_avg = group['compound'].mean()

        try:
            replies_stdev = statistics.stdev(group['compound'])
        except:
            replies_stdev = None

        parent_avg = df[df['comment_id'] == name]['compound'].mean()

        row = {
            'video_id': group['video_id'].iloc[0],
            'parent_id': name,
            'parent_avg': parent_avg,
            'parent_category': categorize(parent_avg),
            'replies_avg': replies_avg,
            'replies_category': categorize(replies_avg),
            'replies_stdev': replies_stdev
        }
        by_parent.append(row)

        # except:
        #     print("=" * 80)
        #     print(f"ERROR for {name}")
        #     print("=" * 80)

    by_parent_df = pd.DataFrame(by_parent, columns=vader_comment_byparent_cols)
    by_parent_df.to_csv("yt_comments_vader_analysis_byparent.csv")


    print("Analysis by parent comment done!")
    print("=" * 80)

    # 3) analysis by video
    print("Starting analysis by video...")

    grouped = df.groupby('video_id')

    by_video = []
    for name, group in grouped:
        # try:
        print(f"Analyzing comments for {name}...")
        avg = group['compound'].mean()

        try:
            stdev = statistics.stdev(group['compound'])
        except:
            stdev = None

        grouped_id = group.groupby('comment_id')

        pos = 0
        neu = 0
        neg = 0

        for _, g in grouped_id:
            category = categorize(g['compound'].mean())
            if category == 'sympathetic':
                pos += 1
            elif category == 'inflammatory':
                neg += 1
            else:
                neu += 1

        row = {
            'video_id': name,
            'comments_avg': avg,
            'comments_category': categorize(avg),
            'comments_stdev': stdev,
            'comments_pos_count': pos,
            'comments_neu_count': neu,
            'comments_neg_count': neg
        }
        by_video.append(row)

        # except:
        #     print("=" * 80)
        #     print(f"ERROR for {name}")
        #     print("=" * 80)

    by_video_df = pd.DataFrame(by_video, columns=vader_comment_byvideo_cols)
    by_video_df.to_csv("yt_comments_vader_analysis_byvideo.csv")

    print("Analysis by vidoe done!")

    return None

def index_score_graph(): # IDK IF THIS WORKS
    """
    Graph the sentence index on the x-axis and the compound score on the y-axis
    for a video.

    *MIGHT NOT WORK*
    """
    # make graph plotting progression of compound scores
    print('Creating plot...')
    ax = group.plot(x='sentence_index', y='compound', kind='line')
    fig = ax.get_figure()

    ax.set_title(f'{name} Transcript Graph')
    ax.set_xlabel('Sentence Index')
    ax.set_ylabel('Compound Score')

    mpld3.save_html(fig, f'{name}_tscript_graph.html')
    print('Plot saved!\n')

    return None

def engagement_analysis():
    """
    - add an engagement_ratio column to data if there isn't one already
    - add a z-score column, if there insn't one already
        - see if there are any outlier z-scores
        - if there are, investigate specifically why those scores are so outlier
    - separate the data based on overall inflammatory, sympathetic, or neutral
        - box plot for each category
    """
    df_stats = pd.read_csv('data/yt_doordash_girl_video_finalAGGR_clean.csv')
    df_vader = pd.read_csv('data/yt_vader_tscript_analysis.csv')

    if 'eng_ratio' not in df_stats.columns:
        # add engagement ratio = (likes + comments) / views
        df_stats['eng_ratio'] = (df_stats['like_count'] * df_stats['comment_count']) / df_stats['view_count']

        # add z-scores based on the engagement ratios
        mean = df_stats['eng_ratio'].mean()
        stdev = statistics.stdev(df_stats['eng_ratio'])
        df_stats['z-score'] = (df_stats['eng_ratio'] - mean) / stdev

        # save as csv
        df_stats.to_csv('yt_doordash_girl_video_finalAGGR_clean.csv', index=False)

    if 'delta_compound' not in df_vader.columns:
        df_vader['delta_compound'] = df_vader['overall_compound'] - df_vader['hook_compound']

        df_vader = df_vader.set_index('video_id')
        df_stats_idx = df_stats.set_index('video_id')

        # copy over the eng ratio and z-score columns
        df_vader['eng_ratio'] = df_stats_idx['eng_ratio']
        df_vader['z-score'] = df_stats_idx['z-score']

        df_vader.reset_index(inplace=True)

        df_vader = df_vader.drop(columns=["Unnamed: 0"])
        df_vader.to_csv('yt_vader_tscript_analysis.csv', index=False)

    # separate based on overall inflammatory, sympathetic, or netural
    # create 3 box plots of engagement ratio based on these categories
    sns.set_theme(style='whitegrid')

    fig, ax = plt.subplots(figsize=(6, 6))
    sns.boxplot(data=df_vader, x='overall_category', y='eng_ratio', ax=ax)
    
    ax.set_title('Engagement Ratio Box Plot by Video Overall Category', fontsize=16)
    ax.set_xlabel('Video Overall Category', fontsize=12)
    ax.set_ylabel('Engagement Ratio', fontsize=12)

    categories = df_vader['overall_category'].unique()
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories)

    plt.tight_layout()

    mpld3.save_html(fig, 'box_plot_overall_cat.html')

    fig, ax = plt.subplots(figsize=(6, 6))
    sns.boxplot(data=df_vader, x='hook_category', y='eng_ratio', ax=ax)
    
    ax.set_title('Engagement Ratio Box Plot by Hook Category', fontsize=16)
    ax.set_xlabel('Hook Category', fontsize=12)
    ax.set_ylabel('Engagement Ratio', fontsize=12)

    categories = df_vader['hook_category'].unique()
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories)

    plt.tight_layout()

    mpld3.save_html(fig, 'box_plot_hook_cat.html')

    return None

def engagement_outliers():
    df_vader = pd.read_csv('data/yt_vader_tscript_analysis.csv')
    outliers = df_vader[(df_vader['z-score'] >= 2) & (df_vader['z-score'] < 3)]
    far_outliers = df_vader[df_vader['z-score'] >= 3]

    outliers.to_csv('vader_outliers.csv', index=False)
    far_outliers.to_csv('vader_far_outliers.csv', index=False)

    return None

def correlation_matrix():
    df = pd.read_csv('data/yt_vader_tscript_analysis.csv')

    df.drop(columns=['video_id', 'type', 'hook_category', 'overall_category'], inplace=True)

    matrix = df.corr()

    plt.figure(figsize=(5, 5))
    sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Correlation Heatmap')
    fig = plt.gcf()

    plt.show()
    mpld3.save_html(fig, 'video_correlation_matrix.html')

    return None
