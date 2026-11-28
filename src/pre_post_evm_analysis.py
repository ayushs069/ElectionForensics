"""
Pre-EVM vs Post-EVM Indian Parliamentary Election Analysis
===========================================================
Reuses the RVM methodology from india_rvm_analysis.py.

Dataset : data/processed/final_20const_14states.csv
Cutoff  : 2004 (nationwide EVM adoption)
  Pre-EVM  : 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999
  Post-EVM : 2004, 2009, 2014, 2019
  Excluded : 1985 (by-elections, n=27), 1992 (by-elections, n=13)

Outputs  : outputs/pre vs post evm analysis/
             figures/, tables/, data/, reports/, logs/

Usage:
    python src/pre_post_evm_analysis.py
    python src/pre_post_evm_analysis.py --runs 30 --dpi 600
"""

import os
import sys
import json
import warnings
import argparse
import logging
import datetime
import platform
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from scipy.integrate import quad
from scipy import stats

warnings.filterwarnings("ignore")

# ── plot style (mirrors india_rvm_analysis.py) ────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
    "font.size":         11,
})

# ── paths ─────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJ_ROOT, "data", "processed", "final_20const_14states.csv")
OUT_ROOT  = os.path.join(PROJ_ROOT, "outputs", "pre vs post evm analysis")

# Subfolders
OUT_FIG     = os.path.join(OUT_ROOT, "figures")
OUT_TAB     = os.path.join(OUT_ROOT, "tables")
OUT_DATA    = os.path.join(OUT_ROOT, "data")
OUT_REP     = os.path.join(OUT_ROOT, "reports")
OUT_LOG     = os.path.join(OUT_ROOT, "logs")

# ── EVM epoch definitions ──────────────────────────────────────
# Standard general elections only; 1985 & 1992 are by-election batches
EXCLUDED_YEARS = {1985, 1992}
PRE_EVM_YEARS  = {1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999}
POST_EVM_YEARS = {2004, 2009, 2014, 2019}
EVM_CUTOFF     = 2004

# colour palette
C_PRE     = "#2166ac"   # blue  — pre-EVM
C_POST    = "#d73027"   # red   — post-EVM
C_ANAL    = "#1a9641"   # green — analytical
C_RVM     = "#636363"   # grey  — RVM band

# ══════════════════════════════════════════════════════════════
# SECTION 1 — ANALYTICAL FORMULA  (identical to india_rvm_analysis.py)
# ══════════════════════════════════════════════════════════════

def P_mu(mu):
    """PDF of specific margin µ = M/T for 3-candidate RVM (large T)."""
    return (1 - mu) * (5 + 7 * mu) / ((1 + mu)**2 * (1 + 2 * mu)**2)

MU_MEAN, _ = quad(lambda m: m * P_mu(m), 0, 1)   # ≈ 0.2285

def F_x_analytical(x):
    """PDF of scaled specific margin x = µ/<µ>."""
    x   = np.asarray(x, dtype=float)
    mu  = x * MU_MEAN
    out = np.zeros_like(mu)
    ok  = (mu > 0) & (mu < 1)
    out[ok] = MU_MEAN * P_mu(mu[ok])
    return out

# ══════════════════════════════════════════════════════════════
# SECTION 2 — RVM SIMULATION  (identical to india_rvm_analysis.py)
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

def rvm_ensemble(turnouts, n_runs=25, seed=42, label=""):
    rng     = np.random.default_rng(seed)
    results = []
    for k in range(n_runs):
        m  = rvm_once(turnouts, rng)
        mu = m / np.maximum(turnouts, 1)
        results.append((m, mu))
    print(f"    RVM ensemble done ({n_runs} runs) [{label}]")
    return results

# ══════════════════════════════════════════════════════════════
# SECTION 3 — HISTOGRAM HELPER  (identical to india_rvm_analysis.py)
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
# SECTION 4 — DATA LOADING
# ══════════════════════════════════════════════════════════════

def load_and_split(path, log):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    df["state_n"] = df["state_n"].str.strip().str.upper()

    for col in ("vv1", "margin", "state_n", "yr"):
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    # Remove invalid rows
    before = len(df)
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]
    log.info(f"Dropped {before - len(df)} invalid rows; {len(df):,} remain")

    all_years = sorted(df["yr"].unique())
    log.info(f"All years in dataset: {all_years}")

    # Identify year categories
    excl  = [y for y in all_years if y in EXCLUDED_YEARS]
    pre   = [y for y in all_years if y in PRE_EVM_YEARS]
    post  = [y for y in all_years if y in POST_EVM_YEARS]
    other = [y for y in all_years if y not in PRE_EVM_YEARS | POST_EVM_YEARS | EXCLUDED_YEARS]

    log.info(f"Pre-EVM  years present : {pre}")
    log.info(f"Post-EVM years present : {post}")
    log.info(f"Excluded years         : {excl}")
    log.info(f"Other/unclassified     : {other}")

    # Standard elections only
    df_std  = df[~df["yr"].isin(EXCLUDED_YEARS)].copy()
    df_pre  = df_std[df_std["yr"].isin(PRE_EVM_YEARS)].copy()
    df_post = df_std[df_std["yr"].isin(POST_EVM_YEARS)].copy()

    states_14 = sorted(df["state_n"].unique())
    log.info(f"States ({len(states_14)}): {states_14}")
    log.info(f"Pre-EVM  rows : {len(df_pre):,}  ({len(pre)} elections)")
    log.info(f"Post-EVM rows : {len(df_post):,}  ({len(post)} elections)")

    return df, df_pre, df_post, states_14, pre, post, excl

# ══════════════════════════════════════════════════════════════
# SECTION 5 — STATISTICAL TESTS
# ══════════════════════════════════════════════════════════════

def compute_stats(mu_pre, mu_post):
    """Return dict of descriptive stats + hypothesis tests."""
    n_pre, n_post = len(mu_pre), len(mu_post)

    res = {
        "n_pre":    n_pre,
        "n_post":   n_post,
        "mean_pre":   float(np.mean(mu_pre)),
        "mean_post":  float(np.mean(mu_post)),
        "median_pre": float(np.median(mu_pre)),
        "median_post":float(np.median(mu_post)),
        "std_pre":    float(np.std(mu_pre, ddof=1)),
        "std_post":   float(np.std(mu_post, ddof=1)),
    }

    # 95% CI for means
    se_pre  = stats.sem(mu_pre)
    se_post = stats.sem(mu_post)
    res["ci95_pre"]  = (res["mean_pre"]  - 1.96*se_pre,  res["mean_pre"]  + 1.96*se_pre)
    res["ci95_post"] = (res["mean_post"] - 1.96*se_post, res["mean_post"] + 1.96*se_post)

    # Mann-Whitney U (non-parametric)
    u_stat, p_mw = stats.mannwhitneyu(mu_pre, mu_post, alternative="two-sided")
    res["mannwhitney_U"] = float(u_stat)
    res["mannwhitney_p"] = float(p_mw)

    # Kolmogorov-Smirnov
    ks_stat, p_ks = stats.ks_2samp(mu_pre, mu_post)
    res["ks_stat"] = float(ks_stat)
    res["ks_p"]    = float(p_ks)

    # Effect size: Cohen's d
    pooled_std = np.sqrt(((n_pre-1)*np.var(mu_pre,ddof=1) + (n_post-1)*np.var(mu_post,ddof=1))
                         / (n_pre + n_post - 2))
    res["cohens_d"] = float((res["mean_pre"] - res["mean_post"]) / pooled_std) if pooled_std > 0 else np.nan

    # Relative change
    res["rel_change_pct"] = float(100 * (res["mean_post"] - res["mean_pre"]) / res["mean_pre"])

    return res

def fraud_score(T, M, rvm_results):
    """Compute mean |z| score vs RVM band (matches india_rvm_analysis.py)."""
    mu_emp  = M / T
    x_emp   = mu_emp / mu_emp.mean()
    xb, Fxb = log_histogram(x_emp)
    if len(xb) == 0:
        return np.nan, False

    rvm0_x  = rvm_results[0][1] / rvm_results[0][1].mean()
    xr, _   = log_histogram(rvm0_x)
    rm, rs  = rvm_mean_std(rvm_results, lambda m, mu: mu / mu.mean(), xr)

    Fxb_ref = np.interp(xr, xb, Fxb, left=np.nan, right=np.nan)
    with np.errstate(invalid="ignore"):
        z = np.abs(Fxb_ref - rm) / (rs + 1e-10)
    mz = float(np.nanmean(z))
    return mz, (mz > 3.0)

# ══════════════════════════════════════════════════════════════
# SECTION 6 — FIGURE: POOLED F(x) SIDE-BY-SIDE
# ══════════════════════════════════════════════════════════════

def fig_pooled_Fx(T_pre, M_pre, T_post, M_post,
                  rvm_pre, rvm_post, dpi, out_dir):
    """Figure 1: Pre vs Post F(x) + analytical + RVM, side-by-side."""
    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    fig.suptitle("Universal Scaled-Margin Distribution F(x)\nPre-EVM (1951–1999) vs Post-EVM (2004–2019)",
                 fontsize=13, y=1.02)

    for ax, T, M, rvm, label, color, yrs in [
        (axes[0], T_pre,  M_pre,  rvm_pre,  "Pre-EVM (1951–1999)",  C_PRE,  "1951–1999"),
        (axes[1], T_post, M_post, rvm_post, "Post-EVM (2004–2019)", C_POST, "2004–2019"),
    ]:
        mu_emp = M / T
        x_emp  = mu_emp / mu_emp.mean()
        xb, Fxb = log_histogram(x_emp)

        rvm0_x  = rvm[0][1] / rvm[0][1].mean()
        xr, _   = log_histogram(rvm0_x)
        rm, rs  = rvm_mean_std(rvm, lambda m, mu: mu / mu.mean(), xr)

        ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs,
                        color=C_RVM, alpha=0.25, label="RVM band")
        ax.plot(x_anal, Fx_anal, "-", color=C_ANAL, lw=2.5,
                label="Analytical F(x)", zorder=5)
        ax.plot(xr, rm, "k--", lw=1.5, label="RVM mean", zorder=4)
        ax.scatter(xb, Fxb, s=22, facecolors="none",
                   edgecolors=color, lw=1.1, label=label, zorder=6)

        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
        ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=12)
        ax.set_ylabel(r"$F(x)$", fontsize=12)
        ax.set_title(f"{label}\n(n = {len(M):,})", fontsize=11)
        ax.legend(fontsize=9, loc="upper right")

    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig01_pooled_Fx_pre_vs_post.png")
    path_pdf = os.path.join(out_dir, "fig01_pooled_Fx_pre_vs_post.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 1 saved: {os.path.basename(path_png)}")
    return path_png


def fig_pooled_scaled_margin(T_pre, M_pre, T_post, M_post,
                              rvm_pre, rvm_post, dpi, out_dir):
    """Figure 2: Scaled margin M/<M> log-log, side-by-side."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
    fig.suptitle("Scaled Margin Distribution  M/⟨M⟩\nPre-EVM vs Post-EVM",
                 fontsize=13, y=1.02)

    for ax, T, M, rvm, label, color in [
        (axes[0], T_pre,  M_pre,  rvm_pre,  "Pre-EVM (1951–1999)",  C_PRE),
        (axes[1], T_post, M_post, rvm_post, "Post-EVM (2004–2019)", C_POST),
    ]:
        xe, ye = log_histogram(M / M.mean())
        rvm0_sm = rvm[0][0] / rvm[0][0].mean()
        xr, _   = log_histogram(rvm0_sm)
        rm, rs  = rvm_mean_std(rvm, lambda m, mu: m / m.mean(), xr)

        ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs,
                        color=C_RVM, alpha=0.3)
        ax.plot(xr, rm, "k-", lw=2, label="RVM prediction")
        ax.scatter(xe, ye, s=22, facecolors="none",
                   edgecolors=color, lw=1.1, label=label, zorder=4)

        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
        ax.set_xlabel(r"$M\,/\,\langle M \rangle$", fontsize=12)
        ax.set_ylabel(r"$f(M/\langle M\rangle)$", fontsize=12)
        ax.set_title(f"{label}\n(n = {len(M):,})", fontsize=11)
        ax.legend(fontsize=9)

    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig02_pooled_scaled_margin.png")
    path_pdf = os.path.join(out_dir, "fig02_pooled_scaled_margin.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 2 saved: {os.path.basename(path_png)}")
    return path_png


def fig_mean_margin_comparison(stats_dict, dpi, out_dir):
    """Figure 3: Mean & median specific margin pre vs post, with CI bars."""
    labels   = ["Pre-EVM\n(1951–1999)", "Post-EVM\n(2004–2019)"]
    means    = [stats_dict["mean_pre"],   stats_dict["mean_post"]]
    medians  = [stats_dict["median_pre"], stats_dict["median_post"]]
    ci_lo    = [stats_dict["ci95_pre"][0],  stats_dict["ci95_post"][0]]
    ci_hi    = [stats_dict["ci95_pre"][1],  stats_dict["ci95_post"][1]]
    yerr_lo  = [m - lo for m, lo in zip(means, ci_lo)]
    yerr_hi  = [hi - m for m, hi in zip(means, ci_hi)]
    colors   = [C_PRE, C_POST]
    x        = np.arange(2)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    # Panel A: Mean + CI
    ax = axes[0]
    bars = ax.bar(x, means, color=colors, edgecolor="white", width=0.5, alpha=0.85)
    ax.errorbar(x, means, yerr=[yerr_lo, yerr_hi],
                fmt="none", color="black", capsize=6, lw=1.5)
    ax.axhline(MU_MEAN, color=C_ANAL, ls="--", lw=1.5,
               label=f"Theoretical ⟨μ⟩ = {MU_MEAN:.4f}")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=11)
    ax.set_title("(a) Mean Specific Margin ± 95% CI", fontsize=11)
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.002,
                f"{val:.4f}", ha="center", fontsize=10, color="black")
    ax.legend(fontsize=9)

    # Panel B: Median
    ax = axes[1]
    ax.bar(x, medians, color=colors, edgecolor="white", width=0.5, alpha=0.85)
    ax.axhline(MU_MEAN, color=C_ANAL, ls="--", lw=1.5,
               label=f"Theoretical ⟨μ⟩ = {MU_MEAN:.4f}")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel(r"Median Specific Margin", fontsize=11)
    ax.set_title("(b) Median Specific Margin", fontsize=11)
    for i, val in enumerate(medians):
        ax.text(i, val + 0.002, f"{val:.4f}", ha="center", fontsize=10)
    ax.legend(fontsize=9)

    d  = stats_dict["cohens_d"]
    rc = stats_dict["rel_change_pct"]
    fig.suptitle(
        f"Mean Margin Comparison — Pooled 14 States\n"
        f"Cohen's d = {d:.3f}  |  Relative change = {rc:+.1f}%  |  "
        f"KS p = {stats_dict['ks_p']:.2e}",
        fontsize=11, y=1.02
    )
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig03_mean_margin_comparison.png")
    path_pdf = os.path.join(out_dir, "fig03_mean_margin_comparison.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 3 saved: {os.path.basename(path_png)}")
    return path_png


def fig_sample_sizes(states, n_pre_s, n_post_s, dpi, out_dir):
    """Figure 4: Sample size per state, pre vs post (grouped bar)."""
    x  = np.arange(len(states))
    w  = 0.38
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.bar(x - w/2, n_pre_s,  w, color=C_PRE,  label="Pre-EVM",  alpha=0.85, edgecolor="white")
    ax.bar(x + w/2, n_post_s, w, color=C_POST, label="Post-EVM", alpha=0.85, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels([s.title() for s in states], rotation=35, ha="right", fontsize=8.5)
    ax.set_ylabel("Number of Constituency-Elections", fontsize=11)
    ax.set_title("Sample Size per State — Pre-EVM vs Post-EVM", fontsize=12)
    ax.legend(fontsize=10)
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig04_sample_sizes.png")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 4 saved: {os.path.basename(path_png)}")
    return path_png


def fig_statewise_mean_margin(states, pre_means, post_means, dpi, out_dir):
    """Figure 5: State-wise mean specific margin, Pre vs Post."""
    x  = np.arange(len(states))
    w  = 0.38
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.bar(x - w/2, pre_means,  w, color=C_PRE,  label="Pre-EVM",  alpha=0.85, edgecolor="white")
    ax.bar(x + w/2, post_means, w, color=C_POST, label="Post-EVM", alpha=0.85, edgecolor="white")
    ax.axhline(MU_MEAN, color=C_ANAL, ls="--", lw=1.5,
               label=f"Theoretical ⟨μ⟩ = {MU_MEAN:.4f}")
    ax.set_xticks(x)
    ax.set_xticklabels([s.title() for s in states], rotation=35, ha="right", fontsize=8.5)
    ax.set_ylabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=11)
    ax.set_title("State-wise Mean Specific Margin — Pre-EVM vs Post-EVM", fontsize=12)
    ax.legend(fontsize=10)
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig05_statewise_mean_margin.png")
    path_pdf = os.path.join(out_dir, "fig05_statewise_mean_margin.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 5 saved: {os.path.basename(path_png)}")
    return path_png


def fig_statewise_Fx_grid(df_pre, df_post, states, rvm_runs, seed, dpi, out_dir):
    """Figure 6: 14-panel grid, one F(x) per state, Pre vs Post overlay."""
    n   = len(states)
    ncols = 4
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*4.5, nrows*4.2))
    fig.suptitle("State-wise Universal F(x) — Pre-EVM (blue) vs Post-EVM (red)",
                 fontsize=13, y=1.005)
    axes_flat = axes.flatten()

    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)

    for idx, state in enumerate(states):
        ax    = axes_flat[idx]
        for df_s, color, era in [(df_pre, C_PRE, "Pre"), (df_post, C_POST, "Post")]:
            sub = df_s[df_s["state_n"] == state]
            if len(sub) < 10:
                continue
            T = sub["vv1"].values.astype(float)
            M = sub["margin"].values.astype(float)
            mu_emp = M / T
            x_emp  = mu_emp / mu_emp.mean()
            xb, Fxb = log_histogram(x_emp)
            if len(xb) == 0:
                continue
            rvm = rvm_ensemble(T, n_runs=rvm_runs, seed=seed, label=f"{state} {era}")
            rvm0_x  = rvm[0][1] / rvm[0][1].mean()
            xr, _   = log_histogram(rvm0_x)
            rm, rs  = rvm_mean_std(rvm, lambda m, mu: mu / mu.mean(), xr)
            ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs,
                            color=color, alpha=0.12)
            ax.plot(xr, rm, "--", color=color, lw=1.2, alpha=0.7)
            ax.scatter(xb, Fxb, s=12, facecolors="none",
                       edgecolors=color, lw=0.8, label=f"{era} (n={len(M)})", zorder=4)

        ax.plot(x_anal, Fx_anal, "-", color=C_ANAL, lw=1.8, alpha=0.8, zorder=5)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
        ax.set_title(state.title(), fontsize=9)
        ax.set_xlabel(r"$x$", fontsize=8)
        ax.set_ylabel(r"$F(x)$", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=7, loc="upper right")

    # Hide empty panels
    for idx in range(n, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig06_statewise_Fx_grid.png")
    path_pdf = os.path.join(out_dir, "fig06_statewise_Fx_grid.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 6 saved: {os.path.basename(path_png)}")
    return path_png


def fig_fraud_score_comparison(state_rows, dpi, out_dir):
    """Figure 7: Fraud score (mean |z|) Pre vs Post per state."""
    df_s  = pd.DataFrame(state_rows).sort_values("fraud_pre", ascending=True)
    states = df_s["state"].tolist()
    x  = np.arange(len(states))
    w  = 0.38
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(x - w/2, df_s["fraud_pre"],  w, color=C_PRE,  label="Pre-EVM",  alpha=0.85, edgecolor="white")
    ax.bar(x + w/2, df_s["fraud_post"], w, color=C_POST, label="Post-EVM", alpha=0.85, edgecolor="white")
    ax.axhline(3.0, color="firebrick", ls="--", lw=1.5, label="Threshold |z|=3")
    ax.set_xticks(x)
    ax.set_xticklabels([s.title() for s in states], rotation=35, ha="right", fontsize=8.5)
    ax.set_ylabel("Fraud Score (mean |z|)", fontsize=11)
    ax.set_title("RVM Deviation Score per State — Pre-EVM vs Post-EVM\n"
                 "(Higher = larger deviation from random-voting model)", fontsize=11)
    ax.legend(fontsize=10)
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig07_fraud_score_comparison.png")
    path_pdf = os.path.join(out_dir, "fig07_fraud_score_comparison.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 7 saved: {os.path.basename(path_png)}")
    return path_png


def fig_mu_distribution_kde(mu_pre, mu_post, dpi, out_dir):
    """Figure 8: KDE of specific margin distributions, pre vs post."""
    from scipy.stats import gaussian_kde
    fig, ax = plt.subplots(figsize=(9, 5))
    for mu, color, label in [
        (mu_pre,  C_PRE,  f"Pre-EVM  (n={len(mu_pre):,})"),
        (mu_post, C_POST, f"Post-EVM (n={len(mu_post):,})"),
    ]:
        kde  = gaussian_kde(mu, bw_method="scott")
        xs   = np.linspace(0, 0.8, 600)
        ys   = kde(xs)
        ax.plot(xs, ys, lw=2.5, color=color, label=label)
        ax.fill_between(xs, ys, alpha=0.12, color=color)
        ax.axvline(float(np.mean(mu)), color=color, ls="--", lw=1.2, alpha=0.7)

    ax.axvline(MU_MEAN, color=C_ANAL, ls="-", lw=1.8,
               label=f"Theoretical ⟨μ⟩ = {MU_MEAN:.4f}")
    ax.set_xlabel(r"Specific Margin $\mu = M/T$", fontsize=12)
    ax.set_ylabel("Density (KDE)", fontsize=11)
    ax.set_title("Distribution of Specific Margin — Pre-EVM vs Post-EVM\n"
                 "(dashed vertical = group mean)", fontsize=11)
    ax.legend(fontsize=10)
    ax.set_xlim(0, 0.7)
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig08_mu_kde_pre_vs_post.png")
    path_pdf = os.path.join(out_dir, "fig08_mu_kde_pre_vs_post.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 8 saved: {os.path.basename(path_png)}")
    return path_png


def fig_yearly_trend(df, dpi, out_dir):
    """Figure 9: Mean specific margin per year with EVM cutoff."""
    df2 = df[~df["yr"].isin(EXCLUDED_YEARS)].copy()
    df2["mu"] = df2["margin"] / df2["vv1"]
    yr_stats  = df2.groupby("yr")["mu"].agg(["mean","median","sem"]).reset_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    pre_mask  = yr_stats["yr"].isin(PRE_EVM_YEARS)
    post_mask = yr_stats["yr"].isin(POST_EVM_YEARS)

    ax.errorbar(yr_stats[pre_mask]["yr"],  yr_stats[pre_mask]["mean"],
                yerr=1.96*yr_stats[pre_mask]["sem"],
                fmt="o-", color=C_PRE,  ms=6, lw=2, capsize=4,
                label="Pre-EVM mean ± 95% CI")
    ax.errorbar(yr_stats[post_mask]["yr"], yr_stats[post_mask]["mean"],
                yerr=1.96*yr_stats[post_mask]["sem"],
                fmt="s-", color=C_POST, ms=6, lw=2, capsize=4,
                label="Post-EVM mean ± 95% CI")

    ax.axvline(EVM_CUTOFF - 0.5, color="black", ls=":", lw=1.5,
               label=f"EVM cutoff ({EVM_CUTOFF})")
    ax.axhline(MU_MEAN, color=C_ANAL, ls="--", lw=1.5,
               label=f"Theoretical ⟨μ⟩ = {MU_MEAN:.4f}")

    ax.fill_between([yr_stats["yr"].min()-2, EVM_CUTOFF-0.5], 0, 1,
                    alpha=0.04, color=C_PRE, transform=ax.get_xaxis_transform())
    ax.fill_between([EVM_CUTOFF-0.5, yr_stats["yr"].max()+2], 0, 1,
                    alpha=0.04, color=C_POST, transform=ax.get_xaxis_transform())

    ax.set_xlabel("Election Year", fontsize=12)
    ax.set_ylabel(r"Mean Specific Margin $\langle\mu\rangle$", fontsize=11)
    ax.set_title("Trend of Mean Specific Margin Over Time — 14 States\n"
                 "Standard general elections only (1985 & 1992 by-election batches excluded)", fontsize=11)
    ax.legend(fontsize=9, loc="upper right")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
    plt.xticks(rotation=45)
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig09_yearly_trend.png")
    path_pdf = os.path.join(out_dir, "fig09_yearly_trend.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 9 saved: {os.path.basename(path_png)}")
    return path_png


def fig_statewise_delta(states, pre_means, post_means, dpi, out_dir):
    """Figure 10: Delta (post - pre) mean mu per state, horizontal bar."""
    deltas   = [post - pre for pre, post in zip(pre_means, post_means)]
    sort_idx = np.argsort(deltas)
    s_states = [states[i] for i in sort_idx]
    s_deltas = [deltas[i]  for i in sort_idx]
    colors   = [C_POST if d > 0 else C_PRE for d in s_deltas]

    fig, ax = plt.subplots(figsize=(8, max(5, len(states)*0.42)))
    ax.barh(range(len(s_states)), s_deltas, color=colors, edgecolor="white", alpha=0.85)
    ax.axvline(0, color="black", lw=1)
    ax.set_yticks(range(len(s_states)))
    ax.set_yticklabels([s.title() for s in s_states], fontsize=9)
    ax.set_xlabel(r"$\Delta\langle\mu\rangle$ = Post-EVM − Pre-EVM", fontsize=11)
    ax.set_title("Change in Mean Specific Margin\nPost-EVM minus Pre-EVM (per state)\n"
                 "(red = increased margin post-EVM, blue = decreased)", fontsize=11)
    fig.tight_layout()
    path_png = os.path.join(out_dir, "fig10_statewise_delta_margin.png")
    path_pdf = os.path.join(out_dir, "fig10_statewise_delta_margin.pdf")
    fig.savefig(path_png, dpi=dpi, bbox_inches="tight")
    fig.savefig(path_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 10 saved: {os.path.basename(path_png)}")
    return path_png

# ══════════════════════════════════════════════════════════════
# SECTION 7 — REPORT WRITER
# ══════════════════════════════════════════════════════════════

def write_report(stats_p, state_rows, pre_yrs, post_yrs, excl_yrs,
                 n_pre_total, n_post_total, out_dir, data_path, args):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Pre-EVM vs Post-EVM Indian Parliamentary Election Analysis",
        "",
        f"**Generated**: {now}  ",
        f"**Dataset**: `{os.path.basename(data_path)}`  ",
        f"**Script**: `src/pre_post_evm_analysis.py`  ",
        f"**RVM runs per group**: {args.runs}  ",
        f"**Output DPI**: {args.dpi}",
        "",
        "---",
        "",
        "## 1. Data Overview",
        "",
        f"| Category | Years | Count |",
        f"|----------|-------|-------|",
        f"| Pre-EVM elections | {pre_yrs} | {n_pre_total:,} constituency-elections |",
        f"| Post-EVM elections | {post_yrs} | {n_post_total:,} constituency-elections |",
        f"| **Excluded** (by-election batches) | {excl_yrs} | — |",
        "",
        "> **EVM cutoff**: 2004. EVMs were introduced experimentally before 2004 in some",
        "> constituencies but were adopted nationwide for the 2004 general election.",
        "> The 1985 (n=27) and 1992 (n=13) rows are mid-term/by-election batches and",
        "> are excluded from both groups to avoid sample-size bias.",
        "",
        "---",
        "",
        "## 2. Pooled Statistical Comparison (14 States)",
        "",
        f"| Metric | Pre-EVM | Post-EVM |",
        f"|--------|---------|----------|",
        f"| N | {stats_p['n_pre']:,} | {stats_p['n_post']:,} |",
        f"| Mean μ | {stats_p['mean_pre']:.6f} | {stats_p['mean_post']:.6f} |",
        f"| Median μ | {stats_p['median_pre']:.6f} | {stats_p['median_post']:.6f} |",
        f"| Std dev | {stats_p['std_pre']:.6f} | {stats_p['std_post']:.6f} |",
        f"| 95% CI (mean) | ({stats_p['ci95_pre'][0]:.5f}, {stats_p['ci95_pre'][1]:.5f}) | ({stats_p['ci95_post'][0]:.5f}, {stats_p['ci95_post'][1]:.5f}) |",
        f"| Theoretical ⟨μ⟩ | {MU_MEAN:.6f} | {MU_MEAN:.6f} |",
        "",
        f"**Relative change**: {stats_p['rel_change_pct']:+.2f}%  ",
        f"**Cohen's d**: {stats_p['cohens_d']:.4f}  ",
        f"**Mann-Whitney U**: {stats_p['mannwhitney_U']:.0f} (p = {stats_p['mannwhitney_p']:.4e})  ",
        f"**KS statistic**: {stats_p['ks_stat']:.4f} (p = {stats_p['ks_p']:.4e})",
        "",
        "---",
        "",
        "## 3. State-wise Summary",
        "",
        "| State | N Pre | N Post | Mean μ Pre | Mean μ Post | Δμ | KS p | Fraud Pre | Fraud Post |",
        "|-------|-------|--------|------------|-------------|-----|------|-----------|------------|",
    ]
    for r in state_rows:
        lines.append(
            f"| {r['state'].title()} | {r['n_pre']} | {r['n_post']} "
            f"| {r['mu_pre']:.5f} | {r['mu_post']:.5f} "
            f"| {r['delta_mu']:+.5f} | {r['ks_p']:.3e} "
            f"| {r['fraud_pre']:.3f} | {r['fraud_post']:.3f} |"
        )
    lines += [
        "",
        "---",
        "",
        "## 4. Interpretation",
        "",
        "- All differences are **statistical associations** between the pre-EVM and post-EVM eras.",
        "- This analysis **does not** establish causality or constitute evidence of electoral fraud.",
        "- Many confounding factors exist: constituency delimitation, population growth,",
        "  expansion of voter rolls, changing competition levels, and economic factors.",
        "- The RVM (Random Voting Model) is a null model assuming random vote allocation;",
        "  systematic deviation from it indicates non-random structure, not manipulation.",
        "",
        "---",
        "",
        "## 5. Reproducibility",
        "",
        f"```",
        f"python src/pre_post_evm_analysis.py --runs {args.runs} --dpi {args.dpi} --seed {args.seed}",
        f"```",
        "",
        f"**Python**: {platform.python_version()}  ",
        f"**NumPy**: {np.__version__}  ",
        f"**Pandas**: {pd.__version__}  ",
        f"**SciPy**: {__import__('scipy').__version__}",
        "",
        "---",
        "*Analysis performed using the project's existing RVM methodology.*",
        "*No existing results were modified.*",
    ]
    path = os.path.join(out_dir, "pre_post_evm_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  ✓ Report saved: pre_post_evm_report.md")
    return path

# ══════════════════════════════════════════════════════════════
# SECTION 8 — MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Pre-EVM vs Post-EVM RVM Analysis")
    parser.add_argument("--data",  default=DATA_PATH)
    parser.add_argument("--runs",  type=int, default=25, help="RVM ensemble runs (default 25)")
    parser.add_argument("--dpi",   type=int, default=600, help="Output DPI (default 600)")
    parser.add_argument("--seed",  type=int, default=42)
    args = parser.parse_args()

    # Create output directory tree
    for d in (OUT_FIG, OUT_TAB, OUT_DATA, OUT_REP, OUT_LOG):
        os.makedirs(d, exist_ok=True)

    # Configure logging
    log_path = os.path.join(OUT_LOG, "analysis.log")
    sh = logging.StreamHandler(sys.stdout)
    sh.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, closefd=False)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            sh,
        ]
    )
    log = logging.getLogger(__name__)
    log.info("=" * 65)
    log.info("  Pre-EVM vs Post-EVM Indian Parliamentary Election Analysis")
    log.info("=" * 65)
    log.info(f"  Data    : {args.data}")
    log.info(f"  RVM runs: {args.runs}   DPI: {args.dpi}   Seed: {args.seed}")

    # ── Load ──────────────────────────────────────────────────
    log.info("\nLoading and splitting data ...")
    df, df_pre, df_post, states_14, pre_yrs, post_yrs, excl_yrs = load_and_split(args.data, log)

    # ── Pooled arrays ─────────────────────────────────────────
    T_pre  = df_pre["vv1"].values.astype(float)
    M_pre  = df_pre["margin"].values.astype(float)
    T_post = df_post["vv1"].values.astype(float)
    M_post = df_post["margin"].values.astype(float)
    mu_pre  = M_pre  / T_pre
    mu_post = M_post / T_post

    # ── Statistical comparison ────────────────────────────────
    log.info("\nComputing pooled statistics ...")
    stats_p = compute_stats(mu_pre, mu_post)
    log.info(f"  Pre  mean mu : {stats_p['mean_pre']:.6f}  (n={stats_p['n_pre']:,})")
    log.info(f"  Post mean mu : {stats_p['mean_post']:.6f}  (n={stats_p['n_post']:,})")
    log.info(f"  Relative delta : {stats_p['rel_change_pct']:+.2f}%")
    log.info(f"  Cohen's d      : {stats_p['cohens_d']:.4f}")
    log.info(f"  KS p-value     : {stats_p['ks_p']:.4e}")
    log.info(f"  MW  p-value    : {stats_p['mannwhitney_p']:.4e}")

    # ── Pooled RVM ────────────────────────────────────────────
    log.info("\nRunning pooled RVM simulations ...")
    rvm_pre  = rvm_ensemble(T_pre,  args.runs, args.seed, label="Pre-EVM pooled")
    rvm_post = rvm_ensemble(T_post, args.runs, args.seed, label="Post-EVM pooled")

    # ── Per-state analysis ────────────────────────────────────
    log.info("\nPer-state analysis ...")
    state_rows = []
    pre_means  = []
    post_means = []
    n_pre_s    = []
    n_post_s   = []

    for state in states_14:
        sub_pre  = df_pre[df_pre["state_n"]  == state]
        sub_post = df_post[df_post["state_n"] == state]
        T_sp = sub_pre["vv1"].values.astype(float)
        M_sp = sub_pre["margin"].values.astype(float)
        T_sq = sub_post["vv1"].values.astype(float)
        M_sq = sub_post["margin"].values.astype(float)

        mu_sp = M_sp / np.maximum(T_sp, 1) if len(T_sp) > 0 else np.array([])
        mu_sq = M_sq / np.maximum(T_sq, 1) if len(T_sq) > 0 else np.array([])

        m_pre  = float(np.mean(mu_sp))  if len(mu_sp) > 0 else np.nan
        m_post = float(np.mean(mu_sq)) if len(mu_sq) > 0 else np.nan
        pre_means.append(m_pre)
        post_means.append(m_post)
        n_pre_s.append(len(T_sp))
        n_post_s.append(len(T_sq))

        # KS test per state
        if len(mu_sp) >= 5 and len(mu_sq) >= 5:
            ks_s, ks_p = stats.ks_2samp(mu_sp, mu_sq)
        else:
            ks_s, ks_p = np.nan, np.nan

        # Fraud scores per state
        rvm_sp  = rvm_ensemble(T_sp,  args.runs, args.seed, label=f"{state} Pre") if len(T_sp) >= 10 else []
        rvm_sq  = rvm_ensemble(T_sq,  args.runs, args.seed, label=f"{state} Post") if len(T_sq) >= 10 else []
        fsc_pre,  _ = fraud_score(T_sp, M_sp, rvm_sp)  if rvm_sp else (np.nan, False)
        fsc_post, _ = fraud_score(T_sq, M_sq, rvm_sq) if rvm_sq else (np.nan, False)

        row = {
            "state":      state,
            "n_pre":      len(T_sp),
            "n_post":     len(T_sq),
            "mu_pre":     m_pre,
            "mu_post":    m_post,
            "delta_mu":   (m_post - m_pre) if not (np.isnan(m_pre) or np.isnan(m_post)) else np.nan,
            "ks_stat":    ks_s,
            "ks_p":       ks_p,
            "fraud_pre":  fsc_pre,
            "fraud_post": fsc_post,
        }
        state_rows.append(row)
        log.info(f"  {state}: n_pre={len(T_sp)}, n_post={len(T_sq)}, "
                 f"mu_pre={m_pre:.4f}, mu_post={m_post:.4f}, "
                 f"delta={row['delta_mu']:+.4f}, KS_p={ks_p:.3e}")

    # ── Save tables ───────────────────────────────────────────
    pd.DataFrame([stats_p]).to_csv(
        os.path.join(OUT_TAB, "pooled_stats.csv"), index=False)

    state_df = pd.DataFrame(state_rows)
    state_df.to_csv(os.path.join(OUT_TAB, "statewise_comparison.csv"), index=False)
    log.info("  ✓ Tables saved")

    # Save derived data
    df_pre.assign(era="pre_evm").to_csv(
        os.path.join(OUT_DATA, "data_pre_evm.csv"), index=False)
    df_post.assign(era="post_evm").to_csv(
        os.path.join(OUT_DATA, "data_post_evm.csv"), index=False)
    log.info("  ✓ Derived data saved")

    # ── Figures ───────────────────────────────────────────────
    log.info("\nGenerating figures ...")
    fig_pooled_Fx(T_pre, M_pre, T_post, M_post,
                  rvm_pre, rvm_post, args.dpi, OUT_FIG)
    fig_pooled_scaled_margin(T_pre, M_pre, T_post, M_post,
                              rvm_pre, rvm_post, args.dpi, OUT_FIG)
    fig_mean_margin_comparison(stats_p, args.dpi, OUT_FIG)
    fig_sample_sizes(states_14, n_pre_s, n_post_s, args.dpi, OUT_FIG)
    fig_statewise_mean_margin(states_14, pre_means, post_means, args.dpi, OUT_FIG)
    fig_statewise_Fx_grid(df_pre, df_post, states_14, args.runs, args.seed, args.dpi, OUT_FIG)
    fig_fraud_score_comparison(state_rows, args.dpi, OUT_FIG)
    fig_mu_distribution_kde(mu_pre, mu_post, args.dpi, OUT_FIG)
    fig_yearly_trend(df, args.dpi, OUT_FIG)
    fig_statewise_delta(states_14, pre_means, post_means, args.dpi, OUT_FIG)

    # ── Report ────────────────────────────────────────────────
    log.info("\nWriting Markdown report ...")
    write_report(stats_p, state_rows, pre_yrs, post_yrs, excl_yrs,
                 len(T_pre), len(T_post),
                 OUT_REP, args.data, args)

    # Reproducibility metadata
    meta = {
        "timestamp":      datetime.datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "numpy_version":  np.__version__,
        "pandas_version": pd.__version__,
        "args":           vars(args),
        "data_sha256":    hashlib.sha256(open(args.data,"rb").read()).hexdigest(),
        "pre_evm_years":  list(pre_yrs),
        "post_evm_years": list(post_yrs),
        "excluded_years": list(excl_yrs),
        "n_pre_total":    int(len(T_pre)),
        "n_post_total":   int(len(T_post)),
        "mu_analytical":  round(MU_MEAN, 8),
    }
    with open(os.path.join(OUT_LOG, "reproducibility.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # ── Final summary ─────────────────────────────────────────
    log.info("")
    log.info("=" * 65)
    log.info("  SUMMARY")
    log.info("=" * 65)
    log.info(f"  Pre-EVM  : {len(T_pre):,} obs  |  mean mu = {stats_p['mean_pre']:.5f}")
    log.info(f"  Post-EVM : {len(T_post):,} obs  |  mean mu = {stats_p['mean_post']:.5f}")
    log.info(f"  Relative change : {stats_p['rel_change_pct']:+.2f}%")
    log.info(f"  Cohen's d       : {stats_p['cohens_d']:.4f}")
    log.info(f"  KS test         : D={stats_p['ks_stat']:.4f}, p={stats_p['ks_p']:.4e}")
    log.info(f"  Mann-Whitney    : p={stats_p['mannwhitney_p']:.4e}")
    log.info("")
    log.info(f"  Figures  : {OUT_FIG}/  (10 PNG + 8 PDF)")
    log.info(f"  Tables   : {OUT_TAB}/  (2 CSV)")
    log.info(f"  Data     : {OUT_DATA}/  (2 CSV)")
    log.info(f"  Report   : {OUT_REP}/pre_post_evm_report.md")
    log.info(f"  Logs     : {OUT_LOG}/")
    log.info("")
    log.info("  To rerun:")
    log.info(f"  python src/pre_post_evm_analysis.py --runs {args.runs} --dpi {args.dpi} --seed {args.seed}")
    log.info("=" * 65)


if __name__ == "__main__":
    main()
