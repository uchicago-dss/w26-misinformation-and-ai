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

import spacy

if __name__ == "__main__":
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    url = "PASTE_A_NEWS_ARTICLE_URL"
    text = get_article_content(url, nlp)
    print(text)


