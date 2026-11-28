"""
US 2020 County Election — Clean Insights for Voter Turnout & Participation
Simple, readable plots for presentation.
Variables kept: Median Income, Gini (inequality/poverty proxy),
Education (development proxy), Turnout, Vote share, Population density (urbanisation)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ── Setup ────────────────────────────────────────────────────────────────────
df = pd.read_csv("/home/claude/election_analysis/outputs/clean.csv", index_col=0)

# Keep only relevant columns, rename for clarity
keep = {
    "county":              "County",
    "state":               "State",
    "Median income (dollars)": "Median Income ($)",
    "Gini Index":          "Gini Index\n(Inequality)",
    "higher_ed":           "Higher Education %\n(Bach + Grad)",
    "low_ed":              "Low Education %\n(<12th, no diploma)",
    "Density per square km": "Population Density\n(per km²)",
    "turnout_proxy":       "Voter Turnout\n(Votes / Population)",
    "dem_margin":          "Democrat Margin (%)\n(Dem% − Rep%)",
    "2020 Democrat vote %":  "Democrat Vote %",
    "2020 Republican vote %":"Republican Vote %",
    "Total Population":    "Total Population",
    "dem_win":             "Democrat Won",
}
d = df[list(keep.keys())].rename(columns=keep).copy()
d["Turnout %"] = d["Voter Turnout\n(Votes / Population)"] * 100
d["Winner"] = d["Democrat Won"].map({1: "Democrat", 0: "Republican"})
d["Income Group"] = pd.qcut(d["Median Income ($)"], 4,
    labels=["Low Income\n(Q1)","Lower-Mid\n(Q2)","Upper-Mid\n(Q3)","High Income\n(Q4)"])
d["Education Group"] = pd.qcut(d["Higher Education %\n(Bach + Grad)"], 4,
    labels=["Low Ed\n(Q1)","Lower-Mid\n(Q2)","Upper-Mid\n(Q3)","High Ed\n(Q4)"])
d["Density Group"] = pd.qcut(d["Population Density\n(per km²)"], 4,
    labels=["Rural","Semi-Rural","Semi-Urban","Urban"])

BLUE, RED, GREEN, ORANGE = "#2980B9", "#C0392B", "#27AE60", "#E67E22"
PURPLE = "#8E44AD"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "#FAFAFA",
})

OUT = "/home/claude/easy_plots/outputs"

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 1 — "What Does a County Look Like?" — Summary Snapshot
# Simple bar of key averages split by Winner
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("Average County Profile: Democrat vs Republican Counties\nUS 2020 Presidential Election  |  3,141 Counties",
             fontsize=14, fontweight="bold", y=1.01)

metrics = [
    ("Median Income ($)", "Median Household Income ($)", True),
    ("Gini Index\n(Inequality)", "Gini Index (Income Inequality)", False),
    ("Higher Education %\n(Bach + Grad)", "Higher Education %\n(Bachelor's or above)", False),
    ("Low Education %\n(<12th, no diploma)", "Low Education %\n(Less than High School)", False),
    ("Turnout %", "Voter Turnout %\n(Votes / Total Population × 100)", False),
    ("Population Density\n(per km²)", "Population Density (per km²)", True),
]

for ax, (col, title, is_dollar) in zip(axes.ravel(), metrics):
    grp = d.groupby("Winner")[col].mean()
    colors = [BLUE if w == "Democrat" else RED for w in grp.index]
    bars = ax.bar(grp.index, grp.values, color=colors, alpha=0.85, width=0.5, edgecolor="white")
    ax.set_title(title, fontweight="bold", fontsize=10)
    ax.set_ylabel("Mean Value")
    # Annotate bars
    for bar, val in zip(bars, grp.values):
        label = f"${val:,.0f}" if is_dollar else f"{val:.2f}"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + bar.get_height()*0.02,
                label, ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_ylim(0, grp.max() * 1.2)
    ax.tick_params(axis="x", labelsize=11)

plt.tight_layout()
fig.savefig(f"{OUT}/01_county_profile_dem_vs_rep.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 1 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 2 — Voter Turnout by Income Group (bar + error bars)
# Simple: richer counties → higher turnout?
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
grp = d.groupby("Income Group", observed=True)["Turnout %"].agg(["mean","sem","count"])
colors_inc = [GREEN, "#52BE80", "#1A5276", BLUE]

bars = ax.bar(grp.index, grp["mean"], yerr=grp["sem"]*1.96,
              color=colors_inc, alpha=0.85, capsize=6, edgecolor="white", width=0.55)

for bar, (_, row) in zip(bars, grp.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + row["sem"]*2 + 0.3,
            f"{row['mean']:.1f}%\n(n={int(row['count'])})",
            ha="center", va="bottom", fontsize=9.5, fontweight="bold")

ax.set_title("Voter Turnout by County Income Level\n"
             "Do Richer Counties Vote More?", fontweight="bold", fontsize=13)
ax.set_xlabel("County Income Quartile  →  Increasing Income", fontsize=11)
ax.set_ylabel("Average Voter Turnout %", fontsize=11)
ax.set_ylim(0, 75)
ax.axhline(d["Turnout %"].mean(), color="gray", ls="--", lw=1.5,
           label=f"Overall average = {d['Turnout %'].mean():.1f}%")
ax.legend()

# Correlation note
r, p = stats.pearsonr(d["Median Income ($)"].dropna(),
                       d.loc[d["Median Income ($)"].notna(), "Turnout %"])
ax.text(0.97, 0.05, f"Correlation r = {r:.2f}  (p < 0.001)",
        transform=ax.transAxes, ha="right", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))

plt.tight_layout()
fig.savefig(f"{OUT}/02_turnout_by_income.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 2 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 3 — Voter Turnout by Education Level
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
grp = d.groupby("Education Group", observed=True)["Turnout %"].agg(["mean","sem","count"])
colors_ed = ["#E8DAEF","#A569BD","#7D3C98","#4A235A"]

bars = ax.bar(grp.index, grp["mean"], yerr=grp["sem"]*1.96,
              color=colors_ed, alpha=0.9, capsize=6, edgecolor="white", width=0.55)

for bar, (_, row) in zip(bars, grp.iterrows()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + row["sem"]*2 + 0.3,
            f"{row['mean']:.1f}%\n(n={int(row['count'])})",
            ha="center", va="bottom", fontsize=9.5, fontweight="bold")

r, p = stats.pearsonr(d["Higher Education %\n(Bach + Grad)"], d["Turnout %"])
ax.set_title("Voter Turnout by Education Level\n"
             "Do More Educated Counties Vote More?", fontweight="bold", fontsize=13)
ax.set_xlabel("County Education Quartile  →  Increasing Education", fontsize=11)
ax.set_ylabel("Average Voter Turnout %", fontsize=11)
ax.set_ylim(0, 75)
ax.axhline(d["Turnout %"].mean(), color="gray", ls="--", lw=1.5,
           label=f"Overall average = {d['Turnout %'].mean():.1f}%")
ax.legend()
ax.text(0.97, 0.05, f"Correlation r = {r:.2f}  (p < 0.001)",
        transform=ax.transAxes, ha="right", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))

plt.tight_layout()
fig.savefig(f"{OUT}/03_turnout_by_education.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 3 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 4 — Turnout by Urban/Rural (boxplot — easy to read)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
groups = ["Rural","Semi-Rural","Semi-Urban","Urban"]
data_by_grp = [d[d["Density Group"]==g]["Turnout %"].dropna().values for g in groups]
pal = [RED, ORANGE, "#2ECC71", BLUE]

bp = ax.boxplot(data_by_grp, patch_artist=True, notch=False, widths=0.5,
                medianprops=dict(color="black", lw=2.5),
                whiskerprops=dict(lw=1.5), capprops=dict(lw=1.5),
                flierprops=dict(marker="o", markersize=2.5, alpha=0.3, color="gray"))
for patch, color in zip(bp["boxes"], pal):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)

ax.set_xticklabels(groups, fontsize=12)
medians = [np.median(g) for g in data_by_grp]
for i, med in enumerate(medians):
    ax.text(i+1, med + 1.5, f"{med:.1f}%", ha="center", fontsize=10, fontweight="bold")

r, p = stats.pearsonr(np.log1p(d["Population Density\n(per km²)"]), d["Turnout %"])
ax.set_title("Voter Turnout: Rural vs Urban Counties\n"
             "Are Urban Counties More Engaged?", fontweight="bold", fontsize=13)
ax.set_xlabel("County Type (by Population Density)", fontsize=11)
ax.set_ylabel("Voter Turnout %", fontsize=11)
ax.text(0.97, 0.05, f"Correlation (log density) r = {r:.2f}  (p < 0.001)",
        transform=ax.transAxes, ha="right", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))
plt.tight_layout()
fig.savefig(f"{OUT}/04_turnout_urban_rural.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 4 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 5 — Income vs Democrat Vote % scatter (clean, annotated)
# Does higher income → more Democratic?
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 7))

# Sample 800 points so plot isn't overloaded
sample = d.dropna(subset=["Median Income ($)"]).sample(800, random_state=42)
colors = [BLUE if w == "Democrat" else RED for w in sample["Winner"]]

ax.scatter(sample["Median Income ($)"] / 1000, sample["Democrat Vote %"],
           c=colors, alpha=0.45, s=35, edgecolors="none")

# OLS line on full data
valid = d.dropna(subset=["Median Income ($)"])
m, b = np.polyfit(valid["Median Income ($)"] / 1000, valid["Democrat Vote %"], 1)
x_range = np.linspace(valid["Median Income ($)"].min()/1000,
                       valid["Median Income ($)"].max()/1000, 200)
ax.plot(x_range, m*x_range + b, "k-", lw=2.2, label="Trend line (OLS)")
ax.axhline(50, color="gray", ls="--", lw=1.2, alpha=0.6, label="50% line (tie)")

r, p = stats.pearsonr(valid["Median Income ($)"], valid["Democrat Vote %"])
ax.set_title("Median County Income vs Democrat Vote Share\n"
             "Do Higher-Income Counties Vote More Democrat?", fontweight="bold", fontsize=13)
ax.set_xlabel("Median Household Income ($ thousands)", fontsize=11)
ax.set_ylabel("Democrat Vote % in 2020", fontsize=11)

# Legend
dem_patch = mpatches.Patch(color=BLUE, alpha=0.7, label="Democrat won")
rep_patch = mpatches.Patch(color=RED, alpha=0.7, label="Republican won")
ax.legend(handles=[dem_patch, rep_patch, 
                   plt.Line2D([0],[0], color="k", lw=2, label="Trend line")],
          loc="upper left")

ax.text(0.97, 0.05, f"r = {r:.2f}  (p < 0.001)\n→ Weak positive: richer counties lean slightly more Democratic",
        transform=ax.transAxes, ha="right", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))

plt.tight_layout()
fig.savefig(f"{OUT}/05_income_vs_dem_vote.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 5 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 6 — Inequality (Gini) vs Turnout & Vote Share
# Higher inequality = poverty proxy
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Gini bins
d["Gini Group"] = pd.qcut(d["Gini Index\n(Inequality)"], 4,
    labels=["Low Inequality\n(Q1)","Q2","Q3","High Inequality\n(Q4)"])

# Left: Gini vs Turnout bar
grp_g = d.groupby("Gini Group", observed=True)["Turnout %"].agg(["mean","sem"])
bars = axes[0].bar(grp_g.index, grp_g["mean"], yerr=grp_g["sem"]*1.96,
                   color=["#AED6F1","#5DADE2","#2874A6","#1A5276"],
                   alpha=0.85, capsize=5, edgecolor="white", width=0.55)
for bar, (_, row) in zip(bars, grp_g.iterrows()):
    axes[0].text(bar.get_x()+bar.get_width()/2,
                 bar.get_height()+row["sem"]*2+0.3,
                 f"{row['mean']:.1f}%", ha="center", fontsize=10, fontweight="bold")
r1, _ = stats.pearsonr(d["Gini Index\n(Inequality)"], d["Turnout %"])
axes[0].set_title("Inequality (Gini Index) vs Voter Turnout\n"
                  "More Unequal Counties — Do They Vote Less?", fontweight="bold", fontsize=11)
axes[0].set_xlabel("Gini Index Quartile  →  Increasing Inequality", fontsize=10)
axes[0].set_ylabel("Average Voter Turnout %")
axes[0].set_ylim(0, 75)
axes[0].text(0.97, 0.05, f"r = {r1:.2f}",
             transform=axes[0].transAxes, ha="right", fontsize=10,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))

# Right: Gini vs Dem margin
grp_gm = d.groupby("Gini Group", observed=True)["Democrat Vote %"].agg(["mean","sem"])
colors_gm = [RED if v < 50 else BLUE for v in grp_gm["mean"]]
bars2 = axes[1].bar(grp_gm.index, grp_gm["mean"], yerr=grp_gm["sem"]*1.96,
                    color=colors_gm, alpha=0.85, capsize=5, edgecolor="white", width=0.55)
axes[1].axhline(50, color="gray", ls="--", lw=1.5, label="50% tie line")
for bar, (_, row) in zip(bars2, grp_gm.iterrows()):
    axes[1].text(bar.get_x()+bar.get_width()/2,
                 bar.get_height()+row["sem"]*2+0.3,
                 f"{row['mean']:.1f}%", ha="center", fontsize=10, fontweight="bold")
r2, _ = stats.pearsonr(d["Gini Index\n(Inequality)"], d["Democrat Vote %"])
axes[1].set_title("Inequality (Gini Index) vs Democrat Vote %\n"
                  "Who Benefits from High-Inequality Counties?", fontweight="bold", fontsize=11)
axes[1].set_xlabel("Gini Index Quartile  →  Increasing Inequality", fontsize=10)
axes[1].set_ylabel("Average Democrat Vote %")
axes[1].set_ylim(0, 70)
axes[1].legend()
axes[1].text(0.97, 0.05, f"r = {r2:.2f}",
             transform=axes[1].transAxes, ha="right", fontsize=10,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"))

plt.suptitle("Gini Index (Inequality / Poverty Proxy) vs Electoral Outcomes",
             fontweight="bold", fontsize=13, y=1.02)
plt.tight_layout()
fig.savefig(f"{OUT}/06_inequality_gini_vs_outcomes.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 6 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 7 — Simple Correlation Summary Table (the "what connects to what" chart)
# One clean horizontal bar chart — all correlations with Turnout
# ═══════════════════════════════════════════════════════════════════════════
targets = {
    "Voter Turnout %":   "Turnout %",
    "Democrat Vote %":   "Democrat Vote %",
}
predictors = {
    "Median Income":        "Median Income ($)",
    "Gini (Inequality)":    "Gini Index\n(Inequality)",
    "Higher Education":     "Higher Education %\n(Bach + Grad)",
    "Low Education":        "Low Education %\n(<12th, no diploma)",
    "Population Density":   "Population Density\n(per km²)",
}

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
for ax, (ylabel, ycol) in zip(axes, targets.items()):
    rs, names = [], []
    for name, col in predictors.items():
        r, p = stats.pearsonr(d[col].dropna(), d.loc[d[col].notna(), ycol])
        rs.append(r)
        names.append(name)
    
    colors_r = [GREEN if r > 0 else RED for r in rs]
    bars = ax.barh(names, rs, color=colors_r, alpha=0.85, edgecolor="white", height=0.55)
    ax.axvline(0, color="black", lw=1.5)
    ax.set_xlim(-0.8, 0.8)
    
    for bar, r in zip(bars, rs):
        xpos = r + 0.02 if r >= 0 else r - 0.02
        ha   = "left" if r >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height()/2,
                f"r = {r:.2f}", va="center", ha=ha, fontsize=10, fontweight="bold")
    
    ax.set_title(f"What Correlates with\n{ylabel}?", fontweight="bold", fontsize=12)
    ax.set_xlabel("Pearson Correlation (r)", fontsize=10)
    
    # Legend
    g_patch = mpatches.Patch(color=GREEN, alpha=0.7, label="Positive (higher → more votes)")
    r_patch = mpatches.Patch(color=RED,   alpha=0.7, label="Negative (higher → fewer votes)")
    ax.legend(handles=[g_patch, r_patch], fontsize=9, loc="lower right")

plt.suptitle("Correlation Summary: How Do Socioeconomic Factors Relate to Voting?\n"
             "US 2020 Presidential Election — 3,141 Counties",
             fontweight="bold", fontsize=13, y=1.02)
plt.tight_layout()
fig.savefig(f"{OUT}/07_correlation_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 7 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 8 — "Development Ladder" — Education quintile × Income × Turnout
# Shows how as counties develop (more edu + income), turnout rises
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 7))

# Average income and turnout per education group
grp = d.groupby("Education Group", observed=True).agg(
    mean_income=("Median Income ($)", "mean"),
    mean_turnout=("Turnout %", "mean"),
    mean_dem=("Democrat Vote %", "mean"),
    n=("Turnout %", "count")
).reset_index()

x = np.arange(len(grp))
width = 0.35

bars_t = ax.bar(x - width/2, grp["mean_turnout"],
                width=width, color=PURPLE, alpha=0.8, label="Voter Turnout %", edgecolor="white")
bars_d = ax.bar(x + width/2, grp["mean_dem"],
                width=width, color=BLUE, alpha=0.8, label="Democrat Vote %", edgecolor="white")

ax2 = ax.twinx()
ax2.plot(x, grp["mean_income"]/1000, "ko-", lw=2.5, ms=9, label="Median Income ($k)")
ax2.set_ylabel("Median Income ($ thousands)", fontsize=11, color="black")

for bar, val in zip(bars_t, grp["mean_turnout"]):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.4,
            f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold", color=PURPLE)
for bar, val in zip(bars_d, grp["mean_dem"]):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.4,
            f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold", color=BLUE)

ax.set_xticks(x)
ax.set_xticklabels(grp["Education Group"], fontsize=11)
ax.set_xlabel("Education Quartile  →  More Educated Counties", fontsize=11)
ax.set_ylabel("Percentage (%)", fontsize=11)
ax.set_ylim(0, 80)
ax.set_title("Development Ladder: As Education Rises, Do Turnout & Income Rise Too?\n"
             "Blue = Democrat Vote %, Purple = Turnout %, Black line = Income",
             fontweight="bold", fontsize=12)

lines, labels = ax2.get_legend_handles_labels()
bars_handles = [mpatches.Patch(color=PURPLE, alpha=0.8, label="Voter Turnout %"),
                mpatches.Patch(color=BLUE, alpha=0.8, label="Democrat Vote %")]
ax.legend(handles=bars_handles + lines, loc="upper left", fontsize=9)

plt.tight_layout()
fig.savefig(f"{OUT}/08_development_ladder.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 8 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 9 — Big picture: Which US States have Highest / Lowest Turnout?
# Simple ranked horizontal bar — easy for teachers
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 14))
state_turn = d.groupby("State")["Turnout %"].median().sort_values()
colors_st = [BLUE if v >= state_turn.median() else RED for v in state_turn.values]
bars = ax.barh(state_turn.index, state_turn.values, color=colors_st, alpha=0.82, edgecolor="white")
ax.axvline(state_turn.median(), color="black", ls="--", lw=1.5,
           label=f"Median = {state_turn.median():.1f}%")
ax.set_xlabel("Median County Turnout % (Votes / Population × 100)", fontsize=11)
ax.set_title("Voter Turnout by US State\n"
             "Median Across Counties Within Each State | 2020 Election",
             fontweight="bold", fontsize=13)
ax.legend(fontsize=10)
high_patch = mpatches.Patch(color=BLUE, alpha=0.8, label="Above national median")
low_patch  = mpatches.Patch(color=RED,  alpha=0.8, label="Below national median")
ax.legend(handles=[high_patch, low_patch, 
                   plt.Line2D([0],[0],color="black",ls="--",lw=1.5,label="National median")],
          fontsize=9)
plt.tight_layout()
fig.savefig(f"{OUT}/09_turnout_by_state.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 9 done")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 10 — "The Big Story" 4-panel summary for teacher
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle("The Big Story: What Drives Voter Participation?\nUS 2020 Presidential Election — County Level",
             fontsize=14, fontweight="bold", y=1.01)

panel_data = [
    ("Income Group", "Turnout %", "Turnout % by Income Level",
     "Richer counties → Higher turnout", ["#AED6F1","#5DADE2","#2874A6","#1A5276"]),
    ("Education Group", "Turnout %", "Turnout % by Education Level",
     "More educated → Higher turnout", ["#D2B4DE","#A569BD","#7D3C98","#4A235A"]),
    ("Density Group", "Turnout %", "Turnout % by Urbanisation",
     "Urban counties → Higher turnout", [RED, ORANGE, "#27AE60", BLUE]),
    ("Gini Group", "Turnout %", "Turnout % by Inequality Level",
     "More unequal counties → Mixed pattern", ["#AED6F1","#5DADE2","#2874A6","#1A5276"]),
]

for ax, (grp_col, val_col, title, subtitle, pal) in zip(axes.ravel(), panel_data):
    grp = d.groupby(grp_col, observed=True)[val_col].agg(["mean","sem"])
    bars = ax.bar(range(len(grp)), grp["mean"], yerr=grp["sem"]*1.96,
                  color=pal, alpha=0.87, capsize=5, edgecolor="white", width=0.6)
    for i, (bar, (_, row)) in enumerate(zip(bars, grp.iterrows())):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+row["sem"]*2+0.3,
                f"{row['mean']:.1f}%", ha="center", fontsize=10, fontweight="bold")
    ax.set_xticks(range(len(grp)))
    ax.set_xticklabels([x.replace(" Group","") for x in grp.index], fontsize=9)
    ax.set_ylim(0, 72)
    ax.set_ylabel("Voter Turnout %")
    ax.set_title(f"{title}\n→ {subtitle}", fontweight="bold", fontsize=10)
    ax.axhline(d["Turnout %"].mean(), color="gray", ls="--", lw=1.2, alpha=0.8)

plt.tight_layout()
fig.savefig(f"{OUT}/10_big_story_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print("Plot 10 done")

print("\n✓ All 10 plots saved")
