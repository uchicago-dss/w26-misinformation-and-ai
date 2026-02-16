"""
analysis is per sentence

"""
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('punkt')

vader_columns_tscript = [
    'video_id',
    'type',
    'sentence_index',
    'text',
    'compound',
    'pos',
    'neg',
    'neu'
]

vader_columns_comments = [
    'video_id',
    'type',
    'sentence_index',
    'text',
    'compound',
    'pos',
    'neg',
    'neu',
    'comment_id',
    'parent_id'
]

def vader(video_id, text, type, comment_id=None, parent_id=None):

    print(f"Processing {type} for {video_id}...")

    if video_id == 'IgQK3tz-fKM': # skip this one bc in diff lang
        return None

    sentences = nltk.sent_tokenize(text)

    analyzer = SentimentIntensityAnalyzer()

    results = []

    for i, sentence in enumerate(sentences):
        vs = analyzer.polarity_scores(sentence)

        if type == 'comments':
            cols = vader_columns_comments
        else:
            cols = vader_columns_tscript

        row = {
            'video_id': video_id,
            'type': type,
            'sentence_index': i,
            'text': sentence,
            'compound': vs['compound'],
            'pos': vs['pos'],
            'neg': vs['neg'],
            'neu': vs['neu']
        }

        if type == 'comments':
            row['comment_id'] = comment_id
            row['parent_id'] = parent_id

        results.append(row)

    return pd.DataFrame(results, columns=cols)
