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

import os
os.environ["MATPLOTLIBRC"] = os.path.join(os.getcwd(), ".mplconfig")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
sns.set_context("talk")  

weekly.index = weekly.index.astype(str)

plt.figure(figsize=(12,6))

plt.plot(weekly.index, weekly["sexual_score"], 
         marker="o", linewidth=3, color="#d62728", label="Sexual Allegation")

plt.plot(weekly.index, weekly["surveillance_score"], 
         marker="o", linewidth=3, color="#ff7f0e", label="Surveillance Crime")

plt.plot(weekly.index, weekly["legal_score"], 
         marker="o", linewidth=3, color="#1f77b4", label="Legal Process")

plt.axvline(x="2025-11-10/2025-11-16", 
            linestyle="--", color="gray", alpha=0.7)

plt.text(4, max(weekly["legal_score"]) * 0.9,
         "Institutional Turning Point",
         fontsize=12, color="gray")

plt.xticks(rotation=45, ha="right")
plt.ylabel("Frame Frequency")
plt.title("Narrative Shift: From Moral Accusation to Legal Accountability")

plt.legend(frameon=False)
plt.tight_layout()

plt.savefig("frame_shift_plot_clean.png", dpi=300)
print("Saved improved plot to frame_shift_plot_clean.png")