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

import json
from urllib.parse import urlparse

def fetch_html_requests(url: str, timeout: int = 10) -> str | None:
    """Fallback fetcher using requests with headers + timeout."""
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        # Many sites return 403/429; keep status for debugging by raising
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def extract_date_from_url(url: str) -> str | None:
    """
    Try extracting date from URL patterns like /2025/11/19/ or -2025-11-19- etc.
    Returns a raw date string parsable by dateutil.
    """
    # /YYYY/MM/DD/
    m = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # -YYYY-MM-DD- or _YYYY-MM-DD_
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # /YYYY/MM/ (no day) -> treat as 1st of month
    m = re.search(r"/(20\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-01"

    return None


def extract_date_from_html(html: str) -> str | None:
    """
    Extract publish date from:
    - OpenGraph / article meta tags
    - <time datetime="">
    - JSON-LD (NewsArticle)
    Returns raw date string.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Common meta tags
        meta_selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("meta", {"name": "publish-date"}),
            ("meta", {"name": "publication_date"}),
            ("meta", {"name": "date"}),
            ("meta", {"property": "og:published_time"}),
        ]
        for tag_name, attrs in meta_selectors:
            tag = soup.find(tag_name, attrs=attrs)
            if tag and tag.get("content"):
                return tag["content"].strip()

        # <time datetime="...">
        t = soup.find("time")
        if t and t.get("datetime"):
            return t["datetime"].strip()

        # JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.get_text(strip=True))
                # JSON-LD may be list or dict
                candidates = data if isinstance(data, list) else [data]
                for obj in candidates:
                    if not isinstance(obj, dict):
                        continue
                    # Sometimes @graph
                    if "@graph" in obj and isinstance(obj["@graph"], list):
                        candidates.extend(obj["@graph"])
                        continue
                    if obj.get("@type") in {"NewsArticle", "Article", "ReportageNewsArticle"}:
                        for k in ["datePublished", "dateCreated", "dateModified"]:
                            if obj.get(k):
                                return str(obj[k]).strip()
            except Exception:
                continue

    except Exception:
        return None

    return None

import json
from urllib.parse import urlparse

def fetch_html_requests(url: str, timeout: int = 10) -> str | None:
    """Fallback fetcher using requests with headers + timeout."""
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        # Many sites return 403/429; keep status for debugging by raising
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def extract_date_from_url(url: str) -> str | None:
    """
    Try extracting date from URL patterns like /2025/11/19/ or -2025-11-19- etc.
    Returns a raw date string parsable by dateutil.
    """
    # /YYYY/MM/DD/
    m = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # -YYYY-MM-DD- or _YYYY-MM-DD_
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # /YYYY/MM/ (no day) -> treat as 1st of month
    m = re.search(r"/(20\d{2})/(\d{2})/", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}-01"

    return None


def extract_date_from_html(html: str) -> str | None:
    """
    Extract publish date from:
    - OpenGraph / article meta tags
    - <time datetime="">
    - JSON-LD (NewsArticle)
    Returns raw date string.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Common meta tags
        meta_selectors = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "article:published_time"}),
            ("meta", {"name": "pubdate"}),
            ("meta", {"name": "publish-date"}),
            ("meta", {"name": "publication_date"}),
            ("meta", {"name": "date"}),
            ("meta", {"property": "og:published_time"}),
        ]
        for tag_name, attrs in meta_selectors:
            tag = soup.find(tag_name, attrs=attrs)
            if tag and tag.get("content"):
                return tag["content"].strip()

        # <time datetime="...">
        t = soup.find("time")
        if t and t.get("datetime"):
            return t["datetime"].strip()

        # JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.get_text(strip=True))
                # JSON-LD may be list or dict
                candidates = data if isinstance(data, list) else [data]
                for obj in candidates:
                    if not isinstance(obj, dict):
                        continue
                    # Sometimes @graph
                    if "@graph" in obj and isinstance(obj["@graph"], list):
                        candidates.extend(obj["@graph"])
                        continue
                    if obj.get("@type") in {"NewsArticle", "Article", "ReportageNewsArticle"}:
                        for k in ["datePublished", "dateCreated", "dateModified"]:
                            if obj.get(k):
                                return str(obj[k]).strip()
            except Exception:
                continue

    except Exception:
        return None

    return None


def get_article_content(url, nlp, timeout=10):
    """
    Robust content + date extraction.
    1) Try trafilatura fetch+extract.
    2) If fails, use requests to fetch HTML then trafilatura.extract(html).
    3) Date: trafilatura metadata -> html meta/time/jsonld -> url.
    """
    downloaded = None
    tra_text = None
    publish_date = None

    # 1) trafilatura fetch
    try:
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
    except Exception:
        downloaded = None

    if downloaded:
        try:
            tra_text = trafilatura.extract(downloaded)
        except Exception:
            tra_text = None

        try:
            metadata = extract_metadata(downloaded)
            publish_date = metadata.date if metadata else None
        except Exception:
            publish_date = None

    # 2) fallback requests fetch
    html = None
    if not tra_text or len(str(tra_text).strip()) == 0:
        html = fetch_html_requests(url, timeout=timeout)
        if not html:
            raise Exception("Download failed (trafilatura+requests)")

        tra_text = trafilatura.extract(html)
        if not tra_text or len(str(tra_text).strip()) == 0:
            raise Exception("Could not extract article content")

        # date fallback from html
        if not publish_date:
            publish_date = extract_date_from_html(html)

    # 3) date fallback from URL
    if not publish_date:
        publish_date = extract_date_from_url(url)

    # sentence split + clean
    doc = nlp(tra_text)
    tokenized_text = [x.text for x in doc.sents]
    cleaned_text = extract_article_text(tokenized_text, nlp)
    gpt_format = "$*$ ".join([x.strip() for x in cleaned_text])

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
            status = f"fail:{type(e).__name__}:{str(e)[:80]}"
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
            "https://www.oswegocountynewsnow.com/news/doordash-driver-case-headed-to-grand-jury/article_d553b1c8-c960-41ad-95c9-0af98a5f8460.html",
            "https://www.oswegocountynewsnow.com/news/doordash-driver-back-in-court-today/article_b70feade-9497-4f1c-90c1-0a06ad0ec91b.html",
            "https://www.wgem.com/2025/11/18/doordash-driver-charged-after-recording-posting-video-nude-customer-police-say/",
            "https://tribune.com.pk/story/2581616/doordash-driver-appears-in-court-after-filming-and-accusing-customer-of-harrassment-during-delivery",
            "https://www.the-independent.com/news/world/americas/crime/doordash-driver-arrested-filming-naked-man-b2867751.html",
            "https://nypost.com/2025/12/10/us-news/ny-doordash-driver-arrested-for-sharing-video-of-passed-out-naked-customer-hides-from-cameras-outside-courthouse/",
            "https://www.oswegocountynewsnow.com/news/incident-with-oswego-doordash-driver-goes-viral/article_57d25644-f245-4c07-9b3e-7d060706bc04.html",
            "https://www.tmz.com/2025/11/17/doordash-driver-recording-naked-man/",
            "https://www.oswegocountynewsnow.com/news/woman-in-doordash-incident-pleads-not-guilty-to-charges/article_f6a3c880-7eb9-467a-8a1a-b780303089e0.html",
            "https://www.oswegocountynewsnow.com/news/lawyer-doordash-driver-charged-with-posting-video-of-naked-customer-has-been-harassed/article_eaf898b6-3256-4d01-86eb-933080beafe5.html",
            "https://www.oswegocountynewsnow.com/news/oswego-doordash-driver-who-posted-viral-video-of-naked-man-on-tiktok-arrested/article_7623d09f-9f02-496a-950c-9a0a116d907a.html",
            "https://www.newsweek.com/doordash-driver-tiktok-sexual-assault-report-firing-10912422",
            "https://www.splicetoday.com/pop-culture/tiktok-victim-cries-wolf-ends-up-with-felony-charges",
            "https://local12.com/news/nation-world/irlmonsterhighdoll-olivia-henderson-doordash-driver-faces-felony-charges-for-recording-customer-without-consent-tiktoker-social-media-viral-videos-cincinnati-crime-criminal-activity-door-dash-company-policy-incapacitated-unconscious-filed-police-report",
            "https://tribune.com.pk/story/2577715/doordash-driver-arrested-after-filming-and-accusing-customer-of-harrassment-during-delivery",
            "https://www.inquisitr.com/doordash-driver-films-customer-in-compromising-situation-then-claims-she-was-assaulted",
            "https://dailyvoice.com/ny/albany/doordash-driver-charged-in-oswego-video-case/",
            "https://www.ibtimes.co.uk/viral-ex-doordash-employee-criminally-charged-faces-possible-10-year-prison-time-1755419",
            "https://littlethings.com/lifestyle/doordash-driver-arrested-filming-sexual-assault-allegations",
            "https://www.ibtimes.co.uk/doordash-girl-video-still-posted-online-even-after-major-update-she-guilty-felony-1755958",
            "https://metro.co.uk/2025/11/19/delivery-driver-arrested-filming-naked-male-customer-ordered-food-24749578/",
            "https://dailydot.com/doordasher-arrested-reactions",
            "https://www.ibtimes.co.uk/viral-doordash-girl-slammed-cops-police-dept-release-intel-true-events-1756537",
            "https://www.dexerto.com/tiktok/tiktok-doordash-driver-olivia-henderson-arrested-after-viral-delivery-incident-leads-to-felony-charge-3283725/",
            "https://www.thehollywoodgossip.com/2025/11/doordash-driver-charged-tiktok-video-unclothed-customer/",
            "https://hip-hopvibe.com/news/doordash-driver-tiktok-surveillance-court-appearance/",
            "https://thenerdstash.com/new-york-doordash-driver-arrested-for-recording-man-inside-his-home-and-posting-his-personal-details-people-dont-think-before-they-share/",
            "https://www.distractify.com/p/doordash-girl-arrested",
            "https://www.dailymail.co.uk/news/article-15301993/female-door-dash-driver-sexual-assault-arrest-oswego-new-york.html",
            "https://www.timesnownews.com/world/us/us-news/who-is-livie-rose-henderson-doordash-driver-fired-after-reporting-sexual-harassment-on-job-video-article-153028991",
            "https://lawenforcementtoday.com/doordasher-arrested-over-tiktok-of-half-naked-customer",
            "https://spitfirenews.com/p/doordash-and-darvo-attacks-on-working-class-women",
            "https://thetab.com/2025/10/21/doordash-responds-to-driver-who-claimed-she-was-fired-after-reporting-on-job-sxual-assault",
            "https://www.themarysue.com/doordash-driver-banned-after-complaint/",
            "https://www.ibtimes.co.uk/who-livie-rose-henderson-doordash-girl-slammed-taking-video-customer-calling-sexual-assault-1749378",
            "https://www.themarysue.com/doordash-customer-exposing-self/",
            "https://tribune.com.pk/story/2573410/doordash-under-scrutiny-as-driver-faces-account-deactivation-after-alleged-harrassment-by-customer",
            "https://www.ibtimes.co.uk/doordasher-says-she-was-sexually-assaulted-customer-why-are-people-saying-shes-not-victim-1748762",
            "https://mothership.sg/2025/10/doordash-driver-sexually-harassed/",
            "https://knowyourmeme.com/editorials/guides/what-is-the-doordash-sa-girl-video-the-controversy-surrounding-claims-from-tiktoker-irlmonsterhighdoll-explained",
            "https://www.indiatimes.com/trending/who-is-livie-rose-henderson-and-why-was-she-fired-by-doordash-tiktok-video-shows-customer-allegedly-naked-as-she-claims-sexual-assault/articleshow/124715363.html",
            "https://wegotthiscovered.com/social-media/that-was-my-only-way-to-make-money-doordash-fired-woman-days-after-she-reported-being-sexually-harassed-by-customer/",
            "https://perezhilton.com/doordash-driver-fired-after-accusing-customer-of-sexual-assault/",
            "https://www.freepressjournal.in/viral/doordash-driver-livie-henderson-fired-after-reporting-sexual-assault-incident-during-delivery-in-new-york-video",
            "https://www.kgns.tv/2025/11/18/doordash-driver-charged-after-recording-posting-video-nude-customer-police-say/",
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
