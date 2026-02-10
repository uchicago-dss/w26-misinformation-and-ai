"""
analysis is per sentence

"""
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('punkt')

vader_columns = [
    'video_id',
    'type',
    'sentence_index',
    'text',
    'compound',
    'pos',
    'neg',
    'neu'
]

def vader(video_id, text, type):

    print(f"Processing {type} for {video_id}...")

    sentences = nltk.sent_tokenize(text)

    analyzer = SentimentIntensityAnalyzer()

    results = []

    for i, sentence in enumerate(sentences):
        vs = analyzer.polarity_scores(sentence)

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
        results.append(row)

    return pd.DataFrame(results, columns=vader_columns)
