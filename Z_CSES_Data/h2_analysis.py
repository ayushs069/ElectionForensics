"""
H2 Analysis: Economic Conditions → Electoral Outcomes
CSES IMD Dataset | Election-level aggregation | 1996-2016
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('/mnt/user-data/uploads/cses_clean.csv')

# Pre-processing
df = df[~df['education'].isin([6.0])]
df = df[df['income_quintile'] != 6.0]
df['turnout'] = df['turnout'].astype(float)
df['inflation_log'] = np.log1p(df['inflation_rate'].clip(lower=0))

# ── Aggregate to ELECTION level ──────────────────────────────
election_df = df.groupby(['country','election_year']).agg(
    turnout_rate       = ('turnout','mean'),
    incumbent_support  = ('voted_incumbent','mean'),
    gdp_growth         = ('gdp_growth_elec_year','first'),
    gdp_prev           = ('gdp_growth_prev_year','first'),
    gdp_pc             = ('gdp_per_capita','first'),
    unemployment       = ('unemployment_rate','first'),
    inflation          = ('inflation_rate','first'),
    inflation_log      = ('inflation_log','first'),
    n_resp             = ('turnout','count')
).reset_index()

election_df['turnout_pct']      = election_df['turnout_rate'] * 100
election_df['incumbent_pct']    = election_df['incumbent_support'] * 100

print(f"Election-level dataset: {election_df.shape}")
print(f"Elections with incumbent data: {election_df['incumbent_pct'].notna().sum()}")

BLUE  = "#2980B9"
RED   = "#C0392B"
GREEN = "#27AE60"
PURP  = "#8E44AD"
ORG   = "#E67E22"
OUT   = "/home/claude/h2_plots"

plt.rcParams.update({"axes.spines.top":False,"axes.spines.right":False,
                     "figure.facecolor":"white","axes.facecolor":"#FAFAFA"})

# ════════════════════════════════════════════════════════════
# H2 PLOT 1 — Correlation Summary (election level)
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("H2: How Do Economic Conditions Relate to Electoral Outcomes?\n"
             "Election-Level Analysis | ~230 Elections | 54 Countries",
             fontweight='bold', fontsize=13, y=1.01)

macro_vars = {
    'GDP Growth\n(Election Year)': 'gdp_growth',
    'GDP Growth\n(Previous Year)': 'gdp_prev',
    'GDP per Capita\n(PPP)':       'gdp_pc',
    'Unemployment\nRate':          'unemployment',
    'Inflation\n(Log)':            'inflation_log',
}

# vs Turnout rate
r_turn, n_turn, labels = [], [], []
for label, col in macro_vars.items():
    sub = election_df[[col,'turnout_pct']].dropna()
    r, p = stats.pearsonr(sub[col], sub['turnout_pct'])
    r_turn.append(r)
    labels.append(label)

colors_t = [GREEN if r > 0 else RED for r in r_turn]
bars = axes[0].barh(labels, r_turn, color=colors_t, alpha=0.85,
                    edgecolor='white', height=0.55)
axes[0].axvline(0, color='black', lw=1.5)
axes[0].set_xlim(-0.5, 0.5)
for bar, r in zip(bars, r_turn):
    xpos = r + 0.015 if r >= 0 else r - 0.015
    ha = 'left' if r >= 0 else 'right'
    axes[0].text(xpos, bar.get_y()+bar.get_height()/2,
                 f"r = {r:.3f}", va='center', fontsize=10, fontweight='bold')
axes[0].set_title("Economic Variables → Voter Turnout Rate", fontweight='bold')
axes[0].set_xlabel("Pearson r (Election Level)")

# vs Incumbent support
r_inc = []
for label, col in macro_vars.items():
    sub = election_df[[col,'incumbent_pct']].dropna()
    if len(sub) > 10:
        r, p = stats.pearsonr(sub[col], sub['incumbent_pct'])
    else:
        r = np.nan
    r_inc.append(r)

colors_i = [GREEN if (r and r > 0) else RED for r in r_inc]
bars2 = axes[1].barh(labels, r_inc, color=colors_i, alpha=0.85,
                     edgecolor='white', height=0.55)
axes[1].axvline(0, color='black', lw=1.5)
axes[1].set_xlim(-0.5, 0.5)
for bar, r in zip(bars2, r_inc):
    if r and not np.isnan(r):
        xpos = r + 0.015 if r >= 0 else r - 0.015
        ha = 'left' if r >= 0 else 'right'
        axes[1].text(xpos, bar.get_y()+bar.get_height()/2,
                     f"r = {r:.3f}", va='center', fontsize=10, fontweight='bold')
axes[1].set_title("Economic Variables → Incumbent Support Rate", fontweight='bold')
axes[1].set_xlabel("Pearson r (Election Level)")

plt.tight_layout()
fig.savefig(f"{OUT}/H2_01_economic_correlations.png", dpi=150, bbox_inches='tight')
plt.close()
print("H2 Plot 1 done")

# ════════════════════════════════════════════════════════════
# H2 PLOT 2 — 2×2 Scatter Grid
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle("H2: Economic Conditions vs Electoral Outcomes\n"
             "Each dot = one election | Trend line = OLS",
             fontweight='bold', fontsize=13, y=1.01)

panels = [
    ('gdp_growth',   'turnout_pct',    'GDP Growth (%) vs Voter Turnout',     BLUE,  'GDP Growth %',       'Turnout Rate %'),
    ('unemployment', 'turnout_pct',    'Unemployment vs Voter Turnout',        RED,   'Unemployment Rate %','Turnout Rate %'),
    ('inflation_log','turnout_pct',    'Inflation (Log) vs Voter Turnout',     ORG,   'Inflation (Log)',    'Turnout Rate %'),
    ('gdp_growth',   'incumbent_pct',  'GDP Growth vs Incumbent Support',      GREEN, 'GDP Growth %',       'Incumbent Support %'),
]

for ax, (xcol, ycol, title, color, xlabel, ylabel) in zip(axes.ravel(), panels):
    sub = election_df[[xcol, ycol, 'country']].dropna()
    if len(sub) < 5:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center',
                transform=ax.transAxes)
        ax.set_title(title, fontweight='bold')
        continue
    r, p = stats.pearsonr(sub[xcol], sub[ycol])
    ax.scatter(sub[xcol], sub[ycol], c=color, alpha=0.45, s=40, edgecolors='none')
    m, b = np.polyfit(sub[xcol], sub[ycol], 1)
    x_r = np.linspace(sub[xcol].min(), sub[xcol].max(), 100)
    ax.plot(x_r, m*x_r+b, 'k-', lw=2)
    # Label top 3 outliers
    sub['resid'] = (sub[ycol] - (m*sub[xcol]+b)).abs()
    top3 = sub.nlargest(3, 'resid')
    for _, row in top3.iterrows():
        ax.annotate(row['country'], (row[xcol], row[ycol]),
                    fontsize=7, alpha=0.8,
                    xytext=(4,4), textcoords='offset points')
    stars = '***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else ''))
    ax.set_title(title, fontweight='bold', fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.text(0.97, 0.05, f"r = {r:.3f}{stars}\nn = {len(sub)} elections",
            transform=ax.transAxes, ha='right', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))

plt.tight_layout()
fig.savefig(f"{OUT}/H2_02_scatter_grid.png", dpi=150, bbox_inches='tight')
plt.close()
print("H2 Plot 2 done")

# ════════════════════════════════════════════════════════════
# H2 PLOT 3 — "Economic Voting" GDP Quartile → Incumbent Support
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("H2: Economic Voting — Do Voters Reward/Punish the Government?\n"
             "Incumbent Support Rate by Economic Conditions",
             fontweight='bold', fontsize=13, y=1.01)

inc_sub = election_df.dropna(subset=['incumbent_pct'])

# GDP quartiles → incumbent support
inc_sub = inc_sub.copy()
inc_sub['gdp_q'] = pd.qcut(inc_sub['gdp_growth'], 4,
                            labels=['Q1\nWeak Growth','Q2','Q3','Q4\nStrong Growth'])
gdp_grp = inc_sub.groupby('gdp_q', observed=True)['incumbent_pct'].agg(['mean','sem','count'])
colors_g = ['#C0392B','#E67E22','#27AE60','#1A5276']
bars = axes[0].bar(gdp_grp.index, gdp_grp['mean'],
                   yerr=gdp_grp['sem']*1.96, color=colors_g,
                   alpha=0.85, capsize=5, edgecolor='white', width=0.6)
for bar, (_, row) in zip(bars, gdp_grp.iterrows()):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+row['sem']*2+0.5,
                 f"{row['mean']:.1f}%\n(n={int(row['count'])})",
                 ha='center', fontsize=9.5, fontweight='bold')
axes[0].set_title("GDP Growth Quartile → Incumbent Support\n"
                  "Better economy → More support for incumbent?",
                  fontweight='bold')
axes[0].set_xlabel("GDP Growth Quartile →  Increasing Growth")
axes[0].set_ylabel("Mean Incumbent Support %")
axes[0].set_ylim(0, 60)

# Unemployment quartiles → incumbent support
inc_sub['unemp_q'] = pd.qcut(inc_sub['unemployment'], 4,
                              labels=['Q1\nLow Unemp','Q2','Q3','Q4\nHigh Unemp'])
unemp_grp = inc_sub.groupby('unemp_q', observed=True)['incumbent_pct'].agg(['mean','sem','count'])
colors_u = ['#1A5276','#27AE60','#E67E22','#C0392B']
bars2 = axes[1].bar(unemp_grp.index, unemp_grp['mean'],
                    yerr=unemp_grp['sem']*1.96, color=colors_u,
                    alpha=0.85, capsize=5, edgecolor='white', width=0.6)
for bar, (_, row) in zip(bars2, unemp_grp.iterrows()):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+row['sem']*2+0.5,
                 f"{row['mean']:.1f}%\n(n={int(row['count'])})",
                 ha='center', fontsize=9.5, fontweight='bold')
axes[1].set_title("Unemployment Quartile → Incumbent Support\n"
                  "Higher unemployment → Less support for incumbent?",
                  fontweight='bold')
axes[1].set_xlabel("Unemployment Rate Quartile →  Increasing Unemployment")
axes[1].set_ylabel("Mean Incumbent Support %")
axes[1].set_ylim(0, 60)

plt.tight_layout()
fig.savefig(f"{OUT}/H2_03_economic_voting.png", dpi=150, bbox_inches='tight')
plt.close()
print("H2 Plot 3 done")

# ════════════════════════════════════════════════════════════
# H2 PLOT 4 — Turnout over time + GDP overlay
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 6))
yr_turn = election_df.groupby('election_year').agg(
    turnout_mean=('turnout_pct','mean'),
    gdp_mean=('gdp_growth','mean')).reset_index()

ax2 = ax.twinx()
l1, = ax.plot(yr_turn['election_year'], yr_turn['turnout_mean'],
              'bo-', lw=2.5, ms=8, label='Avg Turnout % (left)')
l2, = ax2.plot(yr_turn['election_year'], yr_turn['gdp_mean'],
               'g^--', lw=2, ms=7, label='Avg GDP Growth % (right)', alpha=0.8)
for _, row in yr_turn.iterrows():
    ax.annotate(f"{row['turnout_mean']:.1f}%", (row['election_year'], row['turnout_mean']),
                textcoords='offset points', xytext=(0,8), fontsize=8, color=BLUE)

ax.set_xlabel("Election Year", fontsize=11)
ax.set_ylabel("Mean Voter Turnout %", fontsize=11, color=BLUE)
ax2.set_ylabel("Mean GDP Growth %", fontsize=11, color=GREEN)
ax.set_title("H2: Voter Turnout and GDP Growth Over Time (1996–2016)\n"
             "Does economic performance track with electoral participation?",
             fontweight='bold', fontsize=12)
ax.legend(handles=[l1, l2], loc='lower left')
plt.tight_layout()
fig.savefig(f"{OUT}/H2_04_turnout_gdp_over_time.png", dpi=150, bbox_inches='tight')
plt.close()
print("H2 Plot 4 done")

# ════════════════════════════════════════════════════════════
# H2 PLOT 5 — Inflation quartile → Turnout + Incumbent
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("H2: Does Inflation Affect Voter Behaviour?\n"
             "Inflation Quartile vs Turnout and Incumbent Support",
             fontweight='bold', fontsize=13, y=1.01)

election_df['inf_q'] = pd.qcut(election_df['inflation'], 4,
                                labels=['Q1\nLow','Q2','Q3','Q4\nHigh'])

# Turnout
inf_t = election_df.groupby('inf_q', observed=True)['turnout_pct'].agg(['mean','sem'])
colors_if = ['#AED6F1','#5DADE2','#E67E22','#C0392B']
bars = axes[0].bar(inf_t.index, inf_t['mean'], yerr=inf_t['sem']*1.96,
                   color=colors_if, alpha=0.85, capsize=5, edgecolor='white', width=0.6)
for bar, (_, row) in zip(bars, inf_t.iterrows()):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+row['sem']*2+0.3,
                 f"{row['mean']:.1f}%", ha='center', fontsize=11, fontweight='bold')
axes[0].set_title("Inflation Quartile → Voter Turnout", fontweight='bold')
axes[0].set_xlabel("Inflation Quartile →  Increasing Inflation")
axes[0].set_ylabel("Mean Turnout %")
axes[0].set_ylim(0, 100)

# Incumbent
inc_sub2 = election_df.dropna(subset=['incumbent_pct']).copy()
inc_sub2['inf_q2'] = pd.qcut(inc_sub2['inflation'], 4,
                              labels=['Q1\nLow','Q2','Q3','Q4\nHigh'])
inf_i = inc_sub2.groupby('inf_q2', observed=True)['incumbent_pct'].agg(['mean','sem','count'])
bars2 = axes[1].bar(inf_i.index, inf_i['mean'], yerr=inf_i['sem']*1.96,
                    color=colors_if, alpha=0.85, capsize=5, edgecolor='white', width=0.6)
for bar, (_, row) in zip(bars2, inf_i.iterrows()):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+row['sem']*2+0.3,
                 f"{row['mean']:.1f}%\n(n={int(row['count'])})",
                 ha='center', fontsize=9.5, fontweight='bold')
axes[1].set_title("Inflation Quartile → Incumbent Support\n"
                  "Do voters punish governments during high inflation?",
                  fontweight='bold')
axes[1].set_xlabel("Inflation Quartile →  Increasing Inflation")
axes[1].set_ylabel("Mean Incumbent Support %")
axes[1].set_ylim(0, 60)

plt.tight_layout()
fig.savefig(f"{OUT}/H2_05_inflation_effects.png", dpi=150, bbox_inches='tight')
plt.close()
print("H2 Plot 5 done")

# ════════════════════════════════════════════════════════════
# H2 PLOT 6 — GDP per capita vs Turnout (development proxy)
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 7))
sub = election_df[['gdp_pc','turnout_pct','country','election_year']].dropna()
r, p = stats.pearsonr(sub['gdp_pc'], sub['turnout_pct'])
ax.scatter(sub['gdp_pc']/1000, sub['turnout_pct'],
           c=BLUE, alpha=0.4, s=45, edgecolors='none')
m, b = np.polyfit(sub['gdp_pc'], sub['turnout_pct'], 1)
x_r = np.linspace(sub['gdp_pc'].min(), sub['gdp_pc'].max(), 200)
ax.plot(x_r/1000, m*x_r+b, 'k-', lw=2.2)
stars = '***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else ''))
ax.set_title("H2: GDP per Capita vs Voter Turnout\n"
             "Do Wealthier Countries Vote More?",
             fontweight='bold', fontsize=13)
ax.set_xlabel("GDP per Capita PPP ($ thousands)", fontsize=11)
ax.set_ylabel("Voter Turnout Rate %", fontsize=11)
ax.text(0.97, 0.05,
        f"r = {r:.3f}{stars}  (n={len(sub)} elections)",
        transform=ax.transAxes, ha='right', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))
plt.tight_layout()
fig.savefig(f"{OUT}/H2_06_gdppc_vs_turnout.png", dpi=150, bbox_inches='tight')
plt.close()
print("H2 Plot 6 done")

# Save H2 correlation table
corr_rows = []
for label, col in macro_vars.items():
    sub_t = election_df[[col,'turnout_pct']].dropna()
    sub_i = election_df[[col,'incumbent_pct']].dropna()
    r_t, p_t = stats.pearsonr(sub_t[col], sub_t['turnout_pct']) if len(sub_t)>5 else (np.nan,np.nan)
    r_i, p_i = stats.pearsonr(sub_i[col], sub_i['incumbent_pct']) if len(sub_i)>5 else (np.nan,np.nan)
    corr_rows.append({
        'Variable': label.replace('\n',' '),
        'r vs Turnout': round(r_t,4), 'p vs Turnout': round(p_t,4),
        'r vs Incumbent': round(r_i,4), 'p vs Incumbent': round(p_i,4)
    })
pd.DataFrame(corr_rows).to_csv("/home/claude/outputs/H2_correlations.csv", index=False)
election_df.to_csv("/home/claude/outputs/election_level_data.csv", index=False)

print("\n✓ All H2 plots saved to /home/claude/h2_plots/")
print(f"Election-level rows: {len(election_df)} | With incumbent data: {election_df['incumbent_pct'].notna().sum()}")
