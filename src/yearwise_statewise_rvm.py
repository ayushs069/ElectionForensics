"""
Year-wise State RVM Analysis
==============================
For each of the 7 target states, generates one RVM plot per available
election year, saved to:

  outputs/election_year_wise_plots/<STATE_NAME>/<STATE>_<YEAR>_rvm.png

Plots:
  - Empirical F(x) dots (blue circles)  - specific-margin scaled by sample mean
  - Theoretical analytical curve (green)
  - RVM simulation band (gray fill) + RVM mean (dashed black)
  - RVM deviation score (mean |z|) shown on plot

Usage:
    python src/yearwise_statewise_rvm.py
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad

warnings.filterwarnings("ignore")

# -- Paths
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJ_ROOT, "data", "processed", "alltime_csv_india.csv")
OUT_ROOT  = os.path.join(PROJ_ROOT, "outputs", "election_year_wise_plots")

TARGET_STATES = [
    "UTTAR PRADESH",
    "WEST BENGAL",
    "BIHAR",
    "GUJARAT",
    "MADHYA PRADESH",
    "TAMIL NADU",
    "RAJASTHAN",
]

MIN_CONST = 10
N_RUNS    = 30
SEED      = 42

plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

COL_DATA   = "#2166ac"
COL_THEORY = "#1a9641"
COL_RVM    = "#525252"
COL_BAND   = "#bdbdbd"


# ============================================================
# 1 - ANALYTICAL RVM FORMULA
# ============================================================

def P_mu(mu):
    return (1 - mu) * (5 + 7 * mu) / ((1 + mu)**2 * (1 + 2 * mu)**2)

MU_MEAN, _ = quad(lambda m: m * P_mu(m), 0, 1)

def F_x_analytical(x):
    x   = np.asarray(x, dtype=float)
    mu  = x * MU_MEAN
    out = np.zeros_like(mu)
    ok  = (mu > 0) & (mu < 1)
    out[ok] = MU_MEAN * P_mu(mu[ok])
    return out


# ============================================================
# 2 - RVM SIMULATION
# ============================================================

def rvm_once(turnouts, rng, n_cand=3):
    N      = len(turnouts)
    margins = np.empty(N)
    for i, T in enumerate(turnouts):
        T      = max(int(T), 2)
        w      = rng.uniform(0, 1, n_cand)
        p      = w / w.sum()
        votes  = rng.multinomial(T, p)
        s      = np.sort(votes)[::-1]
        margins[i] = s[0] - s[1]
    return margins

def rvm_ensemble(turnouts, n_runs=N_RUNS, seed=SEED):
    rng     = np.random.default_rng(seed)
    results = []
    for _ in range(n_runs):
        m   = rvm_once(turnouts, rng)
        mu  = m / turnouts
        results.append((m, mu))
    return results


# ============================================================
# 3 - LOG HISTOGRAM HELPER
# ============================================================

def log_histogram(values, n_bins=45):
    v = np.asarray(values, dtype=float)
    v = v[v > 0]
    if len(v) < 4:
        return np.array([]), np.array([])
    lo, hi = v.min(), v.max()
    if lo == hi:
        return np.array([]), np.array([])
    bins          = np.logspace(np.log10(lo), np.log10(hi), n_bins + 1)
    counts, edges = np.histogram(v, bins=bins, density=True)
    centers       = np.sqrt(edges[:-1] * edges[1:])
    ok            = counts > 0
    return centers[ok], counts[ok]

def rvm_band(rvm_results, extractor, ref_x, n_bins=45):
    pdfs = []
    for (m, mu) in rvm_results:
        xr, yr = log_histogram(extractor(m, mu), n_bins)
        if len(xr) == 0:
            continue
        pdfs.append(np.interp(ref_x, xr, yr, left=np.nan, right=np.nan))
    if not pdfs:
        return np.full_like(ref_x, np.nan), np.full_like(ref_x, np.nan)
    mat = np.array(pdfs)
    return np.nanmean(mat, axis=0), np.nanstd(mat, axis=0)


# ============================================================
# 4 - CORE YEAR-WISE RVM PLOT
# ============================================================

def plot_yearwise_rvm(T, M, rvm_results, state, year, n_const, save_path):
    mu_emp = M / T
    mu_emp = mu_emp[mu_emp > 0]
    if len(mu_emp) < 4:
        return None

    x_emp        = mu_emp / mu_emp.mean()
    xb, Fxb      = log_histogram(x_emp)
    if len(xb) == 0:
        return None

    rvm0_x  = rvm_results[0][1] / rvm_results[0][1].mean()
    xr, _   = log_histogram(rvm0_x)
    if len(xr) == 0:
        xr = np.logspace(-1.2, 0.7, 60)
    rm, rs  = rvm_band(rvm_results, lambda m, mu: mu / mu.mean(), xr)

    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)

    Fxb_ref   = np.interp(xr, xb, Fxb, left=np.nan, right=np.nan)
    with np.errstate(invalid="ignore"):
        z_scores = np.abs(Fxb_ref - rm) / (rs + 1e-10)
    mean_z  = float(np.nanmean(z_scores))
    flagged = mean_z > 3.0

    fig, ax = plt.subplots(figsize=(7, 5.5))

    band_lo = np.clip(rm - rs, 1e-5, None)
    band_hi = rm + rs
    ax.fill_between(xr, band_lo, band_hi,
                    color=COL_BAND, alpha=0.55, label="RVM simulation band")
    ax.plot(xr, rm, "--", color=COL_RVM, lw=1.6, label="RVM mean", zorder=4)
    ax.plot(x_anal, Fx_anal, "-", color=COL_THEORY, lw=2.5,
            label="Theoretical F(x)  [3-cand RVM]", zorder=5)
    ax.scatter(xb, Fxb, s=28, facecolors="none",
               edgecolors=COL_DATA, lw=1.1,
               label=f"Empirical ({n_const} constituencies)", zorder=6)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1)
    ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel("x = mu/<mu>",   fontsize=13)
    ax.set_ylabel("F(x)",           fontsize=13)
    ax.set_title(
        f"{state.title()}  -  {year} General Election\n"
        f"Empirical F(x) vs Theoretical RVM Distribution",
        fontsize=11, pad=10
    )
    ax.legend(fontsize=9, loc="upper right")

    score_color  = "firebrick" if flagged else "#1a7a3c"
    score_label  = (f"RVM Dev. Score  |z| = {mean_z:.2f}"
                    + ("  ANOMALOUS" if flagged else "  Normal"))
    ax.text(0.03, 0.04, score_label,
            transform=ax.transAxes, fontsize=8.5,
            color=score_color, va="bottom",
            bbox=dict(boxstyle="round,pad=0.35",
                      facecolor="#fff3f3" if flagged else "#f0fff4",
                      edgecolor=score_color, alpha=0.9))

    ax.axvline(1.0, color=COL_THEORY, lw=0.8, ls=":", alpha=0.5)

    fig.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path, dpi=150)
    plt.close(fig)

    return mean_z, flagged


# ============================================================
# 5 - MAIN
# ============================================================

def main():
    print("\n" + "="*65)
    print("  Year-wise State RVM Analysis  -  Indian Parliamentary Elections")
    print("="*65)

    print(f"\nLoading: {DATA_PATH}\n")
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip().str.lower()
    df["state_n"] = df["state_n"].str.strip().str.upper()

    required = {"state_n", "yr", "vv1", "margin"}
    missing  = required - set(df.columns)
    if missing:
        sys.exit(f"ERROR: missing columns: {missing}")

    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]
    print(f"Valid rows : {len(df):,}")
    print(f"Years      : {int(df['yr'].min())} - {int(df['yr'].max())}")
    print(f"States     : {df['state_n'].nunique()}")

    all_results = []

    for state in TARGET_STATES:
        sub_state = df[df["state_n"] == state]
        if sub_state.empty:
            print(f"\n[WARNING] State not found: '{state}'")
            continue

        years      = sorted(sub_state["yr"].unique())
        safe_state = state.replace(" ", "_")
        state_out  = os.path.join(OUT_ROOT, safe_state)
        os.makedirs(state_out, exist_ok=True)

        print(f"\n{'-'*65}")
        print(f"  {state}  |  {len(years)} years: {years}")
        print(f"{'-'*65}")

        for year in years:
            sub = sub_state[sub_state["yr"] == year]
            n   = len(sub)

            if n < MIN_CONST:
                print(f"  [{year}] SKIP - only {n} constituencies (< {MIN_CONST})")
                continue

            T       = sub["vv1"].values.astype(float)
            M       = sub["margin"].values.astype(float)
            mean_mu = float((M / T).mean())

            print(f"  [{year}]  {n:>3} consts  mean T={T.mean():>9,.0f}  mean mu={mean_mu:.4f}")

            rvm_results = rvm_ensemble(T, n_runs=N_RUNS, seed=SEED)

            fname     = f"{safe_state}_{year}_rvm.png"
            save_path = os.path.join(state_out, fname)

            result = plot_yearwise_rvm(T, M, rvm_results, state, year, n, save_path)
            if result is not None:
                mean_z, flagged = result
                verdict = "ANOMALOUS" if flagged else "Normal"
                print(f"         -> |z| = {mean_z:.3f}  [{verdict}]  saved: {fname}")
                all_results.append({
                    "state":     state,
                    "year":      year,
                    "n_const":   n,
                    "mean_mu":   round(mean_mu, 6),
                    "rvm_dev_z": round(mean_z, 3),
                    "flagged":   flagged,
                    "plot_file": os.path.join(safe_state, fname),
                })

    if all_results:
        summary      = pd.DataFrame(all_results)
        summary_path = os.path.join(OUT_ROOT, "yearwise_summary.csv")
        summary.to_csv(summary_path, index=False)
        print(f"\n{'='*65}")
        print(f"  Summary saved: {summary_path}")

        flagged_df = summary[summary["flagged"]]
        normal_df  = summary[~summary["flagged"]]
        print(f"\n  Total plots   : {len(summary)}")
        print(f"  Normal        : {len(normal_df)}")
        print(f"  Anomalous     : {len(flagged_df)}")

        if not flagged_df.empty:
            print("\n  ANOMALOUS STATE-YEARS (|z| > 3.0):")
            print(flagged_df[["state","year","n_const","rvm_dev_z"]].to_string(index=False))

    print(f"\n  All plots saved to: {OUT_ROOT}/")
    print("\n" + "="*65)
    print("  Done.")
    print("="*65)


if __name__ == "__main__":
    main()
