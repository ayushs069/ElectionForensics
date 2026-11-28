"""
02_eda.py — Exploratory Data Analysis
US 2020 County Election + Socioeconomic Dataset
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

CLEAN = "/home/claude/election_analysis/outputs/clean.csv"
PLOTS = "/home/claude/election_analysis/plots"

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
BLUE, RED = "#3674B5", "#C0392B"

df = pd.read_csv(CLEAN, index_col=0)
print(f"Loaded {len(df)} counties, {len(df.columns)} cols")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 1 — Distribution of Dem margin (outcome variable)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].hist(df["dem_margin"], bins=60, color=BLUE, alpha=0.8, edgecolor="white")
axes[0].axvline(0, color="black", lw=1.5, ls="--", label="50-50")
axes[0].axvline(df["dem_margin"].mean(), color=RED, lw=1.5, ls="-",
                label=f"Mean = {df['dem_margin'].mean():.1f}pp")
axes[0].set_title("Distribution of Dem Margin Across US Counties", fontweight="bold")
axes[0].set_xlabel("Democrat % − Republican %")
axes[0].set_ylabel("Number of Counties")
axes[0].legend()

dem_by_state = df.groupby("state")["dem_win"].mean().sort_values()
colors_bar = [BLUE if v > 0.5 else RED for v in dem_by_state]
axes[1].barh(dem_by_state.index, dem_by_state.values * 100, color=colors_bar, alpha=0.85)
axes[1].axvline(50, color="black", lw=1, ls="--")
axes[1].set_title("% Counties Won by Democrats by State", fontweight="bold")
axes[1].set_xlabel("% of Counties (Dem win)")
axes[1].set_xlim(0, 100)
plt.tight_layout()
fig.savefig(f"{PLOTS}/fig1_outcome_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 1 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 2 — Turnout proxy distribution
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(df["turnout_proxy"], bins=60, color="#2E86AB", alpha=0.8, edgecolor="white")
ax.axvline(df["turnout_proxy"].median(), color=RED, ls="--", lw=1.8,
           label=f"Median = {df['turnout_proxy'].median():.2f}")
ax.set_title("Turnout Proxy (Votes / Total Population) Distribution", fontweight="bold")
ax.set_xlabel("Votes / Population")
ax.set_ylabel("Number of Counties")
ax.legend()
plt.tight_layout()
fig.savefig(f"{PLOTS}/fig2_turnout_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 2 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 3 — Correlation heatmap (key socioeconomic × outcomes)
# ─────────────────────────────────────────────────────────────────────────────
key_cols = {
    "dem_margin": "Dem Margin",
    "turnout_proxy": "Turnout",
    "higher_ed": "Higher Edu %",
    "low_ed": "Low Edu %",
    "log_median_income": "Log Median Income",
    "Gini Index": "Gini Index",
    "log_density": "Log Pop Density",
    "diversity_idx": "Diversity Index",
    "NH-White percentage": "White %",
    "NH-Black percentage": "Black %",
    "Hispanic or Latino percentage": "Hispanic %",
    "Percentage engaged in Management, business, science, and arts occupations": "Mgmt/Prof Occ %",
    "Percentage engaged in Service Occupations": "Service Occ %",
    "Percentage engaged in Resources and Construction": "Resources/Constr %",
}
sub = df[list(key_cols.keys())].rename(columns=key_cols)
corr = sub.corr()

fig, ax = plt.subplots(figsize=(13, 11))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, square=True, linewidths=0.5, ax=ax,
            annot_kws={"size": 8}, vmin=-1, vmax=1)
ax.set_title("Correlation Matrix: Socioeconomic Variables × Electoral Outcomes", 
             fontweight="bold", pad=15)
plt.tight_layout()
fig.savefig(f"{PLOTS}/fig3_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 3 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 4 — Income vs Dem Margin scatter (H1.1)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, xcol, xlabel in zip(
    axes,
    ["log_median_income", "Gini Index"],
    ["Log Median Income", "Gini Index (Inequality)"]
):
    r, p = stats.pearsonr(df[xcol].dropna(), df.loc[df[xcol].notna(), "dem_margin"])
    colors = [BLUE if v > 0 else RED for v in df["dem_margin"]]
    ax.scatter(df[xcol], df["dem_margin"], c=colors, alpha=0.25, s=15)
    # OLS line
    m, b = np.polyfit(df[xcol].dropna(), df.loc[df[xcol].notna(), "dem_margin"], 1)
    x_range = np.linspace(df[xcol].min(), df[xcol].max(), 100)
    ax.plot(x_range, m * x_range + b, color="black", lw=1.8)
    ax.axhline(0, color="gray", ls="--", lw=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Democrat Margin (%)")
    ax.set_title(f"{xlabel} vs Dem Margin\nr = {r:.3f}, p {'< 0.001' if p < 0.001 else f'= {p:.3f}'}", 
                 fontweight="bold")

plt.tight_layout()
fig.savefig(f"{PLOTS}/fig4_income_gini_vs_margin.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 4 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 5 — Education vs Dem Margin (H1.2)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, xcol, xlabel, color in zip(
    axes,
    ["higher_ed", "low_ed"],
    ["Higher Education % (Bach + Grad)", "Low Education % (<12th, no diploma)"],
    [BLUE, RED]
):
    r, p = stats.pearsonr(df[xcol], df["dem_margin"])
    ax.scatter(df[xcol], df["dem_margin"], c=color, alpha=0.22, s=15)
    m, b = np.polyfit(df[xcol], df["dem_margin"], 1)
    x_range = np.linspace(df[xcol].min(), df[xcol].max(), 100)
    ax.plot(x_range, m * x_range + b, color="black", lw=1.8)
    ax.axhline(0, color="gray", ls="--", lw=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Democrat Margin (%)")
    ax.set_title(f"{xlabel}\nvs Dem Margin  r = {r:.3f}", fontweight="bold")

plt.tight_layout()
fig.savefig(f"{PLOTS}/fig5_education_vs_margin.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 5 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 6 — Urban density vs Dem Margin (H1.3)
# ─────────────────────────────────────────────────────────────────────────────
# Bin counties into urban quartiles
df["density_quartile"] = pd.qcut(df["Density per square km"], 4,
                                  labels=["Q1 Rural","Q2 Semi-Rural","Q3 Semi-Urban","Q4 Urban"])

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Scatter
r, p = stats.pearsonr(df["log_density"], df["dem_margin"])
axes[0].scatter(df["log_density"], df["dem_margin"],
                c=[BLUE if v > 0 else RED for v in df["dem_margin"]],
                alpha=0.22, s=15)
m, b = np.polyfit(df["log_density"], df["dem_margin"], 1)
x_r = np.linspace(df["log_density"].min(), df["log_density"].max(), 100)
axes[0].plot(x_r, m * x_r + b, "k-", lw=1.8)
axes[0].axhline(0, color="gray", ls="--", lw=1)
axes[0].set_xlabel("Log Population Density (per km²)")
axes[0].set_ylabel("Dem Margin (%)")
axes[0].set_title(f"Urbanization vs Dem Margin\nr = {r:.3f}", fontweight="bold")

# Boxplot by quartile
q_data = [df[df["density_quartile"] == q]["dem_margin"].values
          for q in ["Q1 Rural","Q2 Semi-Rural","Q3 Semi-Urban","Q4 Urban"]]
bp = axes[1].boxplot(q_data, patch_artist=True, notch=True,
                      labels=["Q1\nRural","Q2\nSemi-Rural","Q3\nSemi-Urban","Q4\nUrban"])
for patch, color in zip(bp["boxes"], [RED, "#E67E22", "#27AE60", BLUE]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
axes[1].axhline(0, color="gray", ls="--", lw=1)
axes[1].set_ylabel("Dem Margin (%)")
axes[1].set_title("Dem Margin by Urbanization Quartile", fontweight="bold")

plt.tight_layout()
fig.savefig(f"{PLOTS}/fig6_urbanization_vs_margin.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 6 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 7 — Race / Diversity (H1.3 demographics)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(17, 6))
race_pairs = [
    ("NH-White percentage", "White % (non-Hispanic)", RED),
    ("NH-Black percentage", "Black % (non-Hispanic)", BLUE),
    ("Hispanic or Latino percentage", "Hispanic %", "#8E44AD"),
]
for ax, (col, label, color) in zip(axes, race_pairs):
    r, p = stats.pearsonr(df[col], df["dem_margin"])
    ax.scatter(df[col], df["dem_margin"], c=color, alpha=0.2, s=15)
    m, b = np.polyfit(df[col], df["dem_margin"], 1)
    x_r = np.linspace(df[col].min(), df[col].max(), 100)
    ax.plot(x_r, m * x_r + b, "k-", lw=1.8)
    ax.axhline(0, color="gray", ls="--", lw=1)
    ax.set_xlabel(label)
    ax.set_ylabel("Dem Margin (%)")
    ax.set_title(f"r = {r:.3f}", fontweight="bold")

plt.suptitle("Racial Composition vs Democrat Margin", fontweight="bold", y=1.02)
plt.tight_layout()
fig.savefig(f"{PLOTS}/fig7_race_vs_margin.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 7 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 8 — Occupation structure (H1 employment angle)
# ─────────────────────────────────────────────────────────────────────────────
occ_cols = {
    "Percentage engaged in Management, business, science, and arts occupations": "Mgmt/Prof",
    "Percentage engaged in Service Occupations": "Service",
    "Percentage engaged in Sales and Office": "Sales/Office",
    "Percentage engaged in Resources and Construction": "Resources/Constr",
    "Percentage engaged in Transportation": "Transport",
}
corrs_occ = {v: stats.pearsonr(df[k], df["dem_margin"])[0]
             for k, v in occ_cols.items()}
corrs_turn = {v: stats.pearsonr(df[k], df["turnout_proxy"])[0]
              for k, v in occ_cols.items()}

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
names = list(corrs_occ.keys())
vals_m = list(corrs_occ.values())
vals_t = list(corrs_turn.values())

colors_m = [BLUE if v > 0 else RED for v in vals_m]
colors_t = [BLUE if v > 0 else RED for v in vals_t]

axes[0].barh(names, vals_m, color=colors_m, alpha=0.8)
axes[0].axvline(0, color="black", lw=1)
axes[0].set_title("Occupation % → Dem Margin\n(Pearson r)", fontweight="bold")
axes[0].set_xlabel("Correlation r")

axes[1].barh(names, vals_t, color=colors_t, alpha=0.8)
axes[1].axvline(0, color="black", lw=1)
axes[1].set_title("Occupation % → Turnout\n(Pearson r)", fontweight="bold")
axes[1].set_xlabel("Correlation r")

plt.tight_layout()
fig.savefig(f"{PLOTS}/fig8_occupation_correlations.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 8 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 9 — Turnout vs socioeconomic vars
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 11))
turn_pairs = [
    ("log_median_income", "Log Median Income", "#2ECC71"),
    ("higher_ed", "Higher Education %", BLUE),
    ("log_density", "Log Population Density", "#E67E22"),
    ("diversity_idx", "Diversity Index", "#8E44AD"),
]
for ax, (col, label, color) in zip(axes.ravel(), turn_pairs):
    r, p = stats.pearsonr(df[col].dropna(), df.loc[df[col].notna(), "turnout_proxy"])
    ax.scatter(df[col], df["turnout_proxy"], c=color, alpha=0.2, s=15)
    valid = df[[col, "turnout_proxy"]].dropna()
    m, b = np.polyfit(valid[col], valid["turnout_proxy"], 1)
    x_r = np.linspace(valid[col].min(), valid[col].max(), 100)
    ax.plot(x_r, m * x_r + b, "k-", lw=1.8)
    ax.set_xlabel(label)
    ax.set_ylabel("Turnout Proxy")
    ax.set_title(f"{label} vs Turnout  r = {r:.3f}", fontweight="bold")

plt.suptitle("Socioeconomic Variables vs Voter Turnout (County Level)", 
             fontweight="bold", y=1.01)
plt.tight_layout()
fig.savefig(f"{PLOTS}/fig9_turnout_socioeconomic.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 9 saved")

print("\n✓ All EDA plots saved")
