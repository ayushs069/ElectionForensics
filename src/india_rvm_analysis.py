"""
India RVM Analysis Script
==========================
Adapted for India parliamentary election data.

Dataset: INDIA/finallllllll.csv
    Columns: state_n, yr, cst_n, vv1, winner_votes, runnerup_votes,
             margin, specific_margin, scaled_margin, scaled_specific_margin

Outputs saved to: INDIA/rvm_outputs/
    eda/           → EDA plots
    pooled/        → plots for all India combined
    per_state/     → 3 RVM plots per state
    summary.csv    → fraud scores for all states

Usage:
    python india_rvm_analysis.py
    python india_rvm_analysis.py --state "UTTAR PRADESH"
    python india_rvm_analysis.py --runs 30
"""

import os
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.integrate import quad

warnings.filterwarnings("ignore")

# ── global plot style ──────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(BASE_DIR)
OUT_ROOT = os.path.join(PROJ_ROOT, "outputs", "rvm_outputs_india")

# ══════════════════════════════════════════════════════════════
# SECTION 1 — ANALYTICAL FORMULA
# ══════════════════════════════════════════════════════════════

def P_mu(mu):
    """PDF of specific margin µ = M/T (3 candidates, large T)"""
    return (1 - mu) * (5 + 7 * mu) / ((1 + mu)**2 * (1 + 2 * mu)**2)

MU_MEAN, _ = quad(lambda m: m * P_mu(m), 0, 1)   # ≈ 0.2285

def F_x_analytical(x):
    """PDF of scaled specific margin x = µ/<µ>"""
    x   = np.asarray(x, dtype=float)
    mu  = x * MU_MEAN
    out = np.zeros_like(mu)
    ok  = (mu > 0) & (mu < 1)
    out[ok] = MU_MEAN * P_mu(mu[ok])
    return out


# ══════════════════════════════════════════════════════════════
# SECTION 2 — DATA LOADING
# ══════════════════════════════════════════════════════════════

def load_data(path, min_units=50):
    """
    Load India CSV, clean invalid rows, return full DataFrame.
    Uses 'state_n' as the grouping column (analogous to ctr_n in world data).
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    df["state_n"] = df["state_n"].str.strip()

    # validate required columns
    for col in ("vv1", "margin", "state_n", "yr"):
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    before = len(df)
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]
    print(f"  Dropped {before - len(df)} invalid rows")
    print(f"  Valid rows : {len(df):,}")
    print(f"  States     : {df['state_n'].nunique()}")
    print(f"  Years      : {int(df['yr'].min())} – {int(df['yr'].max())}")

    counts   = df.groupby("state_n").size()
    eligible = counts[counts >= min_units].index.tolist()
    skipped  = counts[counts <  min_units].index.tolist()
    print(f"\n  Eligible (≥{min_units} rows) : {len(eligible)} states")
    if skipped:
        print(f"  Skipped  (<{min_units} rows) : {skipped}")

    return df, eligible


# ══════════════════════════════════════════════════════════════
# SECTION 3 — EDA  (India-specific exploratory analysis)
# ══════════════════════════════════════════════════════════════

def run_eda(df, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print("\n  Running EDA...")

    years  = sorted(df["yr"].unique())
    states = sorted(df["state_n"].unique())

    # ── EDA 1: Constituency count per state ────────────────────
    counts = df.groupby("state_n").size().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, max(5, len(counts) * 0.28)))
    colors  = plt.cm.tab20c(np.linspace(0, 1, len(counts)))
    ax.barh(counts.index, counts.values, color=colors, edgecolor="white")
    ax.set_xlabel("Number of Constituency-Election Records", fontsize=11)
    ax.set_title("Constituency Records per State\n(India, all years combined)", fontsize=12)
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda1_records_per_state.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA1: records per state")

    # ── EDA 2: Constituency count per year ─────────────────────
    year_counts = df.groupby("yr").size()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(year_counts.index, year_counts.values, color="#4393c3", edgecolor="white", width=1.8)
    ax.set_xlabel("Election Year", fontsize=11)
    ax.set_ylabel("Number of Constituencies", fontsize=11)
    ax.set_title("Number of Constituencies per Election Year — India", fontsize=12)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
    plt.xticks(rotation=45)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda2_const_per_year.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA2: constituencies per year")

    # ── EDA 3: Distribution of voter turnout ───────────────────
    T = df["vv1"].values
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    ax = axes[0]
    ax.hist(T, bins=60, color="#4393c3", edgecolor="white", density=True)
    ax.set_xlabel("Voter Turnout (vv1)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title("Distribution of Voter Turnout", fontsize=11)

    ax = axes[1]
    ax.hist(T, bins=60, color="#4393c3", edgecolor="white", density=True, log=True)
    ax.set_xlabel("Voter Turnout (vv1)", fontsize=11)
    ax.set_ylabel("Density (log scale)", fontsize=11)
    ax.set_title("Distribution of Voter Turnout (log-y)", fontsize=11)
    fig.suptitle("India Parliamentary Elections — Voter Turnout Distribution", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda3_turnout_dist.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA3: turnout distribution")

    # ── EDA 4: Distribution of margin & specific margin ────────
    M  = df["margin"].values
    mu = M / df["vv1"].values
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(M, bins=60, color="#d73027", edgecolor="white", density=True)
    axes[0].set_xlabel("Margin (M)", fontsize=11)
    axes[0].set_ylabel("Density", fontsize=11)
    axes[0].set_title("Distribution of Vote Margin", fontsize=11)

    axes[1].hist(mu[mu > 0], bins=60, color="#d73027", edgecolor="white", density=True)
    axes[1].set_xlabel(r"Specific  Margin  $\mu = M/T$", fontsize=11)
    axes[1].set_ylabel("Density", fontsize=11)
    axes[1].set_title("Distribution of Specific Margin", fontsize=11)
    fig.suptitle("India Parliamentary Elections — Margin Distributions", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda4_margin_dist.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA4: margin distributions")

    # ── EDA 5: Mean specific margin per state ──────────────────
    state_mu = (
        df.assign(mu=df["margin"] / df["vv1"])
          .groupby("state_n")["mu"].mean()
          .sort_values(ascending=True)
    )
    fig, ax = plt.subplots(figsize=(10, max(5, len(state_mu) * 0.28)))
    colors2  = ["#d73027" if v > state_mu.mean() else "#4393c3" for v in state_mu]
    ax.barh(state_mu.index, state_mu.values, color=colors2, edgecolor="white")
    ax.axvline(state_mu.mean(), color="black", ls="--", lw=1.2, label=f"All-India mean = {state_mu.mean():.3f}")
    ax.set_xlabel(r"Mean Specific Margin $\langle\mu\rangle = \langle M/T \rangle$", fontsize=11)
    ax.set_title("Mean Specific Margin by State\n(red = above average, blue = below)", fontsize=12)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda5_mean_mu_per_state.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA5: mean specific margin per state")

    # ── EDA 6: Mean specific margin over years (trend) ─────────
    year_mu = (
        df.assign(mu=df["margin"] / df["vv1"])
          .groupby("yr")["mu"].mean()
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(year_mu.index, year_mu.values, "o-", color="#2166ac", lw=2, ms=5)
    ax.fill_between(year_mu.index, year_mu.values, alpha=0.15, color="#2166ac")
    ax.axhline(MU_MEAN, color="#d73027", ls="--", lw=1.5,
               label=f"Theoretical <µ> = {MU_MEAN:.4f}")
    ax.set_xlabel("Election Year", fontsize=11)
    ax.set_ylabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=11)
    ax.set_title("Trend of Mean Specific Margin Over Time — India", fontsize=12)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda6_mu_over_years.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA6: µ trend over years")

    # ── EDA 7: Scaled specific margin histogram vs analytical ──
    mu_all  = df["margin"].values / df["vv1"].values
    mu_all  = mu_all[mu_all > 0]
    x_emp   = mu_all / mu_all.mean()
    x_anal  = np.linspace(0, 5, 500)
    Fx_anal = F_x_analytical(x_anal)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(x_emp, bins=80, density=True, color="#4393c3", edgecolor="white",
            alpha=0.6, label="India data")
    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2.5, label="Analytical F(x)")
    ax.set_xlim(0, 5)
    ax.set_xlabel(r"$x = \mu/\langle\mu\rangle$", fontsize=13)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title("Scaled Specific Margin — India vs Analytical Universal Curve", fontsize=11)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda7_scaled_mu_vs_analytical.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA7: scaled µ vs analytical (linear)")

    # ── EDA 8: Scaled margin log-log all India ─────────────────
    scaled_M = df["margin"].values / df["margin"].mean()
    scaled_M = scaled_M[scaled_M > 0]
    bins     = np.logspace(np.log10(scaled_M.min()), np.log10(scaled_M.max()), 56)
    cnts, edges = np.histogram(scaled_M, bins=bins, density=True)
    ctrs    = np.sqrt(edges[:-1] * edges[1:])
    ok      = cnts > 0

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(ctrs[ok], cnts[ok], s=20, facecolors="none",
               edgecolors="#2166ac", lw=0.9, label="India (pooled)", zorder=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$M/\langle M\rangle$", fontsize=13)
    ax.set_ylabel(r"$f(M/\langle M\rangle)$", fontsize=13)
    ax.set_title("Scaled Margin Distribution — All India (pooled)", fontsize=11)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda8_scaled_margin_loglog.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA8: scaled margin log-log (all India)")

    # ── EDA 9: Boxplot of margin by state ──────────────────────
    state_order = (
        df.groupby("state_n")["margin"].median()
          .sort_values(ascending=False).index.tolist()
    )
    data_box = [df[df["state_n"] == s]["margin"].values for s in state_order]
    fig, ax  = plt.subplots(figsize=(14, max(6, len(state_order) * 0.4)))
    bp = ax.boxplot(data_box, vert=False, patch_artist=True,
                    flierprops=dict(marker=".", ms=2, alpha=0.3))
    for patch in bp["boxes"]:
        patch.set_facecolor("#abd9e9")
    ax.set_yticklabels(state_order, fontsize=7)
    ax.set_xlabel("Vote Margin", fontsize=11)
    ax.set_title("Margin Distribution by State (median-sorted) — India", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "eda9_margin_boxplot_by_state.png"), dpi=150)
    plt.close(fig)
    print("    ✓ EDA9: margin boxplot by state")

    # ── EDA 10: Winner vs Runner-up scatter ────────────────────
    if "winner_votes" in df.columns and "runnerup_votes" in df.columns:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(df["winner_votes"], df["runnerup_votes"],
                   s=4, alpha=0.3, color="#4393c3")
        lim = max(df["winner_votes"].max(), df["runnerup_votes"].max())
        ax.plot([0, lim], [0, lim], "r--", lw=1.2, label="Perfect equality line")
        ax.set_xlabel("Winner Votes", fontsize=11)
        ax.set_ylabel("Runner-up Votes", fontsize=11)
        ax.set_title("Winner vs Runner-up Votes — India (all elections)", fontsize=11)
        ax.legend(fontsize=9)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "eda10_winner_vs_runnerup.png"), dpi=150)
        plt.close(fig)
        print("    ✓ EDA10: winner vs runner-up scatter")

    print(f"  EDA plots saved to: {out_dir}")


# ══════════════════════════════════════════════════════════════
# SECTION 4 — RVM SIMULATION
# ══════════════════════════════════════════════════════════════

def rvm_once(turnouts, rng, n_cand=3):
    N = len(turnouts)
    margins = np.empty(N)
    for i, T in enumerate(turnouts):
        T = max(int(T), 2)
        w     = rng.uniform(0, 1, n_cand)
        p     = w / w.sum()
        votes = rng.multinomial(T, p)
        s     = np.sort(votes)[::-1]
        margins[i] = s[0] - s[1]
    return margins

def rvm_ensemble(turnouts, n_runs=25, seed=0):
    rng     = np.random.default_rng(seed)
    results = []
    for k in range(n_runs):
        m  = rvm_once(turnouts, rng)
        mu = m / turnouts
        results.append((m, mu))
        if (k + 1) % 10 == 0:
            print(f"    RVM {k+1}/{n_runs} done")
    return results


# ══════════════════════════════════════════════════════════════
# SECTION 5 — HISTOGRAM HELPER
# ══════════════════════════════════════════════════════════════

def log_histogram(values, n_bins=55):
    v = np.asarray(values, dtype=float)
    v = v[v > 0]
    if len(v) < 5:
        return np.array([]), np.array([])
    bins    = np.logspace(np.log10(v.min()), np.log10(v.max()), n_bins + 1)
    counts, edges = np.histogram(v, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])
    ok      = counts > 0
    return centers[ok], counts[ok]

def rvm_mean_std(rvm_results, extractor, ref_x, n_bins=55):
    pdfs = []
    for (m, mu) in rvm_results:
        xr, yr = log_histogram(extractor(m, mu), n_bins)
        if len(xr) == 0:
            continue
        pdfs.append(np.interp(ref_x, xr, yr, left=np.nan, right=np.nan))
    mat = np.array(pdfs)
    return np.nanmean(mat, axis=0), np.nanstd(mat, axis=0)


# ══════════════════════════════════════════════════════════════
# SECTION 6 — THREE CORE RVM PLOTS  (same as world script)
# ══════════════════════════════════════════════════════════════

def plot_scaled_margin(T, M, rvm_results, label, save_path):
    scaled_M    = M / M.mean()
    xe, ye      = log_histogram(scaled_M)
    rvm0_scaled = rvm_results[0][0] / rvm_results[0][0].mean()
    xr, _       = log_histogram(rvm0_scaled)
    rm, rs      = rvm_mean_std(rvm_results, lambda m, mu: m / m.mean(), xr)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs, color="gray", alpha=0.3)
    ax.plot(xr, rm, "k-", lw=2, label="RVM prediction")
    ax.scatter(xe, ye, s=20, facecolors="none",
               edgecolors="#2166ac", lw=0.9, label=f"{label} (data)", zorder=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$M\,/\,\langle M \rangle$", fontsize=13)
    ax.set_ylabel(r"$f\!\left(M/\langle M\rangle\right)$", fontsize=13)
    ax.set_title(f"Scaled Margin Distribution — {label}", fontsize=11)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_universal_Fx(T, M, rvm_results, label, save_path):
    mu_emp  = M / T
    x_emp   = mu_emp / mu_emp.mean()
    xb, Fxb = log_histogram(x_emp)
    rvm0_x  = rvm_results[0][1] / rvm_results[0][1].mean()
    xr, _   = log_histogram(rvm0_x)
    rm, rs  = rvm_mean_std(rvm_results, lambda m, mu: mu / mu.mean(), xr)
    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs, color="gray", alpha=0.25)
    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2.5, label="Analytical F(x)", zorder=5)
    ax.plot(xr, rm, "k--", lw=1.5, label="RVM", zorder=4)
    ax.scatter(xb, Fxb, s=20, facecolors="none",
               edgecolors="#2166ac", lw=0.9, label=f"{label} (data)", zorder=6)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=13)
    ax.set_ylabel(r"$F(x)$", fontsize=13)
    ax.set_title(f"Universal F(x) — {label}", fontsize=11)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_fraud_check(T, M, rvm_results, label, save_path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # left panel
    scaled_M   = M / M.mean()
    xe, ye     = log_histogram(scaled_M)
    rvm0_sm    = rvm_results[0][0] / rvm_results[0][0].mean()
    xr_m, _    = log_histogram(rvm0_sm)
    rm_m, rs_m = rvm_mean_std(rvm_results, lambda m, mu: m / m.mean(), xr_m)

    ax = axes[0]
    ax.fill_between(xr_m, np.clip(rm_m - rs_m, 1e-5, None), rm_m + rs_m,
                    color="#f4a582", alpha=0.5)
    ax.plot(xr_m, rm_m, "-", color="#d73027", lw=2, label="RVM")
    ax.scatter(xe, ye, s=15, facecolors="none",
               edgecolors="#4393c3", lw=0.9, label=label)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$M/\langle M\rangle$", fontsize=12)
    ax.set_ylabel(r"$f(M/\langle M\rangle)$", fontsize=12)
    ax.set_title(f"(a) Scaled Margin — {label}", fontsize=10)
    ax.legend(fontsize=9)

    # right panel
    mu_emp  = M / T
    x_emp   = mu_emp / mu_emp.mean()
    xb, Fxb = log_histogram(x_emp)
    rvm0_x  = rvm_results[0][1] / rvm_results[0][1].mean()
    xr_x, _ = log_histogram(rvm0_x)
    rm_x, rs_x = rvm_mean_std(rvm_results, lambda m, mu: mu / mu.mean(), xr_x)
    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)

    Fxb_ref = np.interp(xr_x, xb, Fxb, left=np.nan, right=np.nan)
    with np.errstate(invalid="ignore"):
        z_scores = np.abs(Fxb_ref - rm_x) / (rs_x + 1e-10)
    mean_z  = float(np.nanmean(z_scores))
    flagged = mean_z > 3.0

    ax = axes[1]
    ax.fill_between(xr_x, np.clip(rm_x - rs_x, 1e-5, None), rm_x + rs_x,
                    color="#f4a582", alpha=0.5, label="RVM band")
    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2, label="Analytical F(x)")
    ax.scatter(xb, Fxb, s=15, facecolors="none",
               edgecolors="#4393c3", lw=0.9, label=label)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu/\langle\mu\rangle$", fontsize=12)
    ax.set_ylabel(r"$F(x)$", fontsize=12)
    ax.set_title(f"(b) Universal F(x) — {label}", fontsize=10)
    ax.legend(fontsize=9)

    color_z = "firebrick" if flagged else "green"
    label_z = f"Mean |z| = {mean_z:.2f}  {'⚠ FLAGGED' if flagged else '✓ OK'}"
    ax.text(0.03, 0.04, label_z, transform=ax.transAxes, fontsize=9,
            color=color_z, va="bottom",
            bbox=dict(boxstyle="round,pad=0.3",
                      facecolor="#fff0f0" if flagged else "#f0fff0",
                      edgecolor=color_z))

    fig.suptitle(f"Deviation Check — {label}", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return mean_z, flagged


# ══════════════════════════════════════════════════════════════
# SECTION 7 — ALL STATES F(x) OVERLAY
# ══════════════════════════════════════════════════════════════

def plot_all_states_Fx(df, eligible, rvm_cache, save_path):
    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)
    xb_ref  = np.logspace(-1.2, 0.7, 80)

    cmap   = plt.cm.get_cmap("tab20", len(eligible))
    fig, ax = plt.subplots(figsize=(8, 6))

    all_Fx = []
    for i, state in enumerate(eligible):
        sub    = df[df["state_n"] == state]
        T      = sub["vv1"].values.astype(float)
        M      = sub["margin"].values.astype(float)
        mu_emp = M / T
        x_emp  = mu_emp / mu_emp.mean()
        xb, Fxb = log_histogram(x_emp)
        if len(xb) == 0:
            continue
        ax.scatter(xb, Fxb, s=8, color=cmap(i), alpha=0.55, zorder=3)
        all_Fx.append(np.interp(xb_ref, xb, Fxb, left=np.nan, right=np.nan))

    avg_Fx = np.nanmean(all_Fx, axis=0)
    ok     = ~np.isnan(avg_Fx)
    ax.scatter(xb_ref[ok], avg_Fx[ok], s=45, facecolors="none",
               edgecolors="red", lw=1.5, zorder=5, label="Average (all states)")

    all_rvm_Fx = []
    for state in eligible:
        if state not in rvm_cache:
            continue
        rvm    = rvm_cache[state]
        rvm0x  = rvm[0][1] / rvm[0][1].mean()
        xrr, _ = log_histogram(rvm0x)
        rm, _  = rvm_mean_std(rvm, lambda m, mu: mu / mu.mean(), xrr)
        all_rvm_Fx.append(np.interp(xb_ref, xrr, rm, left=np.nan, right=np.nan))
    avg_rvm = np.nanmean(all_rvm_Fx, axis=0)
    ok2     = ~np.isnan(avg_rvm)
    ax.scatter(xb_ref[ok2], avg_rvm[ok2], s=45, facecolors="none",
               edgecolors="black", lw=1.5, zorder=4, label="RVM average")

    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2.5,
            label="Analytical F(x)", zorder=6)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 6); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=13)
    ax.set_ylabel(r"$F(x)$", fontsize=13)
    ax.set_title(f"Universal F(x) — All {len(eligible)} States\n(each colour = one state)", fontsize=11)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")


# ══════════════════════════════════════════════════════════════
# SECTION 8 — FRAUD BAR CHART
# ══════════════════════════════════════════════════════════════

def plot_fraud_barchart(summary_df, save_path):
    s      = summary_df.sort_values("fraud_score", ascending=True)
    colors = ["#d73027" if f else "#4393c3" for f in s["flagged"]]

    fig, ax = plt.subplots(figsize=(9, max(5, len(s) * 0.35)))
    bars = ax.barh(s["state"], s["fraud_score"],
                   color=colors, edgecolor="white", height=0.7)
    ax.axvline(3.0, color="firebrick", ls="--", lw=1.5,
               label="Fraud threshold (|z| = 3)")
    for bar, val, flag in zip(bars, s["fraud_score"], s["flagged"]):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}" + ("  ⚠" if flag else ""),
                va="center", fontsize=8,
                color="firebrick" if flag else "black")
    ax.set_xlabel("Fraud Score  (mean |z|)", fontsize=11)
    ax.set_title("Fraud Indicator Score by State — India\n"
                 "(red = flagged, threshold = 3.0)", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(0, s["fraud_score"].max() * 1.2 + 0.5)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")


# ══════════════════════════════════════════════════════════════
# SECTION 9 — MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="India RVM Analysis — State-wise Election Universality & Fraud Detection"
    )
    parser.add_argument("--data",      default=os.path.join(PROJ_ROOT, "data", "processed", "finallllllll.csv"),
                        help="Path to India CSV (default: data/processed/finallllllll.csv)")
    parser.add_argument("--state",     default=None, help="Run single state only")
    parser.add_argument("--runs",      type=int, default=25,
                        help="RVM ensemble runs per state (default: 25)")
    parser.add_argument("--min-units", type=int, default=50,
                        help="Min rows per state (default: 50)")
    parser.add_argument("--seed",      type=int, default=42)
    parser.add_argument("--skip-eda",  action="store_true", help="Skip EDA section")
    args = parser.parse_args()

    # ── output folders ────────────────────────────────────────
    OUT_EDA     = os.path.join(OUT_ROOT, "eda")
    OUT_POOLED  = os.path.join(OUT_ROOT, "pooled")
    OUT_STATE   = os.path.join(OUT_ROOT, "per_state")
    for d in (OUT_EDA, OUT_POOLED, OUT_STATE):
        os.makedirs(d, exist_ok=True)

    print("\n" + "═"*60)
    print("  India RVM Analysis — Parliamentary Elections")
    print("═"*60)

    # ── load ──────────────────────────────────────────────────
    print(f"\nLoading {args.data}...")
    df, eligible = load_data(args.data, min_units=args.min_units)

    # ── EDA ───────────────────────────────────────────────────
    if not args.skip_eda:
        run_eda(df, OUT_EDA)

    # ── single state mode ─────────────────────────────────────
    if args.state:
        state_match = args.state.strip().upper()
        if state_match not in df["state_n"].values:
            print(f"State '{state_match}' not found.")
            print(f"Available: {sorted(df['state_n'].unique())}")
            return
        states_to_run = [state_match]
    else:
        states_to_run = eligible

    # ── per-state loop ────────────────────────────────────────
    summary_rows = []
    rvm_cache    = {}

    for state in states_to_run:
        sub = df[df["state_n"] == state]
        T   = sub["vv1"].values.astype(float)
        M   = sub["margin"].values.astype(float)
        n   = len(sub)
        yr_range = f"{int(sub['yr'].min())}–{int(sub['yr'].max())}"

        print(f"\n{'─'*55}")
        print(f"  {state}  ({n:,} rows, {yr_range})")
        print(f"  Mean T={T.mean():,.0f}  Mean M={M.mean():,.0f}  "
              f"Mean µ={(M/T).mean():.4f}")

        rvm = rvm_ensemble(T, n_runs=args.runs, seed=args.seed)
        rvm_cache[state] = rvm

        safe = state.replace(" ", "_").replace("/", "-")

        # Plot A
        plot_scaled_margin(T, M, rvm, state,
                           os.path.join(OUT_STATE, f"{safe}_fig1_scaled_margin.png"))
        print(f"  ✓ scaled margin plot saved")

        # Plot B
        plot_universal_Fx(T, M, rvm, state,
                          os.path.join(OUT_STATE, f"{safe}_fig2_universal_Fx.png"))
        print(f"  ✓ universal F(x) plot saved")

        # Plot C
        mean_z, flagged = plot_fraud_check(
            T, M, rvm, state,
            os.path.join(OUT_STATE, f"{safe}_fig3_fraud_check.png")
        )
        verdict = "⚠ FLAGGED" if flagged else "✓ OK"
        print(f"  Fraud score: {mean_z:.3f}  {verdict}")

        summary_rows.append({
            "state":           state,
            "n_units":         n,
            "yr_min":          int(sub["yr"].min()),
            "yr_max":          int(sub["yr"].max()),
            "mean_T":          round(T.mean(), 1),
            "mean_M":          round(M.mean(), 1),
            "mean_mu":         round((M/T).mean(), 6),
            "mu_analytical":   round(MU_MEAN, 6),
            "fraud_score":     round(mean_z, 3),
            "flagged":         flagged,
        })

    # ── pooled plot (all India) ────────────────────────────────
    if not args.state:
        print(f"\n{'─'*55}")
        print("  Generating pooled plots (all India)...")
        T_all = df[df["state_n"].isin(eligible)]["vv1"].values.astype(float)
        M_all = df[df["state_n"].isin(eligible)]["margin"].values.astype(float)
        rvm_all = rvm_ensemble(T_all, n_runs=args.runs, seed=args.seed)

        plot_scaled_margin(T_all, M_all, rvm_all, "All India (pooled)",
                           os.path.join(OUT_POOLED, "fig1_scaled_margin_pooled.png"))
        plot_universal_Fx(T_all, M_all, rvm_all, "All India (pooled)",
                          os.path.join(OUT_POOLED, "fig2_universal_Fx_pooled.png"))
        plot_fraud_check(T_all, M_all, rvm_all, "All India (pooled)",
                         os.path.join(OUT_POOLED, "fig3_fraud_check_pooled.png"))
        plot_all_states_Fx(df, eligible, rvm_cache,
                           os.path.join(OUT_POOLED, "fig4_all_states_Fx_overlay.png"))

    # ── summary CSV + fraud bar chart ─────────────────────────
    summary_df  = pd.DataFrame(summary_rows)
    summary_df  = summary_df.sort_values("fraud_score", ascending=False)
    summary_path = os.path.join(OUT_ROOT, "summary.csv")
    summary_df.to_csv(summary_path, index=False)

    if len(summary_df) > 1:
        plot_fraud_barchart(summary_df,
                            os.path.join(OUT_ROOT, "fraud_barchart.png"))

    # ── final ranking ─────────────────────────────────────────
    print("\n" + "═"*60)
    print("  FRAUD SCORE RANKING — STATES")
    print("═"*60)
    cols = ["state", "n_units", "mean_mu", "fraud_score", "flagged"]
    print(summary_df[cols].to_string(index=False))
    print(f"\n  Saved summary: {summary_path}")
    print(f"  EDA plots    : {OUT_EDA}/")
    print(f"  State plots  : {OUT_STATE}/  ({len(states_to_run)*3} files)")
    print(f"  Pooled plots : {OUT_POOLED}/")
    print("\n" + "═"*60)
    print("  All done.")
    print("═"*60)


if __name__ == "__main__":
    main()
