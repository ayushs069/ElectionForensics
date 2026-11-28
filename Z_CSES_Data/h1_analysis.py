"""
H1 Analysis: Demographic/Socioeconomic Factors → Voter Turnout
CSES IMD Dataset | 204,333 respondents | 54 countries | 1996-2016
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('/mnt/user-data/uploads/cses_clean.csv')

# Pre-processing
df = df[~df['education'].isin([6.0])]          # drop 19 "Other" edu rows
df = df[df['income_quintile'] != 6.0]          # drop non-quintile income
df = df[df['gender'].isin([1.0, 2.0])]         # keep M/F only (3=Other: tiny)
df['turnout'] = df['turnout'].astype(int)
df['inflation_log'] = np.log1p(df['inflation_rate'].clip(lower=0))

# Age bins
df['age_group'] = pd.cut(df['age'], bins=[0,24,34,44,54,64,120],
                          labels=['<25','25-34','35-44','45-54','55-64','65+'])

# Education labels (ordered)
edu_map = {0:'None',1:'Primary',2:'Secondary',3:'Post-Sec',4:'University'}
df['edu_label2'] = df['education'].map(edu_map)
edu_order = ['None','Primary','Secondary','Post-Sec','University']

# Employment groups
emp_map = {0:'Employed',1:'Employed',2:'Employed',3:'Employed',4:'Employed',
           5:'Unemployed',6:'Student',7:'Retired',8:'Homemaker',
           9:'Other',10:'Other',11:'Other',12:'Other'}
df['emp_group'] = df['employment_status'].map(emp_map)

BLUE  = "#2980B9"
RED   = "#C0392B"
GREEN = "#27AE60"
PURP  = "#8E44AD"
ORG   = "#E67E22"
OUT   = "/home/claude/h1_plots"

plt.rcParams.update({"axes.spines.top":False,"axes.spines.right":False,
                     "figure.facecolor":"white","axes.facecolor":"#FAFAFA"})

print(f"Dataset after pre-processing: {df.shape}")

# ════════════════════════════════════════════════════════════
# H1 PLOT 1 — Overall turnout rate + breakdown headline
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
fig.suptitle("H1: Who Votes? Turnout by Gender, Education and Income\n"
             "CSES Survey Data | 54 Countries | 1996–2016",
             fontweight="bold", fontsize=13, y=1.01)

# Gender
gender_map = {1.0:"Male", 2.0:"Female"}
g_turn = df.groupby('gender')['turnout'].mean() * 100
g_labels = [gender_map[k] for k in g_turn.index]
bars = axes[0].bar(g_labels, g_turn.values,
                   color=[BLUE, RED], alpha=0.85, width=0.5, edgecolor='white')
for bar, val in zip(bars, g_turn.values):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"{val:.1f}%", ha='center', fontweight='bold', fontsize=12)
axes[0].set_ylim(0, 100)
axes[0].set_title("By Gender", fontweight='bold')
axes[0].set_ylabel("Voter Turnout %")
r_g, p_g = stats.pointbiserialr(df['gender']-1, df['turnout'])
axes[0].text(0.97, 0.05, f"r = {r_g:.3f}",
             transform=axes[0].transAxes, ha='right', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))

# Education
edu_turn = df.groupby('edu_label2', observed=True)['turnout'].mean() * 100
edu_turn = edu_turn.reindex(edu_order).dropna()
colors_e = ["#D5E8D4","#82B366","#6AAF6A","#2D7A2D","#1A4D1A"]
bars = axes[1].bar(edu_turn.index, edu_turn.values,
                   color=colors_e, alpha=0.87, edgecolor='white', width=0.6)
for bar, val in zip(bars, edu_turn.values):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"{val:.1f}%", ha='center', fontweight='bold', fontsize=10)
axes[1].set_ylim(0, 100)
axes[1].set_title("By Education Level", fontweight='bold')
axes[1].set_ylabel("Voter Turnout %")
r_e, p_e = stats.pointbiserialr(df['education'], df['turnout'])
axes[1].text(0.97, 0.05, f"r = {r_e:.3f}***",
             transform=axes[1].transAxes, ha='right', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))
axes[1].tick_params(axis='x', labelsize=9)

# Income
inc_turn = df.groupby('income_quintile')['turnout'].mean() * 100
colors_i = ["#AED6F1","#5DADE2","#2E86C1","#1A5276","#0D2B52"]
bars = axes[2].bar([f"Q{int(q)}" for q in inc_turn.index], inc_turn.values,
                   color=colors_i, alpha=0.87, edgecolor='white', width=0.6)
for bar, val in zip(bars, inc_turn.values):
    axes[2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"{val:.1f}%", ha='center', fontweight='bold', fontsize=11)
axes[2].set_ylim(0, 100)
axes[2].set_title("By Household Income Quintile\n(Q1=Lowest, Q5=Highest)", fontweight='bold')
axes[2].set_ylabel("Voter Turnout %")
r_i, p_i = stats.pointbiserialr(df['income_quintile'], df['turnout'])
axes[2].text(0.97, 0.05, f"r = {r_i:.3f}***",
             transform=axes[2].transAxes, ha='right', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))

plt.tight_layout()
fig.savefig(f"{OUT}/H1_01_gender_education_income.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 1 done")

# ════════════════════════════════════════════════════════════
# H1 PLOT 2 — Turnout by Age Group
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
age_turn = df.groupby('age_group', observed=True)['turnout'].agg(['mean','count'])
age_turn['pct'] = age_turn['mean'] * 100
colors_a = [RED,"#E67E22","#F1C40F","#27AE60",BLUE,"#1A5276"]
bars = ax.bar(age_turn.index, age_turn['pct'],
              color=colors_a, alpha=0.87, edgecolor='white', width=0.6)
for bar, (idx, row) in zip(bars, age_turn.iterrows()):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
            f"{row['pct']:.1f}%\n(n={int(row['count']):,})",
            ha='center', fontsize=9.5, fontweight='bold')
ax.set_ylim(0, 100)
ax.axhline(df['turnout'].mean()*100, color='gray', ls='--', lw=1.5,
           label=f"Overall avg = {df['turnout'].mean()*100:.1f}%")
r_a, p_a = stats.pointbiserialr(df['age'], df['turnout'])
ax.set_title("H1: Voter Turnout by Age Group\nDo Younger People Vote Less?",
             fontweight='bold', fontsize=13)
ax.set_xlabel("Age Group", fontsize=11)
ax.set_ylabel("Voter Turnout %", fontsize=11)
ax.legend()
ax.text(0.97, 0.05, f"Correlation (age vs turnout) r = {r_a:.3f}***",
        transform=ax.transAxes, ha='right', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))
plt.tight_layout()
fig.savefig(f"{OUT}/H1_02_turnout_by_age.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 2 done")

# ════════════════════════════════════════════════════════════
# H1 PLOT 3 — Turnout by Employment Status
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 6))
emp_turn = df.groupby('emp_group')['turnout'].agg(['mean','count'])
emp_turn['pct'] = emp_turn['mean'] * 100
emp_turn = emp_turn.sort_values('pct', ascending=True)
colors_emp = [RED if v < 80 else BLUE for v in emp_turn['pct']]
bars = ax.barh(emp_turn.index, emp_turn['pct'],
               color=colors_emp, alpha=0.85, edgecolor='white', height=0.6)
for bar, (idx, row) in zip(bars, emp_turn.iterrows()):
    ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
            f"{row['pct']:.1f}%  (n={int(row['count']):,})",
            va='center', fontsize=10, fontweight='bold')
ax.set_xlim(0, 105)
ax.axvline(df['turnout'].mean()*100, color='gray', ls='--', lw=1.5,
           label=f"Overall avg = {df['turnout'].mean()*100:.1f}%")
ax.set_title("H1: Voter Turnout by Employment Status\nWho Is Most and Least Likely to Vote?",
             fontweight='bold', fontsize=13)
ax.set_xlabel("Voter Turnout %", fontsize=11)
ax.legend()
plt.tight_layout()
fig.savefig(f"{OUT}/H1_03_turnout_by_employment.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 3 done")

# ════════════════════════════════════════════════════════════
# H1 PLOT 4 — Education × Income Heatmap
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 7))
heat = df.groupby(['edu_label2','income_quintile'], observed=True)['turnout'].mean() * 100
heat = heat.unstack('income_quintile')
heat = heat.reindex(edu_order).dropna(how='all')
heat.columns = [f"Q{int(c)}" for c in heat.columns]
sns.heatmap(heat, annot=True, fmt='.1f', cmap='Blues',
            linewidths=0.5, ax=ax, cbar_kws={'label':'Turnout %'},
            vmin=70, vmax=95, annot_kws={'size':11,'fontweight':'bold'})
ax.set_title("H1: Turnout Rate Matrix — Education × Income\n"
             "Does Education Effect Hold Across All Income Levels?",
             fontweight='bold', fontsize=13)
ax.set_xlabel("Household Income Quintile (Q1=Lowest → Q5=Highest)", fontsize=11)
ax.set_ylabel("Education Level", fontsize=11)
plt.tight_layout()
fig.savefig(f"{OUT}/H1_04_education_income_heatmap.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 4 done")

# ════════════════════════════════════════════════════════════
# H1 PLOT 5 — Correlation Summary Bar Chart
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
vars_h1 = {
    'Age':               'age',
    'Education':         'education',
    'Income Quintile':   'income_quintile',
    'Employed (vs not)': 'employed',
    'Unemployed (vs not)':'unemployed',
    'Gender (Female=2)': 'gender',
}
corrs, names = [], []
for label, col in vars_h1.items():
    sub = df[[col,'turnout']].dropna()
    r, p = stats.pointbiserialr(sub[col], sub['turnout'])
    corrs.append(r)
    names.append(label)

colors_c = [GREEN if r > 0 else RED for r in corrs]
bars = ax.barh(names, corrs, color=colors_c, alpha=0.85,
               edgecolor='white', height=0.55)
ax.axvline(0, color='black', lw=1.5)
ax.set_xlim(-0.15, 0.20)
for bar, r in zip(bars, corrs):
    xpos = r + 0.004 if r >= 0 else r - 0.004
    ha = 'left' if r >= 0 else 'right'
    ax.text(xpos, bar.get_y()+bar.get_height()/2,
            f"r = {r:.3f}", va='center', ha=ha, fontsize=10, fontweight='bold')
ax.set_title("H1: Correlation of Socioeconomic Variables with Voter Turnout\n"
             "Green = positive link with voting | Red = negative link",
             fontweight='bold', fontsize=12)
ax.set_xlabel("Point-Biserial Correlation (r) with Turnout")
g_patch = mpatches.Patch(color=GREEN, alpha=0.8, label='Higher value → more turnout')
r_patch = mpatches.Patch(color=RED,   alpha=0.8, label='Higher value → less turnout')
ax.legend(handles=[g_patch, r_patch], fontsize=9)
plt.tight_layout()
fig.savefig(f"{OUT}/H1_05_correlation_summary.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 5 done")

# ════════════════════════════════════════════════════════════
# H1 PLOT 6 — Logistic Regression Odds Ratios
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 7))
feat_cols = ['age','education','income_quintile','employed','unemployed']
feat_labels = ['Age','Education','Income Quintile','Employed','Unemployed']

sub = df[feat_cols + ['turnout']].dropna()
scaler = StandardScaler()
X = sub[feat_cols].copy()
X[['age','education','income_quintile']] = scaler.fit_transform(
    X[['age','education','income_quintile']])
y = sub['turnout'].astype(int)

log_reg = LogisticRegression(max_iter=500, random_state=42)
log_reg.fit(X, y)
cv_acc = cross_val_score(log_reg, X, y, cv=5, scoring='accuracy').mean()

odds_ratios = np.exp(log_reg.coef_[0])
colors_or = [GREEN if o > 1 else RED for o in odds_ratios]
bars = ax.barh(feat_labels, odds_ratios, color=colors_or,
               alpha=0.85, edgecolor='white', height=0.55)
ax.axvline(1.0, color='black', lw=2, ls='--', label='OR=1 (no effect)')
for bar, o in zip(bars, odds_ratios):
    ax.text(o + 0.01, bar.get_y()+bar.get_height()/2,
            f"OR = {o:.3f}", va='center', fontsize=10, fontweight='bold')
ax.set_title(f"H1: Logistic Regression — Odds Ratios for Voter Turnout\n"
             f"CV Accuracy = {cv_acc:.3f} | OR > 1 = increases turnout probability",
             fontweight='bold', fontsize=12)
ax.set_xlabel("Odds Ratio (OR)\nOR > 1.0 = increases turnout | OR < 1.0 = decreases turnout")
ax.legend()
plt.tight_layout()
fig.savefig(f"{OUT}/H1_06_logistic_odds_ratios.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 6 done")

# ════════════════════════════════════════════════════════════
# H1 PLOT 7 — Turnout by country (top+bottom 15)
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 10))
ctry_turn = df.groupby('country')['turnout'].mean() * 100
ctry_turn = ctry_turn.sort_values()
overall = ctry_turn.mean()
colors_ct = [BLUE if v >= overall else RED for v in ctry_turn.values]
bars = ax.barh(ctry_turn.index, ctry_turn.values,
               color=colors_ct, alpha=0.82, edgecolor='white', height=0.7)
ax.axvline(overall, color='black', ls='--', lw=1.5,
           label=f"Mean = {overall:.1f}%")
ax.set_xlabel("Voter Turnout % (Survey Self-Report)", fontsize=11)
ax.set_title("H1: Voter Turnout Rate by Country\n"
             "Blue = above average | Red = below average | 54 Countries",
             fontweight='bold', fontsize=13)
ax.legend()
plt.tight_layout()
fig.savefig(f"{OUT}/H1_07_turnout_by_country.png", dpi=150, bbox_inches='tight')
plt.close()
print("H1 Plot 7 done")

# Save H1 correlation table
corr_table = pd.DataFrame({'Variable': names, 'r': [round(r,4) for r in corrs]})
corr_table['Interpretation'] = corr_table['r'].apply(
    lambda r: 'Positive → more turnout' if r > 0 else 'Negative → less turnout')
corr_table.to_csv("/home/claude/outputs/H1_correlations.csv", index=False)

print("\n✓ All H1 plots saved to /home/claude/h1_plots/")
print(f"CV Accuracy (Logistic, no country FE): {cv_acc:.3f}")
