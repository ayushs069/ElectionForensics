"""
World vs India — Comparative RVM Election Analysis
====================================================
Generates 15 comparative plots asking key questions across
world elections, India elections, and direct head-to-head comparisons.

Outputs saved to: WORLD VS INDIA/plots/
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.integrate import quad

warnings.filterwarnings("ignore")

# ── style ─────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

# ── paths ─────────────────────────────────────────────────────
ROOT       = os.path.dirname(os.path.abspath(__file__))
PRJ        = os.path.dirname(ROOT)

WORLD_CSV  = os.path.join(PRJ, "constituency_level_results.csv")
INDIA_CSV  = os.path.join(PRJ, "INDIA", "final_20const_14states.csv")
WORLD_SUM  = os.path.join(PRJ, "rvm_outputs", "summary.csv")
INDIA_SUM  = os.path.join(PRJ, "INDIA", "rvm_outputs_14states", "summary.csv")

OUT        = os.path.join(ROOT, "plots")
os.makedirs(OUT, exist_ok=True)

# ── RVM analytical formula ────────────────────────────────────
def P_mu(mu):
    return (1 - mu) * (5 + 7 * mu) / ((1 + mu)**2 * (1 + 2 * mu)**2)

MU_MEAN, _ = quad(lambda m: m * P_mu(m), 0, 1)   # ≈ 0.2285

def F_x_analytical(x):
    x   = np.asarray(x, dtype=float)
    mu  = x * MU_MEAN
    out = np.zeros_like(mu)
    ok  = (mu > 0) & (mu < 1)
    out[ok] = MU_MEAN * P_mu(mu[ok])
    return out

def log_histogram(values, n_bins=55):
    v = np.asarray(values, dtype=float)
    v = v[v > 0]
    if len(v) < 5:
        return np.array([]), np.array([])
    bins = np.logspace(np.log10(v.min()), np.log10(v.max()), n_bins + 1)
    counts, edges = np.histogram(v, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])
    ok = counts > 0
    return centers[ok], counts[ok]

# ── load data ─────────────────────────────────────────────────
print("Loading datasets...")
world_df = pd.read_csv(WORLD_CSV)
world_df.columns = world_df.columns.str.strip().str.lower()
world_df = world_df[(world_df["vv1"] > 0) & (world_df["margin"] >= 0) & (world_df["margin"] <= world_df["vv1"])]
world_df["mu"] = world_df["margin"] / world_df["vv1"]

india_df = pd.read_csv(INDIA_CSV)
india_df.columns = india_df.columns.str.strip().str.lower()
india_df["state_n"] = india_df["state_n"].str.strip()
india_df = india_df[(india_df["vv1"] > 0) & (india_df["margin"] >= 0) & (india_df["margin"] <= india_df["vv1"])]
india_df["mu"] = india_df["margin"] / india_df["vv1"]

world_sum = pd.read_csv(WORLD_SUM)
india_sum = pd.read_csv(INDIA_SUM)

# For India summary rename 'state' to 'entity'
india_sum = india_sum.rename(columns={"state": "entity"})
world_sum = world_sum.rename(columns={"country": "entity"})

print(f"  World rows  : {len(world_df):,}  | Countries : {world_df['ctr_n'].nunique()}")
print(f"  India rows  : {len(india_df):,}  | States    : {india_df['state_n'].nunique()}")

# ─────────────────────────────────────────────────────────────────────────────
# Q1 — WORLD: How are voter turnouts distributed across countries globally?
# ─────────────────────────────────────────────────────────────────────────────
print("\nQ1: World turnout distribution per country (boxplot)...")
country_turnouts = [world_df[world_df["ctr_n"] == c]["vv1"].values for c in world_sum["entity"].values if c in world_df["ctr_n"].values]
country_labels   = [c for c in world_sum["entity"].values if c in world_df["ctr_n"].values]

fig, ax = plt.subplots(figsize=(12, 6))
bp = ax.boxplot(country_turnouts, vert=True, patch_artist=True,
                flierprops=dict(marker=".", ms=2, alpha=0.2),
                medianprops=dict(color="firebrick", lw=2))
for p in bp["boxes"]:
    p.set_facecolor("#cce5ff")
ax.set_xticks(range(1, len(country_labels)+1))
ax.set_xticklabels(country_labels, rotation=45, ha="right", fontsize=7)
ax.set_ylabel("Voter Turnout (vv1)", fontsize=11)
ax.set_title("Q1 [WORLD] — Voter Turnout Distribution Across Countries", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q01_world_turnout_by_country.png"), dpi=150)
plt.close(fig)
print("  ✓ Q1 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q2 — INDIA: How are voter turnouts distributed across states?
# ─────────────────────────────────────────────────────────────────────────────
print("Q2: India turnout distribution per state (boxplot)...")
state_turnouts = [india_df[india_df["state_n"] == s]["vv1"].values for s in india_sum["entity"].values]
state_labels   = india_sum["entity"].values

fig, ax = plt.subplots(figsize=(14, 5))
bp = ax.boxplot(state_turnouts, vert=True, patch_artist=True,
                flierprops=dict(marker=".", ms=2, alpha=0.2),
                medianprops=dict(color="#d73027", lw=2))
for p in bp["boxes"]:
    p.set_facecolor("#ffd9b3")
ax.set_xticks(range(1, len(state_labels)+1))
ax.set_xticklabels(state_labels, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Voter Turnout (vv1)", fontsize=11)
ax.set_title("Q2 [INDIA] — Voter Turnout Distribution Across States", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q02_india_turnout_by_state.png"), dpi=150)
plt.close(fig)
print("  ✓ Q2 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q3 — WORLD vs INDIA: How does the overall specific margin µ distribution compare?
# ─────────────────────────────────────────────────────────────────────────────
print("Q3: World vs India µ distribution...")
mu_world = world_df["mu"].values
mu_india = india_df["mu"].values

x_lin = np.linspace(0, 0.8, 400)
pdf_lin = [P_mu(m) for m in x_lin]

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(mu_world[mu_world > 0], bins=80, density=True, alpha=0.55, color="#2166ac", label="World (all countries)")
ax.hist(mu_india[mu_india > 0], bins=80, density=True, alpha=0.55, color="#d73027",  label="India (14 states)")
ax.plot(x_lin, pdf_lin, "k-", lw=2.5, label=f"Theoretical P(µ)  [RVM, 3 candidates]")
ax.set_xlabel(r"Specific Margin $\mu = M/T$", fontsize=13)
ax.set_ylabel("Density", fontsize=11)
ax.set_xlim(0, 0.8)
ax.set_title("Q3 [WORLD vs INDIA] — Distribution of Specific Margin µ = M/T", fontsize=12)
ax.legend(fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q03_world_vs_india_mu_dist.png"), dpi=150)
plt.close(fig)
print("  ✓ Q3 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q4 — WORLD vs INDIA: How does the scaled specific margin F(x) compare?
# ─────────────────────────────────────────────────────────────────────────────
print("Q4: World vs India universal F(x) overlay (log-log)...")
x_anal = np.logspace(-1.3, 0.8, 600)
Fx_anal = F_x_analytical(x_anal)

mu_w = mu_world[mu_world > 0];  x_w = mu_w / mu_w.mean()
mu_i = mu_india[mu_india > 0];  x_i = mu_i / mu_i.mean()
xw, Fw = log_histogram(x_w)
xi, Fi = log_histogram(x_i)

fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(xw, Fw, s=18, facecolors="none", edgecolors="#2166ac", lw=0.9, label="World (pooled)")
ax.scatter(xi, Fi, s=18, facecolors="none", edgecolors="#d73027", lw=0.9, label="India (14 states)")
ax.plot(x_anal, Fx_anal, "k-", lw=2.5, label="Analytical F(x)", zorder=5)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=13)
ax.set_ylabel(r"$F(x)$", fontsize=13)
ax.set_title("Q4 [WORLD vs INDIA] — Universal F(x) Overlay", fontsize=12)
ax.legend(fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q04_world_vs_india_Fx_overlay.png"), dpi=150)
plt.close(fig)
print("  ✓ Q4 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q5 — WORLD vs INDIA: Scaled margin f(M/<M>) comparison (log-log)
# ─────────────────────────────────────────────────────────────────────────────
print("Q5: Scaled margin log-log comparison...")
M_world = world_df["margin"].values.astype(float)
M_india = india_df["margin"].values.astype(float)

sm_w = M_world / M_world.mean();  sm_w = sm_w[sm_w > 0]
sm_i = M_india / M_india.mean();  sm_i = sm_i[sm_i > 0]
xmw, ymw = log_histogram(sm_w)
xmi, ymi = log_histogram(sm_i)

fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(xmw, ymw, s=18, facecolors="none", edgecolors="#2166ac", lw=0.9, label="World (pooled)")
ax.scatter(xmi, ymi, s=18, facecolors="none", edgecolors="#d73027", lw=0.9, label="India (14 states)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
ax.set_xlabel(r"$M\,/\,\langle M\rangle$", fontsize=13)
ax.set_ylabel(r"$f(M/\langle M\rangle)$", fontsize=13)
ax.set_title("Q5 [WORLD vs INDIA] — Scaled Margin Distribution (log-log)", fontsize=12)
ax.legend(fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q05_world_vs_india_scaled_margin.png"), dpi=150)
plt.close(fig)
print("  ✓ Q5 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q6 — WORLD vs INDIA: How do mean specific margins compare entity by entity?
# ─────────────────────────────────────────────────────────────────────────────
print("Q6: Mean µ comparison — world countries vs India states...")
world_mu_mean = world_sum[["entity","mean_mu"]].copy()
world_mu_mean["source"] = "World"
india_mu_mean = india_sum[["entity","mean_mu"]].copy()
india_mu_mean["source"] = "India"
combined = pd.concat([world_mu_mean, india_mu_mean], ignore_index=True).sort_values("mean_mu")

colors_c = ["#2166ac" if s == "World" else "#d73027" for s in combined["source"]]
fig, ax = plt.subplots(figsize=(12, max(6, len(combined) * 0.28)))
ax.barh(combined["entity"], combined["mean_mu"], color=colors_c, edgecolor="white")
ax.axvline(MU_MEAN, color="black", ls="--", lw=1.5, label=f"Theoretical ⟨µ⟩ = {MU_MEAN:.4f}")
ax.set_xlabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=12)
ax.set_title("Q6 [WORLD vs INDIA] — Mean Specific Margin by Entity\n(blue=World country, red=India state)", fontsize=12)
ax.legend(fontsize=9)
from matplotlib.patches import Patch
leg_els = [Patch(facecolor="#2166ac", label="World country"),
           Patch(facecolor="#d73027", label="India state")]
ax.legend(handles=leg_els + [plt.Line2D([0],[0], color="black", ls="--", lw=1.5, label=f"Theoretical ⟨µ⟩ = {MU_MEAN:.4f}")],
          fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q06_mean_mu_world_vs_india.png"), dpi=150)
plt.close(fig)
print("  ✓ Q6 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q7 — WORLD vs INDIA: Fraud score ranking (all entities together)
# ─────────────────────────────────────────────────────────────────────────────
print("Q7: Combined fraud score ranking...")
world_sum["source"] = "World"
india_sum["source"] = "India"
all_fraud = pd.concat([world_sum[["entity","fraud_score","flagged","source"]],
                        india_sum[["entity","fraud_score","flagged","source"]]], ignore_index=True)
all_fraud = all_fraud.sort_values("fraud_score", ascending=True)

colors_f = []
for _, r in all_fraud.iterrows():
    if r["flagged"]:
        colors_f.append("#d73027")
    elif r["source"] == "World":
        colors_f.append("#2166ac")
    else:
        colors_f.append("#f4a582")

fig, ax = plt.subplots(figsize=(10, max(7, len(all_fraud) * 0.3)))
bars = ax.barh(all_fraud["entity"], all_fraud["fraud_score"], color=colors_f, edgecolor="white", height=0.7)
ax.axvline(3.0, color="firebrick", ls="--", lw=1.5, label="Flag threshold (|z|=3)")
for bar, val, flag in zip(bars, all_fraud["fraud_score"], all_fraud["flagged"]):
    ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}" + ("  ⚠" if flag else ""),
            va="center", fontsize=7, color="firebrick" if flag else "black")
leg_els = [Patch(facecolor="#2166ac", label="World country (OK)"),
           Patch(facecolor="#f4a582", label="India state (OK)"),
           Patch(facecolor="#d73027", label="Flagged (any)")]
ax.legend(handles=leg_els + [plt.Line2D([0],[0], color="firebrick", ls="--", lw=1.5, label="Threshold |z|=3")], fontsize=9)
ax.set_xlabel("Fraud Score (mean |z|)", fontsize=11)
ax.set_title("Q7 [WORLD vs INDIA] — Combined Fraud Score Ranking\nAll Countries + India States", fontsize=12)
ax.set_xlim(0, all_fraud["fraud_score"].max() * 1.2 + 0.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q07_combined_fraud_ranking.png"), dpi=150)
plt.close(fig)
print("  ✓ Q7 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q8 — WORLD vs INDIA: What fraction of entities are flagged?
# ─────────────────────────────────────────────────────────────────────────────
print("Q8: Flagged proportion comparison (pie / group bar)...")
w_flagged = world_sum["flagged"].sum(); w_total = len(world_sum)
i_flagged = india_sum["flagged"].sum(); i_total = len(india_sum)

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
for ax, flagged, total, label, c1, c2 in [
    (axes[0], w_flagged, w_total, "World Countries",  "#d73027", "#2166ac"),
    (axes[1], i_flagged, i_total, "India States",     "#d73027", "#f4a582"),
]:
    sizes = [flagged, total - flagged]
    axes_labels = [f"Flagged\n({flagged})", f"OK\n({total-flagged})"]
    wedges, texts, autotexts = ax.pie(sizes, labels=axes_labels, colors=[c1, c2],
                                       autopct="%1.0f%%", startangle=90,
                                       wedgeprops=dict(edgecolor="white", linewidth=1.5))
    for at in autotexts:
        at.set_fontsize(12)
    ax.set_title(label, fontsize=12)
fig.suptitle("Q8 [WORLD vs INDIA] — Fraction of Entities Flagged for Anomalies", fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q08_flagged_proportion.png"), dpi=150, bbox_inches="tight")
plt.close(fig)
print("  ✓ Q8 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q9 — WORLD: How do fraud scores vary across individual countries?
# ─────────────────────────────────────────────────────────────────────────────
print("Q9: World — fraud score by country (scatter, sorted)...")
ws = world_sum.sort_values("fraud_score", ascending=False).reset_index(drop=True)
colors9 = ["#d73027" if f else "#2166ac" for f in ws["flagged"]]

fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(range(len(ws)), ws["fraud_score"], c=colors9, s=60, zorder=3)
ax.axhline(3.0, color="firebrick", ls="--", lw=1.5, label="Threshold |z|=3")
for i, (_, row) in enumerate(ws.iterrows()):
    ax.text(i, row["fraud_score"] + 0.05, row["entity"], rotation=75,
            fontsize=6.5, ha="center", va="bottom",
            color="#d73027" if row["flagged"] else "black")
ax.set_xticks([]); ax.set_ylabel("Fraud Score (mean |z|)", fontsize=11)
ax.set_title("Q9 [WORLD] — Fraud Score by Country (sorted descending)", fontsize=12)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q09_world_fraud_scatter.png"), dpi=150)
plt.close(fig)
print("  ✓ Q9 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q10 — INDIA: Fraud score by state with threshold line
# ─────────────────────────────────────────────────────────────────────────────
print("Q10: India — fraud score by state...")
is_ = india_sum.sort_values("fraud_score", ascending=True)
colors10 = ["#d73027" if f else "#f4a582" for f in is_["flagged"]]

fig, ax = plt.subplots(figsize=(9, max(5, len(is_) * 0.38)))
bars = ax.barh(is_["entity"], is_["fraud_score"], color=colors10, edgecolor="white", height=0.7)
ax.axvline(3.0, color="firebrick", ls="--", lw=1.5, label="Threshold |z|=3")
for bar, val, flag in zip(bars, is_["fraud_score"], is_["flagged"]):
    ax.text(val + 0.02, bar.get_y() + bar.get_height()/2,
            f"{val:.2f}" + ("  ⚠" if flag else ""),
            va="center", fontsize=9,
            color="firebrick" if flag else "black")
ax.set_xlabel("Fraud Score (mean |z|)", fontsize=11)
ax.set_title("Q10 [INDIA] — Fraud Score by State\n(threshold = 3.0)", fontsize=12)
ax.legend(fontsize=9)
ax.set_xlim(0, is_["fraud_score"].max() * 1.3 + 0.2)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q10_india_fraud_by_state.png"), dpi=150)
plt.close(fig)
print("  ✓ Q10 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q11 — WORLD vs INDIA: Fraud score distribution (violin/box)
# ─────────────────────────────────────────────────────────────────────────────
print("Q11: Fraud score distribution — World vs India (violin)...")
fig, ax = plt.subplots(figsize=(8, 6))
data_v = [world_sum["fraud_score"].values, india_sum["fraud_score"].values]
vp = ax.violinplot(data_v, positions=[1, 2], showmedians=True, showextrema=True)
for i, (body, color) in enumerate(zip(vp["bodies"], ["#2166ac", "#d73027"])):
    body.set_facecolor(color); body.set_alpha(0.6)
vp["cmedians"].set_color("black"); vp["cmedians"].set_lw(2)
for part in ["cbars","cmins","cmaxes"]:
    vp[part].set_color("gray"); vp[part].set_lw(1)
ax.axhline(3.0, color="firebrick", ls="--", lw=1.5, label="Flag threshold (|z|=3)")
ax.set_xticks([1, 2]); ax.set_xticklabels(["World Countries", "India States"], fontsize=12)
ax.set_ylabel("Fraud Score (mean |z|)", fontsize=11)
ax.set_title("Q11 [WORLD vs INDIA] — Fraud Score Distribution", fontsize=12)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q11_fraud_score_violin.png"), dpi=150)
plt.close(fig)
print("  ✓ Q11 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q12 — WORLD vs INDIA: Mean µ vs fraud score scatter (entity-level)
# ─────────────────────────────────────────────────────────────────────────────
print("Q12: Mean µ vs fraud score scatter...")
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(world_sum["mean_mu"], world_sum["fraud_score"],
           s=60, c=["#d73027" if f else "#2166ac" for f in world_sum["flagged"]],
           marker="o", label="World country", zorder=3, alpha=0.85)
ax.scatter(india_sum["mean_mu"], india_sum["fraud_score"],
           s=80, c=["#d73027" if f else "#f4a582" for f in india_sum["flagged"]],
           marker="s", label="India state", zorder=4, alpha=0.85)
ax.axhline(3.0, color="firebrick", ls="--", lw=1.2, label="Flag threshold")
ax.axvline(MU_MEAN, color="gray", ls=":", lw=1.2, label=f"Theoretical ⟨µ⟩={MU_MEAN:.4f}")
ax.set_xlabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=12)
ax.set_ylabel("Fraud Score (mean |z|)", fontsize=11)
ax.set_title("Q12 [WORLD vs INDIA] — Mean µ vs Fraud Score\n(circle=world, square=India state)", fontsize=12)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q12_mean_mu_vs_fraud_scatter.png"), dpi=150)
plt.close(fig)
print("  ✓ Q12 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q13 — WORLD: Number of constituency records per country
# ─────────────────────────────────────────────────────────────────────────────
print("Q13: World — constituency records per country...")
world_cnt = world_df.groupby("ctr_n").size().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, max(5, len(world_cnt) * 0.3)))
clrs = plt.cm.Blues_r(np.linspace(0.3, 0.9, len(world_cnt)))
ax.barh(world_cnt.index, world_cnt.values, color=clrs, edgecolor="white")
ax.set_xlabel("Number of Constituency Records", fontsize=11)
ax.set_title("Q13 [WORLD] — Constituency Records per Country", fontsize=12)
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q13_world_records_per_country.png"), dpi=150)
plt.close(fig)
print("  ✓ Q13 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q14 — WORLD vs INDIA: How close are empirical <µ> to the theoretical value?
# ─────────────────────────────────────────────────────────────────────────────
print("Q14: Deviation of mean µ from theoretical value...")
world_dev = world_sum["mean_mu"] - MU_MEAN
india_dev = india_sum["mean_mu"] - MU_MEAN

fig, ax = plt.subplots(figsize=(10, 5))
w_sorted = world_sum.assign(dev=world_dev).sort_values("dev")
i_sorted = india_sum.assign(dev=india_dev).sort_values("dev")

ax.barh(w_sorted["entity"], w_sorted["dev"], color="#2166ac", alpha=0.75, label="World country", height=0.6)
ax.barh(i_sorted["entity"], i_sorted["dev"], color="#d73027", alpha=0.75, label="India state", height=0.6)
ax.axvline(0, color="black", lw=1.5)
ax.set_xlabel(r"$\langle\mu\rangle_{empirical} - \langle\mu\rangle_{theory}$", fontsize=12)
ax.set_title("Q14 [WORLD vs INDIA] — Deviation of Mean µ from Theoretical Value", fontsize=12)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q14_dev_from_theoretical_mu.png"), dpi=150)
plt.close(fig)
print("  ✓ Q14 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q15 — WORLD vs INDIA: Side-by-side scaled margin + F(x) (2×2 overview)
# ─────────────────────────────────────────────────────────────────────────────
print("Q15: 2×2 overview — Scaled margin and F(x) for World and India...")
x_anal = np.logspace(-1.3, 0.8, 600)
Fx_anal = F_x_analytical(x_anal)

fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# Row 1: Scaled margin (world | india)
for ax, sm, lcolor, lbl in [
    (axes[0,0], sm_w, "#2166ac", "World (pooled)"),
    (axes[0,1], sm_i, "#d73027", "India (14 states)")
]:
    x_, y_ = log_histogram(sm)
    ax.scatter(x_, y_, s=18, facecolors="none", edgecolors=lcolor, lw=0.9, label=lbl)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$M\,/\,\langle M\rangle$", fontsize=12)
    ax.set_ylabel(r"$f(M/\langle M\rangle)$", fontsize=12)
    ax.set_title(f"Scaled Margin — {lbl}", fontsize=11)
    ax.legend(fontsize=9)

# Row 2: F(x) (world | india)
for ax, x_dat, lcolor, lbl in [
    (axes[1,0], x_w, "#2166ac", "World (pooled)"),
    (axes[1,1], x_i, "#d73027", "India (14 states)")
]:
    xh, Fh = log_histogram(x_dat)
    ax.scatter(xh, Fh, s=18, facecolors="none", edgecolors=lcolor, lw=0.9, label=lbl)
    ax.plot(x_anal, Fx_anal, "k-", lw=2, label="Analytical F(x)", zorder=5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=12)
    ax.set_ylabel(r"$F(x)$", fontsize=12)
    ax.set_title(f"Universal F(x) — {lbl}", fontsize=11)
    ax.legend(fontsize=9)

fig.suptitle("Q15 [WORLD vs INDIA] — 2×2 RVM Overview: Scaled Margin & Universal F(x)", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q15_2x2_overview.png"), dpi=150)
plt.close(fig)
print("  ✓ Q15 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Q16 — WORLD vs INDIA: Number of units vs mean µ scatter (size = fraud)
# ─────────────────────────────────────────────────────────────────────────────
print("Q16: n_units vs mean_mu bubble plot (size=fraud score)...")
fig, ax = plt.subplots(figsize=(10, 7))

for _, row in world_sum.iterrows():
    color = "#d73027" if row["flagged"] else "#2166ac"
    size  = max(20, row["fraud_score"] * 40)
    ax.scatter(row["n_units"], row["mean_mu"], s=size, c=color, alpha=0.65, marker="o", zorder=3)
    ax.text(row["n_units"]*1.01, row["mean_mu"], row["entity"], fontsize=6, va="center", color="gray")

for _, row in india_sum.iterrows():
    color = "#d73027" if row["flagged"] else "#e87d0d"
    size  = max(20, row["fraud_score"] * 40)
    ax.scatter(row["n_units"], row["mean_mu"], s=size, c=color, alpha=0.75, marker="s", zorder=4)
    ax.text(row["n_units"]*1.01, row["mean_mu"], row["entity"], fontsize=6.5, va="center", color="saddlebrown")

ax.axhline(MU_MEAN, color="black", ls="--", lw=1.2, label=f"Theory ⟨µ⟩={MU_MEAN:.4f}")
leg_els = [plt.scatter([],[], s=60, c="#2166ac", marker="o", label="World country"),
           plt.scatter([],[], s=60, c="#e87d0d", marker="s", label="India state"),
           plt.scatter([],[], s=60, c="#d73027", marker="o", label="Flagged entity"),
           plt.Line2D([0],[0], color="black", ls="--", lw=1.2, label=f"Theory ⟨µ⟩")]
ax.legend(handles=leg_els, fontsize=8)
ax.set_xlabel("Number of Constituency Records (n_units)", fontsize=11)
ax.set_ylabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=11)
ax.set_title("Q16 [WORLD vs INDIA] — Coverage vs Mean µ\n(bubble size ∝ fraud score)", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "Q16_coverage_vs_mean_mu_bubble.png"), dpi=150)
plt.close(fig)
print("  ✓ Q16 saved")

# ─────────────────────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("  All 16 plots saved to:", OUT)
print("═"*60)
