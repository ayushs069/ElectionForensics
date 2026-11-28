"""
Improved EDA1 — Constituency Records per State
================================================
Generates a redesigned horizontal bar chart with:
  • Thin muted-red line separating states ≥400 / <400 records
  • Uttar Pradesh (highest): dark navy (#1B2A4A)
  • Assam (lowest): orange accent (#E88B3A)
  • All other states: muted gray-blue (#B0BEC5)
  • Value labels outside every bar
  • Descending sort
  • 600 dpi output → outputs/india/report_figures/

Usage:
    python src/eda1_improved.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── paths ──────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJ_ROOT, "data", "processed", "final_20const_14states.csv")
OUT_DIR   = os.path.join(PROJ_ROOT, "outputs", "india", "report_600dpi_images")
os.makedirs(OUT_DIR, exist_ok=True)

# ── load data ──────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip().str.lower()
df["state_n"] = df["state_n"].str.strip()

# constituency-election record counts, sorted descending
counts = df.groupby("state_n").size().sort_values(ascending=False)

# ── colour palette ─────────────────────────────────────────────
COLOR_UP     = "#1B2A4A"   # dark navy — Uttar Pradesh (highest)
COLOR_ASSAM  = "#E88B3A"   # orange — Assam (lowest)
COLOR_MIDDLE = "#B0BEC5"   # muted gray-blue — everyone else

top_state    = counts.index[0]    # Uttar Pradesh
bottom_state = counts.index[-1]   # Assam

colors = []
for state in counts.index:
    if state == top_state:
        colors.append(COLOR_UP)
    elif state == bottom_state:
        colors.append(COLOR_ASSAM)
    else:
        colors.append(COLOR_MIDDLE)

# ── plot style ─────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

fig, ax = plt.subplots(figsize=(10, max(5, len(counts) * 0.35)))

bars = ax.barh(counts.index, counts.values, color=colors,
               edgecolor="white", height=0.72)
ax.invert_yaxis()

# ── value labels — ALL outside the bar ─────────────────────────
max_val = counts.values.max()
for bar, val, state in zip(bars, counts.values, counts.index):
    txt_color = "#333333"
    x_pos     = val + max_val * 0.01
    ha        = "left"
    ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", ha=ha, fontsize=8.5,
            fontweight="bold", color=txt_color)

# ── thin muted-red separation line at 400 ─────────────────────
above_400 = [s for s in counts.index if counts[s] >= 400]
below_400 = [s for s in counts.index if counts[s] < 400]

if above_400 and below_400:
    idx_last_above = list(counts.index).index(above_400[-1])
    y_sep = idx_last_above + 0.5
    ax.axhline(y=y_sep, color="#C0392B", linestyle="--", linewidth=1.0,
               alpha=0.7, label="400-record threshold")

# ── axis labels (title removed — goes in caption) ─────────────
ax.set_xlabel("Number of Constituency-Election Records", fontsize=11)
ax.legend(fontsize=9, loc="lower right")

# room for value labels
ax.set_xlim(0, max_val * 1.12)

fig.tight_layout()

# ── save at 600 dpi ────────────────────────────────────────────
out_path = os.path.join(OUT_DIR, "fig1_records_per_state.png")
fig.savefig(out_path, dpi=600)
plt.close(fig)

print(f"✓ Saved (600 dpi): {out_path}")
