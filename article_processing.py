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

def get_article_content(url, nlp):
    response = requests.get(url, timeout=10, headers=headers)
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        raise Exception(f"Error: Status code {response.status_code}")
    tra_text = trafilatura.extract(response.text)
    
    # Handle case where trafilatura couldn't extract any content
    if tra_text is None or len(tra_text.strip()) == 0:
        print(f"Error: trafilatura could not extract content from {url}")
        raise Exception(f"Error: Could not extract article content from URL")
    
    doc: spacy.tokens.doc.Doc = nlp(tra_text)
    tokenized_text = [x.text for x in doc.sents]
    cleaned_text = extract_article_text(tokenized_text, nlp)
    gpt_format = '$*$ '.join([x.strip() for x in cleaned_text])
    return gpt_format


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

def save_articles(urls, out_csv="articles.csv"):
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    rows = []
    texts = []

    for url in urls:
      try:
        text = get_article_content(url, nlp)
        status = "ok"
        texts.append(text)
        print("[OK ]", url, "words=", len(text.replace("$*$", " ").split()))
      except Exception as e:
        text = ""
        status = f"fail:{type(e).__name__}"
        print("[FAIL]", url, status)


        rows.append({
            "url": url,
            "status": status,
            "word_count": len(text.replace("$*$", " ").split()),
            "collected_at": datetime.utcnow().isoformat(),
            "text": text
            })

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["url", "status", "word_count", "collected_at", "text"]
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

def extract_top_keywords(texts, top_k=50):
    words = []
    for text in texts:
        clean = text.replace("$*$", " ").lower()
        tokens = re.findall(r"[a-z']+", clean)
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) >= 3]
        words.extend(tokens)

    return Counter(words).most_common(top_k)


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

    save_articles(urls)

    

texts = save_articles(urls)

keywords = extract_top_keywords(texts, top_k=50)

for k, c in keywords[:50]:
    print(k, c)

print("Number of usable articles:", len(texts))

with open("top_keywords.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "count"])
        w.writerows(keywords)

print("Saved:", os.path.abspath("top_keywords.csv"))