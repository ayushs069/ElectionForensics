import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_DIR, "constituency_level_results.csv")
PLOTS_DIR = os.path.join(SCRIPT_DIR, "plots", "ed1")
os.makedirs(PLOTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 120, "savefig.bbox": "tight"})

print("Loading data for ed1...")
df = pd.read_csv(DATA_PATH)

def save(fig, name):
    path = os.path.join(PLOTS_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved: {name}")

# 1. Total Countries Plot (Bar chart of top countries by constituency count to represent total countries)
# Or just a simple plot showing the count of unique countries
fig, ax = plt.subplots(figsize=(8, 4))
ax.text(0.5, 0.5, f"Total Unique Countries:\n{df['ctr_n'].nunique()}", 
        fontsize=24, ha='center', va='center', fontweight='bold', color='navy')
ax.axis('off')
save(fig, "01_total_countries.png")

# 2. Total Constituencies Over Time (Country-wise - Top 5 for clarity)
top5_ctrs = df['ctr_n'].value_counts().head(5).index
df_top5 = df[df['ctr_n'].isin(top5_ctrs)]
cst_over_time = df_top5.groupby(['yr', 'ctr_n'])['cst_n'].nunique().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(12, 6))
cst_over_time.plot(ax=ax, linewidth=2)
ax.set_title("Total Unique Constituencies Over Time (Top 5 Countries)")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Constituencies")
save(fig, "02_constituencies_over_time_countrywise.png")

# 3. Election Years (Start to Present) Histogram
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df['yr'], bins=int(df['yr'].max() - df['yr'].min()), color="steelblue", ax=ax)
ax.set_title(f"Election Records from {df['yr'].min()} to {df['yr'].max()}")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Records")
save(fig, "03_election_years_distribution.png")

# 4. Basic Plot: Valid Votes (Turnout) Over Time (Global Average)
avg_vv = df.groupby('yr')['vv1'].mean()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(avg_vv.index, avg_vv.values, color="forestgreen", marker="o", markersize=3)
ax.set_title("Global Average Valid Votes per Constituency Over Time")
ax.set_xlabel("Year")
ax.set_ylabel("Average Valid Votes")
save(fig, "04_avg_valid_votes_over_time.png")

print("ed1.py complete!")
