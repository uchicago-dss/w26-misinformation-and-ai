import re
import requests
from bs4 import BeautifulSoup
import spacy
import numpy as np
import trafilatura

BOILERPLATE_PATTERNS = [
    r'©|Â©', r'All rights reserved', r'Subscribe', r'Privacy Policy',
    r'Terms of Use', r'Click here', r'By entering your email',
    r'Getty Images|Reuters|AP Photo',  # Image credits
    r'Market data provided', r'Legal Statement',
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/105.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

def remove_caps_sequences(text, min_consecutive_caps=3):
    """
    Remove sequences of consecutive all-caps words from text.
    Returns the cleaned text.
    """
    words = text.split()
    result = []
    i = 0
    
    while i < len(words):
        # Check if this starts a caps sequence
        if words[i].isupper() and len(words[i]) > 1:
            # Count consecutive caps words
            caps_start = i
            while i < len(words) and words[i].isupper() and len(words[i]) > 1:
                i += 1
            
            caps_length = i - caps_start
            
            # Only remove if it's a long enough sequence
            if caps_length < min_consecutive_caps:
                # Keep these words - not a headline
                result.extend(words[caps_start:i])
        else:
            result.append(words[i])
            i += 1
    
    return ' '.join(result)

from trafilatura.metadata import extract_metadata

def get_article_content(url, nlp):
    downloaded = trafilatura.fetch_url(url)

    if not downloaded:
        raise Exception("Download failed")

    tra_text = trafilatura.extract(downloaded)

    if not tra_text or len(tra_text.strip()) == 0:
        raise Exception("Could not extract article content")

    metadata = extract_metadata(downloaded)
    publish_date = metadata.date if metadata else None

    doc = nlp(tra_text)
    tokenized_text = [x.text for x in doc.sents]
    cleaned_text = extract_article_text(tokenized_text, nlp)
    gpt_format = '$*$ '.join([x.strip() for x in cleaned_text])

    return gpt_format, publish_date



def extract_article_text(paragraphs, nlp, min_words=3, min_density=0.3, min_caps_sequence=3):
    results = []

    for p in paragraphs:
        text = p.strip()
        
        # Skip empty
        if not text:
            continue
            
        # Skip boilerplate
        if any(re.search(pat, text, re.IGNORECASE) for pat in BOILERPLATE_PATTERNS):
            continue
        
        # Remove all-caps sequences and skip if too little remains
        text = remove_caps_sequences(text, min_caps_sequence)
        if len(text.split()) <= 3:
            continue
        
        # Skip too short
        words = text.split()
        if len(words) < min_words:
            continue

        results.append(text)
    
    return results

def filter_input_text(text, nlp):
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove excess blank lines
    text = re.sub(r'\t\s*\t', '\t', text)
    text = text.encode("utf-8", errors='ignore').decode("utf-8") #Replacing unicode characters
    text = text.strip()
    #Removing strings of repeated capital letters
    consecutive_caps = r'(?<![.]\s)(?:\b[A-Z]+\b(?:[^\w\s]*)\s+){1,}\b[A-Z]+\b[^\w\s]*'
    text = re.sub(consecutive_caps, "", text)
    doc: spacy.tokens.doc.Doc = nlp(text)
    doc_sents = [x for x in doc.sents]
    seen_lines = [str(sent).strip() for sent in doc_sents]
    full_text = '$*$ '.join(seen_lines)

    return full_text

import csv
from datetime import datetime

from dateutil import parser

def standardize_date(date_str):
    if not date_str:
        return ""

    try:
        dt = parser.parse(date_str)
        return dt.strftime("%m-%d-%Y")
    except:
        return ""
    

def save_articles(urls, out_csv="articles.csv"):
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    seen = set()
    deduped_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped_urls.append(u)
        else:
            print("[SKIP duplicate URL]", u)

    rows = []
    texts = []

    for url in deduped_urls:
        text = ""
        status = "fail"
        std_date = ""

        try:
            text, publish_date = get_article_content(url, nlp)
            std_date = standardize_date(publish_date)
            status = "ok"
            texts.append(text)
            print("[OK ]", url, "date=", std_date, "words=", len(text.replace("$*$", " ").split()))
        except Exception as e:
            status = f"fail:{type(e).__name__}"
            print("[FAIL]", url, status)

        rows.append({
            "url": url,
            "published_date": std_date,
            "status": status,
            "word_count": len(text.replace("$*$", " ").split()),
            "collected_at": datetime.utcnow().isoformat(),
            "text": text
        })

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["url", "published_date", "status", "word_count", "collected_at", "text"]
        )
        writer.writeheader()
        writer.writerows(rows)

    return texts

import os

print("CWD:", os.getcwd())
print("top_keywords.csv exists?", os.path.exists("top_keywords.csv"))


from collections import Counter

STOPWORDS = {
    "the","a","an","and","or","but","if","to","of","in","on","for","with","as",
    "is","are","was","were","be","been","being","it","this","that","these","those",
    "at","by","from","they","them","their","you","your","we","our","i","he","she",
    "his","her","not","no","do","does","did","so","than","then",
    "said","say","says","about","had","when","has"
}

EXTRA_STOPWORDS = {
    "one","two","three","first","second",
    "after","before","during","while","when","where","who","whom","whose","which",
    "also","still","just","now","then","than",
    "could","would","should","may","might","must","can",
    "into","over","under","between","within","without","across","around",
    "said","say","says","according","report","reported","reports","told",
    "police","officials","authorities","statement",
    "oct","nov","dec","jan","feb","mar","apr","jun","jul","aug","sep",
    "day","days","week","weeks","year","years",
}
STOPWORDS = STOPWORDS.union(EXTRA_STOPWORDS)


def extract_top_keywords(texts, top_k=50, min_count=1):
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    counter = Counter()

    for text in texts:
        clean = text.replace("$*$", " ")
        doc = nlp(clean)

        for token in doc:
            t = token.text.lower()

            if token.pos_ not in {"NOUN", "PROPN"}:
                continue
            if t in STOPWORDS:
                continue
            if len(t) < 3:
                continue
            if not re.match(r"^[a-z']+$", t):
                continue

            counter[t] += 1
    items = [(k, c) for k, c in counter.most_common() if c >= min_count]
    return items[:top_k]

FOCUS = {"deepfake", "ai", "surveillance", "tiktok", "doordash", "court", "arrest", "assault", "misinformation"}

def extract_top_bigrams(texts, top_k=30, min_count=3):
    bigrams = []
    for text in texts:
        clean = text.replace("$*$", " ").lower()
        tokens = re.findall(r"[a-z']+", clean)
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) >= 3]

        for i in range(len(tokens) - 1):
            a, b = tokens[i], tokens[i+1]
            if (a in FOCUS) or (b in FOCUS):
                bigrams.append(a + " " + b)

    c = Counter(bigrams)
    items = [(k, v) for k, v in c.most_common() if v >= min_count]
    return items[:top_k]

if __name__ == "__main__":
    urls = ["https://www.wired.com/story/the-viral-doordash-girl-saga-unearthed-a-nightmare-for-black-creators/",
            "https://www.usatoday.com/story/news/nation/2025/11/19/doordash-driver-charged-naked-customer/87351645007/",
            "https://www.wired.com/story/the-viral-doordash-girl-saga-unearthed-a-nightmare-for-black-creators/",
            "https://www.syracuse.com/crime/2025/11/doordash-driver-posts-video-of-partially-nude-oswego-man-she-says-exposed-himself-now-shes-been-arrested.html",
            "https://people.com/doordash-driver-arrested-posted-video-tiktok-naked-sleeping-customer-11850899",
            "https://www.localsyr.com/news/local-news/oswego-doordash-driver-in-court-for-allegations-she-posted-video-of-naked-customer-on-tiktok/",
            "https://www.newsweek.com/olivia-henderson-doordash-delivery-sexual-assault-customer-video-arrest-11055111",
            "https://www.foxcarolina.com/2025/11/18/doordash-driver-charged-after-recording-posting-video-nude-customer-police-say/",
            "https://nypost.com/2025/11/17/us-news/doordash-driver-arrested-over-sharing-naked-vid-of-customer/",
            "https://lawandcrime.com/crime/doordash-driver-whips-out-cellphone-and-films-illegal-tiktok-of-unconscious-and-half-naked-customer-then-makes-up-a-sexual-assault-claim-cops-say/",

    ]

texts = save_articles(urls)

keywords = extract_top_keywords(texts, top_k=50, min_count=5)

for k, c in keywords[:50]:
    print(k, c)

print("Number of usable articles:", len(texts))

bigrams = extract_top_bigrams(texts, top_k=30, min_count=3)
for k, c in bigrams:
    print(k, c)

with open("top_keywords.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "count"])
        w.writerows(keywords)

with open("top_bigrams.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["bigram", "count"])
    w.writerows(bigrams)

print("Saved:", os.path.abspath("top_keywords.csv"))
print("Saved bigrams:", os.path.abspath("top_bigrams.csv"))