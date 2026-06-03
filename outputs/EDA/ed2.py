import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ── Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_DIR, "constituency_level_results.csv")
PLOTS_DIR = os.path.join(SCRIPT_DIR, "plots", "ed2")
os.makedirs(PLOTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150, "savefig.bbox": "tight"})

print("Loading data for ed2...")
df = pd.read_csv(DATA_PATH)

def save(fig, name):
    path = os.path.join(PLOTS_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"Saved: {name}")

# =============================================================================
# 1. Histogram of µ (all countries) - Overall competitiveness distribution
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 6))
sm_clean = df["specific_margin"].dropna()
sns.histplot(sm_clean[sm_clean <= 1.0], bins=60, kde=True, color="mediumpurple", ax=ax)
ax.axvline(sm_clean.median(), color="black", ls="--", label=f"Median = {sm_clean.median():.3f}")
ax.set_title("Overall Competitiveness Distribution (Specific Margin \u03bc)")
ax.set_xlabel("Specific Margin (Winner vs Runner-up share)")
ax.set_ylabel("Frequency")
ax.legend()
save(fig, "01_histogram_mu_all_countries.png")

# =============================================================================
# 2. Boxplot of µ per country - Which countries are outliers
# =============================================================================
# Order by median specific margin
order = df.groupby('ctr_n')['specific_margin'].median().sort_values().index

# Limit to countries with enough data (e.g. top 25 by volume or just all if < 50)
top_ctrs = df['ctr_n'].value_counts().head(25).index
df_box = df[df['ctr_n'].isin(top_ctrs)]
order_box = [c for c in order if c in top_ctrs]

fig, ax = plt.subplots(figsize=(12, 10))
sns.boxplot(data=df_box, y='ctr_n', x='specific_margin', order=order_box, ax=ax, 
            palette="coolwarm", fliersize=2)
ax.set_title("Competitiveness (\u03bc) per Country (Ordered by Median)")
ax.set_xlabel("Specific Margin (\u03bc)")
ax.set_ylabel("")
save(fig, "02_boxplot_mu_per_country.png")

# =============================================================================
# 3. Bar chart — rows per country - Dataset size per country
# =============================================================================
rows_per_ctr = df['ctr_n'].value_counts()
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x=rows_per_ctr.values, y=rows_per_ctr.index, palette="viridis", ax=ax)
ax.set_title("Dataset Size per Country (Total Rows)")
ax.set_xlabel("Number of Rows (Constituency Elections)")
ax.set_ylabel("")
save(fig, "03_bar_rows_per_country.png")

# =============================================================================
# 4. Turnout distribution g(T) — 6 countries overlaid
# =============================================================================
# Select 6 diverse/top countries for overlaying
top6 = df['ctr_n'].value_counts().head(6).index
df_top6 = df[df['ctr_n'].isin(top6)].copy()

fig, ax = plt.subplots(figsize=(12, 6))
# Using log(vv1) for plotting the turnout curve g(T) as valid votes vary wildly
df_top6['log_vv1'] = np.log1p(df_top6['vv1'])

for country in top6:
    sns.kdeplot(data=df_top6[df_top6['ctr_n'] == country], x='log_vv1', label=country, linewidth=2, ax=ax)

ax.set_title("Turnout Distribution g(T) - 6 Countries Overlaid")
ax.set_xlabel("Log(1 + Valid Votes)")
ax.set_ylabel("Density")
ax.legend(title="Country")
save(fig, "04_turnout_distribution_g_T.png")

# =============================================================================
# 5. µ over time (pooled) - Is democracy getting more competitive?
# =============================================================================
yearly_mu = df.groupby('yr')['specific_margin'].median()
yearly_mu_mean = df.groupby('yr')['specific_margin'].mean()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(yearly_mu.index, yearly_mu.values, label="Median \u03bc", color="darkorchid", linewidth=2)
ax.plot(yearly_mu_mean.index, yearly_mu_mean.values, label="Mean \u03bc", color="teal", linestyle="--")

# Add a trend line for median
z = np.polyfit(yearly_mu.index, yearly_mu.values, 1)
p = np.poly1d(z)
ax.plot(yearly_mu.index, p(yearly_mu.index), "r:", label=f"Trend: {'decreasing (more competitive)' if z[0]<0 else 'increasing (less competitive)'}", linewidth=2)

ax.set_title("Competitiveness (\u03bc) Over Time - Is democracy getting more competitive?")
ax.set_xlabel("Year")
ax.set_ylabel("Specific Margin (\u03bc) [Lower = More Competitive]")
ax.legend()
save(fig, "05_mu_over_time.png")

print("ed2.py complete!")
