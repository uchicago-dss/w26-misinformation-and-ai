import pandas as pd

# 1. Load data
df = pd.read_csv("articles.csv")

# 2. Keep successful articles
df = df[df["status"] == "ok"]
df = df[df["published_date"] != ""]

df["published_date"] = pd.to_datetime(df["published_date"])
df["week"] = df["published_date"].dt.to_period("W")

# 3. Define frames
SEXUAL = ["sexual assault", "assault occurred", "harassment"]
SURVEILLANCE = ["unlawful surveillance", "surveillance degree", "surveillance dissemination"]
LEGAL = ["court", "felony", "charges", "appear court"]

def count_frame(text, keywords):
    text = str(text).lower()
    return sum(text.count(k) for k in keywords)

df["sexual_score"] = df["text"].apply(lambda x: count_frame(x, SEXUAL))
df["surveillance_score"] = df["text"].apply(lambda x: count_frame(x, SURVEILLANCE))
df["legal_score"] = df["text"].apply(lambda x: count_frame(x, LEGAL))

# 4. Aggregate by week
weekly = df.groupby("week")[["sexual_score","surveillance_score","legal_score"]].sum()

print("\nFrame Frequency by Week:\n")
print(weekly)

# Optional: save for slides
weekly.to_csv("frame_by_week.csv")