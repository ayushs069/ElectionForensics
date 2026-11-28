"""
make_single_race_plot.py
Generates exactly 1 single plot: Whites vs Blacks with 2 bars in each denoting
voter turnout % of Democratic (Biden) vs Republican (Trump) counties.
Saved to: US_SocioEconomic/Easy_Election_Plots/easy_plots/outputs/05_turnout_by_race_white_vs_black.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load data
data_path = "US_SocioEconomic/US_Election_dataset_v1.csv"
df = pd.read_csv(data_path)
df.columns = [c.replace('\r', '').replace('\n', ' ').strip() for c in df.columns]

# Calculate turnout and winner
df['total_votes'] = df['2020 Democrat vote raw'] + df['2020 Republican vote raw'] + df['2020 other vote raw']
df['turnout_proxy'] = df['total_votes'] / df['Total Population']
df['Turnout %'] = df['turnout_proxy'] * 100

# Filter valid county turnout range
df = df[(df['Turnout %'] > 1) & (df['Turnout %'] <= 150)].copy()

# Winner variable
df['dem_win'] = df['2020 Democrat vote %'] > df['2020 Republican vote %']
df['Winner'] = np.where(df['dem_win'], 'Democratic Counties (Won by Biden)', 'Republican Counties (Won by Trump)')

# Filter Black counties (>= 10% NH-Black) and White counties (>= 80% NH-White)
black_counties = df[df['NH-Black percentage'] >= 10.0]
white_counties = df[df['NH-White percentage'] >= 80.0]

nat_avg = df['Turnout %'].mean()

# Colors
BLUE = "#2980B9"
RED = "#C0392B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "#FAFAFA",
})

fig, ax = plt.subplots(figsize=(10.5, 6.5))

categories = ["Blacks\n(High Black Share: ≥10%)", "Whites\n(High White Share: ≥80%)"]
x = np.arange(len(categories))
width = 0.36

# Dem and Rep stats for Blacks
dem_b = black_counties[black_counties['Winner'] == 'Democratic Counties (Won by Biden)']
rep_b = black_counties[black_counties['Winner'] == 'Republican Counties (Won by Trump)']

# Dem and Rep stats for Whites
dem_w = white_counties[white_counties['Winner'] == 'Democratic Counties (Won by Biden)']
rep_w = white_counties[white_counties['Winner'] == 'Republican Counties (Won by Trump)']

dem_means = [dem_b['Turnout %'].mean(), dem_w['Turnout %'].mean()]
dem_counts = [len(dem_b), len(dem_w)]

rep_means = [rep_b['Turnout %'].mean(), rep_w['Turnout %'].mean()]
rep_counts = [len(rep_b), len(rep_w)]

bars_dem = ax.bar(x - width/2, dem_means, width, label='Democratic Counties (Won by Biden)', color=BLUE, alpha=0.88, edgecolor='white')
bars_rep = ax.bar(x + width/2, rep_means, width, label='Republican Counties (Won by Trump)', color=RED, alpha=0.88, edgecolor='white')

# Reference line for national average turnout
ax.axhline(nat_avg, color='#555555', linestyle='--', linewidth=1.8,
           label=f'National County Average Turnout = {nat_avg:.1f}%')

# Annotate Dem bars
for bar, mean, count in zip(bars_dem, dem_means, dem_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.9,
            f"{mean:.1f}%\n(n={count})",
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=BLUE)

# Annotate Rep bars
for bar, mean, count in zip(bars_rep, rep_means, rep_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.9,
            f"{mean:.1f}%\n(n={count})",
            ha='center', va='bottom', fontsize=10, fontweight='bold', color=RED)

# Styling
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
ax.set_xlabel("Races / Racial Demographics Group", fontsize=11.5, fontweight='bold', labelpad=10)
ax.set_ylabel("Average Voter Turnout %", fontsize=11.5, fontweight='bold')
ax.set_ylim(0, 66)
ax.grid(axis='y', linestyle='--', alpha=0.4, color='#CCCCCC')

# Title & Subtitle
fig.suptitle("Figure 5: Voter Turnout by Race (Blacks vs Whites) — Democrat vs Republican Counties",
             fontsize=13.5, fontweight='bold', y=0.98, color='#111111')
ax.set_title("How Does Racial Composition Shape Voter Turnout Across Partisan Lines?",
             fontsize=11.5, fontweight='bold', color='#444444', pad=12)

# Legend
ax.legend(loc='upper left', framealpha=0.95, facecolor='white', edgecolor='#D1D5DB', fontsize=10)

plt.tight_layout()
plt.subplots_adjust(top=0.87)

out_dir = "US_SocioEconomic/Easy_Election_Plots/easy_plots/outputs"
os.makedirs(out_dir, exist_ok=True)
filepath = os.path.join(out_dir, "05_turnout_by_race_white_vs_black.png")

fig.savefig(filepath, dpi=300, bbox_inches='tight')
plt.close()

print(f"Successfully generated single plot -> {filepath}")
