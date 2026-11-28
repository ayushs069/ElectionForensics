"""
EDA6 — Scientific Reports Redesign
====================================
Mean Specific Margin (⟨μ⟩) over election years for India.

Changes vs original:
  • Scientific Reports typography & style
  • 1975–1977 Emergency period lightly shaded + labelled
  • Theoretical ⟨μ⟩ = 0.1993 dashed line preserved
  • 600 dpi → outputs/india/report_figures/

Usage:
    python src/eda6_scientific.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.integrate import quad

# ── RVM theoretical mean ───────────────────────────────────────
def P_mu(mu):
    return (1 - mu) * (5 + 7 * mu) / ((1 + mu)**2 * (1 + 2 * mu)**2)

MU_MEAN, _ = quad(lambda m: m * P_mu(m), 0, 1)   # 0.199289

# ── paths ──────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJ_ROOT, "data", "processed", "final_20const_14states.csv")
OUT_DIR   = os.path.join(PROJ_ROOT, "outputs", "india", "report_600dpi_images")
os.makedirs(OUT_DIR, exist_ok=True)

# ── load & compute ─────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip().str.lower()
df["state_n"] = df["state_n"].str.strip()
df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]

year_mu = (
    df.assign(mu=df["margin"] / df["vv1"])
      .groupby("yr")["mu"].mean()
      .sort_index()
)

# ── Scientific Reports style ───────────────────────────────────
plt.rcParams.update({
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "DejaVu Serif"],
    "font.size":          9,
    "axes.labelsize":     10,
    "axes.titlesize":     10,
    "xtick.labelsize":    8.5,
    "ytick.labelsize":    8.5,
    "legend.fontsize":    8.5,
    "axes.linewidth":     0.8,
    "xtick.major.width":  0.7,
    "ytick.major.width":  0.7,
    "xtick.minor.width":  0.5,
    "ytick.minor.width":  0.5,
    "xtick.direction":    "in",
    "ytick.direction":    "in",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.dpi":         150,
})

# ── figure ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.0, 3.2))   # ~178 mm wide — Sci Reports 1-col

years  = year_mu.index.values
values = year_mu.values

# filled area under curve
ax.fill_between(years, values, alpha=0.10, color="#2166AC", linewidth=0)

# main line + markers
ax.plot(years, values, "-o",
        color="#2166AC", linewidth=1.4, markersize=3.8,
        markeredgewidth=0.6, markeredgecolor="#2166AC",
        markerfacecolor="white", zorder=4, label=r"$\langle\mu\rangle$ (observed)")

# theoretical reference line
ax.axhline(MU_MEAN, color="#C0392B", linestyle="--", linewidth=1.1,
           alpha=0.85, zorder=3,
           label=fr"Theoretical $\langle\mu\rangle$ = {MU_MEAN:.4f}")

# ── Emergency period shading (1975–1977) ───────────────────────
EMRG_START, EMRG_END = 1975, 1977
ax.axvspan(EMRG_START, EMRG_END, color="#FFAA00", alpha=0.13, linewidth=0, zorder=1)
ax.axvline(EMRG_START, color="#B8860B", linewidth=0.7, linestyle=":", alpha=0.7)
ax.axvline(EMRG_END,   color="#B8860B", linewidth=0.7, linestyle=":", alpha=0.7)

# label — anchored to top of axes, centred on shaded band
ax.text((EMRG_START + EMRG_END) / 2, 0.97,
        "Emergency\n(1975–77)", ha="center", va="top",
        fontsize=7.5, color="#7A5C00", style="italic",
        transform=ax.get_xaxis_transform(),
        bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                  edgecolor="#FFAA00", linewidth=0.6, alpha=0.88))

# ── axes ───────────────────────────────────────────────────────
ax.set_xlabel("Election Year", labelpad=5)
ax.set_ylabel(r"Mean Specific Margin $\langle\mu\rangle$", labelpad=6)
# title removed — goes in caption

ax.set_xlim(years.min() - 1, years.max() + 1)
ax.set_ylim(0, values.max() * 1.20)

ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
ax.xaxis.set_minor_locator(mticker.MultipleLocator(5))
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.05))
ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.025))
ax.tick_params(which="minor", length=3)
ax.tick_params(which="major", length=5)

ax.legend(loc="upper right", frameon=True,
          framealpha=0.92, edgecolor="#CCCCCC", handlelength=2.2)

fig.tight_layout(pad=0.5)

# ── save ───────────────────────────────────────────────────────
out_path = os.path.join(OUT_DIR, "fig2_mean_mu_over_years.png")
fig.savefig(out_path, dpi=600, bbox_inches="tight")
plt.close(fig)
print(f"✓ Saved (600 dpi): {out_path}")
