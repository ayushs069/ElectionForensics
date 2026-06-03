"""
RVM Analysis Script
====================

Dataset columns expected:
    ctr_n, yr, cst_n, vv1, winner_votes, runner_up_votes,
    margin, specific_margin, scaled_margin, scaled_specific_margin

Usage:
    # All countries
    python rvm_analysis.py --data constituency_level_results.csv

    # Single country
    python rvm_analysis.py --data constituency_level_results.csv --country India

    # Change RVM runs (more = smoother band, slower)
    python rvm_analysis.py --data constituency_level_results.csv --runs 30

Outputs saved to:  rvm_outputs/
    pooled/        → plots for all countries combined
    per_country/   → 3 plots per country
    summary.csv    → fraud scores for all countries
"""

import os
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad

warnings.filterwarnings("ignore")

# ── global plot style ──────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        150,
})

# ══════════════════════════════════════════════════════════════
# SECTION 1 — ANALYTICAL FORMULA
# ══════════════════════════════════════════════════════════════

def P_mu(mu):
    """PDF of specific margin µ = M/T (3 candidates, large T)"""
    return (1 - mu) * (5 + 7 * mu) / ((1 + mu)**2 * (1 + 2 * mu)**2)

# numerical mean of µ under P(µ)
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

def load_data(path, min_units=400):
    """
    Load CSV, clean invalid rows, return full DataFrame.
    Also prints per-country summary.
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    # validate required columns
    for col in ("vv1", "margin", "ctr_n"):
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    before = len(df)
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]
    print(f"  Dropped {before - len(df)} invalid rows")
    print(f"  Valid rows : {len(df):,}")
    print(f"  Countries  : {df['ctr_n'].nunique()}")
    print(f"  Years      : {int(df['yr'].min())} – {int(df['yr'].max())}")

    # country eligibility
    counts = df.groupby("ctr_n").size()
    eligible = counts[counts >= min_units].index.tolist()
    skipped  = counts[counts <  min_units].index.tolist()
    print(f"\n  Eligible (≥{min_units} rows) : {len(eligible)} countries")
    if skipped:
        print(f"  Skipped  (<{min_units} rows) : {skipped}")

    return df, eligible


# ══════════════════════════════════════════════════════════════
# SECTION 3 — RVM SIMULATION
# ══════════════════════════════════════════════════════════════

def rvm_once(turnouts, rng, n_cand=3):
    """
    Single RVM run.
    For each electoral unit i with turnout T_i:
      1. Draw n_cand weights ~ Uniform(0,1), normalise → probabilities
      2. Draw votes ~ Multinomial(T_i, probs)
      3. margin_i = top_vote - second_vote
    Returns margins array.
    """
    N = len(turnouts)
    margins = np.empty(N)
    for i, T in enumerate(turnouts):
        T = max(int(T), 2)
        w     = rng.uniform(0, 1, n_cand)
        p     = w / w.sum()
        votes = rng.multinomial(T, p)
        s     = np.sort(votes)[::-1]       # descending
        margins[i] = s[0] - s[1]
    return margins

def rvm_ensemble(turnouts, n_runs=25, seed=0):
    """
    Run RVM n_runs times.
    Returns list of (margins, specific_margins) tuples.
    """
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
# SECTION 4 — HISTOGRAM HELPER
# ══════════════════════════════════════════════════════════════

def log_histogram(values, n_bins=55):
    """
    Log-spaced histogram returning (bin_centers, density).
    Uses geometric midpoints so log-log plots look clean.
    """
    v = np.asarray(values, dtype=float)
    v = v[v > 0]
    if len(v) < 5:
        return np.array([]), np.array([])
    bins    = np.logspace(np.log10(v.min()), np.log10(v.max()), n_bins + 1)
    counts, edges = np.histogram(v, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])   # geometric midpoint
    ok      = counts > 0
    return centers[ok], counts[ok]

def rvm_mean_std(rvm_results, extractor, ref_x, n_bins=55):
    """
    Given RVM runs and a function extractor(margins, mu) → array of values,
    compute mean and std of the PDF across all runs on a reference x-grid.
    """
    pdfs = []
    for (m, mu) in rvm_results:
        xr, yr = log_histogram(extractor(m, mu), n_bins)
        if len(xr) == 0:
            continue
        pdfs.append(np.interp(ref_x, xr, yr, left=np.nan, right=np.nan))
    mat = np.array(pdfs)
    return np.nanmean(mat, axis=0), np.nanstd(mat, axis=0)


# ══════════════════════════════════════════════════════════════
# SECTION 5 — THE THREE CORE PLOTS
# ══════════════════════════════════════════════════════════════

# ── Plot A: f(M/<M>)  scaled margin ───────────

def plot_scaled_margin(T, M, rvm_results, country, save_path):
    """
    Empirical scaled margin distribution vs RVM prediction.
    Circles = data,  solid line = RVM mean,  band = RVM ± 1σ
    """
    # empirical
    scaled_M     = M / M.mean()
    xe, ye       = log_histogram(scaled_M)

    # RVM reference grid from first run
    rvm0_scaled  = rvm_results[0][0] / rvm_results[0][0].mean()
    xr, _        = log_histogram(rvm0_scaled)
    rm, rs       = rvm_mean_std(rvm_results, lambda m, mu: m / m.mean(), xr)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs,
                    color="gray", alpha=0.3)
    ax.plot(xr, rm, "k-", lw=2, label="RVM prediction")
    ax.scatter(xe, ye, s=20, facecolors="none",
               edgecolors="#2166ac", lw=0.9, label=f"{country} (data)", zorder=4)

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$M\,/\,\langle M \rangle$", fontsize=13)
    ax.set_ylabel(r"$f\!\left(M/\langle M\rangle\right)$", fontsize=13)
    ax.set_title(f"Scaled Margin Distribution — {country}", fontsize=12)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


# ── Plot B: F(x)  universal curve ─────────────

def plot_universal_Fx(T, M, rvm_results, country, save_path):
    """
    Scaled specific margin x = µ/<µ> vs analytical universal curve.
    Red line = analytical F(x),  circles = data,  dashed = RVM
    """
    mu_emp   = M / T
    x_emp    = mu_emp / mu_emp.mean()
    xb, Fxb  = log_histogram(x_emp)

    rvm0_x   = rvm_results[0][1] / rvm_results[0][1].mean()
    xr, _    = log_histogram(rvm0_x)
    rm, rs   = rvm_mean_std(rvm_results, lambda m, mu: mu / mu.mean(), xr)

    x_anal   = np.logspace(-1.3, 0.8, 600)
    Fx_anal  = F_x_analytical(x_anal)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs,
                    color="gray", alpha=0.25)
    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2.5,
            label="Analytical F(x)", zorder=5)
    ax.plot(xr, rm, "k--", lw=1.5, label="RVM", zorder=4)
    ax.scatter(xb, Fxb, s=20, facecolors="none",
               edgecolors="#2166ac", lw=0.9, label=f"{country} (data)", zorder=6)

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=13)
    ax.set_ylabel(r"$F(x)$", fontsize=13)
    ax.set_title(f"Universal F(x) — {country}", fontsize=12)
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


# ── Plot C: Fraud detection ───────────────────

def plot_fraud_check(T, M, rvm_results, country, save_path):
    """
    Two-panel deviation check.
    Left  : f(M/<M>) — is the margin distribution unusual?
    Right : F(x)     — does it deviate from universal curve?
    Shows fraud score mean|z| in corner.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # ── left panel ────────────────────────────────────────────
    scaled_M     = M / M.mean()
    xe, ye       = log_histogram(scaled_M)
    rvm0_sm      = rvm_results[0][0] / rvm_results[0][0].mean()
    xr_m, _      = log_histogram(rvm0_sm)
    rm_m, rs_m   = rvm_mean_std(rvm_results, lambda m, mu: m / m.mean(), xr_m)

    ax = axes[0]
    ax.fill_between(xr_m, np.clip(rm_m - rs_m, 1e-5, None), rm_m + rs_m,
                    color="#f4a582", alpha=0.5)
    ax.plot(xr_m, rm_m, "-", color="#d73027", lw=2, label="RVM")
    ax.scatter(xe, ye, s=15, facecolors="none",
               edgecolors="#4393c3", lw=0.9, label=country)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$M/\langle M\rangle$", fontsize=12)
    ax.set_ylabel(r"$f(M/\langle M\rangle)$", fontsize=12)
    ax.set_title(f"(a) Scaled Margin — {country}", fontsize=11)
    ax.legend(fontsize=9)

    # ── right panel ───────────────────────────────────────────
    mu_emp   = M / T
    x_emp    = mu_emp / mu_emp.mean()
    xb, Fxb  = log_histogram(x_emp)
    rvm0_x   = rvm_results[0][1] / rvm_results[0][1].mean()
    xr_x, _  = log_histogram(rvm0_x)
    rm_x, rs_x = rvm_mean_std(rvm_results, lambda m, mu: mu / mu.mean(), xr_x)

    x_anal   = np.logspace(-1.3, 0.8, 600)
    Fx_anal  = F_x_analytical(x_anal)

    # fraud score
    Fxb_ref  = np.interp(xr_x, xb, Fxb, left=np.nan, right=np.nan)
    with np.errstate(invalid="ignore"):
        z_scores = np.abs(Fxb_ref - rm_x) / (rs_x + 1e-10)
    mean_z   = float(np.nanmean(z_scores))
    flagged  = mean_z > 3.0

    ax = axes[1]
    ax.fill_between(xr_x, np.clip(rm_x - rs_x, 1e-5, None), rm_x + rs_x,
                    color="#f4a582", alpha=0.5, label="RVM band")
    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2, label="Analytical F(x)")
    ax.scatter(xb, Fxb, s=15, facecolors="none",
               edgecolors="#4393c3", lw=0.9, label=country)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu/\langle\mu\rangle$", fontsize=12)
    ax.set_ylabel(r"$F(x)$", fontsize=12)
    ax.set_title(f"(b) Universal F(x) — {country}", fontsize=11)
    ax.legend(fontsize=9)

    color_z = "firebrick" if flagged else "green"
    label_z = f"Mean |z| = {mean_z:.2f}  {'⚠ FLAGGED' if flagged else '✓ OK'}"
    ax.text(0.03, 0.04, label_z, transform=ax.transAxes,
            fontsize=9, color=color_z, va="bottom",
            bbox=dict(boxstyle="round,pad=0.3",
                      facecolor="#fff0f0" if flagged else "#f0fff0",
                      edgecolor=color_z))

    fig.suptitle(f"Deviation Check — {country}", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return mean_z, flagged


# ══════════════════════════════════════════════════════════════
# SECTION 6 — BONUS: ALL COUNTRIES F(x) ON ONE PLOT
# ══════════════════════════════════════════════════════════════

def plot_all_countries_Fx(df, eligible, rvm_cache, save_path):
    """
    Overlay F(x) from all eligible countries + analytical curve.
    Overlay F(x) from all eligible countries + analytical curve.
    """
    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)
    xb_ref  = np.logspace(-1.2, 0.7, 80)

    cmap   = plt.cm.get_cmap("tab20", len(eligible))
    fig, ax = plt.subplots(figsize=(7, 6))

    all_Fx = []
    for i, ctr in enumerate(eligible):
        sub    = df[df["ctr_n"] == ctr]
        T      = sub["vv1"].values.astype(float)
        M      = sub["margin"].values.astype(float)
        mu_emp = M / T
        x_emp  = mu_emp / mu_emp.mean()
        xb, Fxb = log_histogram(x_emp)
        if len(xb) == 0:
            continue
        ax.scatter(xb, Fxb, s=10, color=cmap(i), alpha=0.6, zorder=3)
        all_Fx.append(np.interp(xb_ref, xb, Fxb, left=np.nan, right=np.nan))

    # average empirical
    avg_Fx = np.nanmean(all_Fx, axis=0)
    ok     = ~np.isnan(avg_Fx)
    ax.scatter(xb_ref[ok], avg_Fx[ok], s=40, facecolors="none",
               edgecolors="red", lw=1.5, zorder=5, label="Average (all countries)")

    # average RVM
    all_rvm_Fx = []
    for ctr in eligible:
        if ctr not in rvm_cache:
            continue
        rvm = rvm_cache[ctr]
        rvm0x = rvm[0][1] / rvm[0][1].mean()
        xrr, _ = log_histogram(rvm0x)
        rm, _  = rvm_mean_std(rvm, lambda m, mu: mu / mu.mean(), xrr)
        all_rvm_Fx.append(np.interp(xb_ref, xrr, rm, left=np.nan, right=np.nan))
    avg_rvm = np.nanmean(all_rvm_Fx, axis=0)
    ok2     = ~np.isnan(avg_rvm)
    ax.scatter(xb_ref[ok2], avg_rvm[ok2], s=40, facecolors="none",
               edgecolors="black", lw=1.5, zorder=4, label="RVM average")

    # analytical
    ax.plot(x_anal, Fx_anal, "-", color="#d73027", lw=2.5,
            label="Analytical F(x)", zorder=6)

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(8e-2, 6); ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=13)
    ax.set_ylabel(r"$F(x)$", fontsize=13)
    ax.set_title(f"Universal F(x) — All {len(eligible)} Countries\n"
                 f"(each colour = one country)", fontsize=11)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")


# ══════════════════════════════════════════════════════════════
# SECTION 7 — FRAUD BAR CHART
# ══════════════════════════════════════════════════════════════

def plot_fraud_barchart(summary_df, save_path):
    s = summary_df.sort_values("fraud_score", ascending=True)
    colors = ["#d73027" if f else "#4393c3" for f in s["flagged"]]

    fig, ax = plt.subplots(figsize=(8, max(5, len(s) * 0.32)))
    bars = ax.barh(s["country"], s["fraud_score"],
                   color=colors, edgecolor="white", height=0.7)
    ax.axvline(3.0, color="firebrick", ls="--", lw=1.5,
               label="Fraud threshold (|z| = 3)")
    for bar, val, flag in zip(bars, s["fraud_score"], s["flagged"]):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}" + ("  ⚠" if flag else ""),
                va="center", fontsize=8,
                color="firebrick" if flag else "black")
    ax.set_xlabel("Fraud Score  (mean |z|)", fontsize=11)
    ax.set_title("Fraud Indicator Score by Country\n"
                 "(red = flagged, threshold = 3.0)", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(0, s["fraud_score"].max() * 1.2)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")


# ══════════════════════════════════════════════════════════════
# SECTION 8 — MAIN
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="RVM Analysis — Election Universality & Fraud Detection"
    )
    parser.add_argument("--data",    required=True, help="Path to CSV file")
    parser.add_argument("--country", default=None,  help="Run single country only")
    parser.add_argument("--runs",    type=int, default=25,
                        help="RVM ensemble runs per country (default: 25)")
    parser.add_argument("--min-units", type=int, default=400,
                        help="Min rows per country (default: 400)")
    parser.add_argument("--seed",    type=int, default=42)
    args = parser.parse_args()

    # ── output folders ────────────────────────────────────────
    OUT_POOLED  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "rvm_outputs", "pooled")
    OUT_CTR     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "rvm_outputs", "per_country")
    os.makedirs(OUT_POOLED, exist_ok=True)
    os.makedirs(OUT_CTR,    exist_ok=True)

    print("\n" + "═"*55)
    print("  RVM Analysis — Election Data")
    print("═"*55)

    # ── load ──────────────────────────────────────────────────
    print(f"\nLoading {args.data}...")
    df, eligible = load_data(args.data, min_units=args.min_units)

    # ── single country mode ───────────────────────────────────
    if args.country:
        if args.country not in df["ctr_n"].values:
            print(f"Country '{args.country}' not found.")
            print(f"Available: {sorted(df['ctr_n'].unique())}")
            return
        countries_to_run = [args.country]
    else:
        countries_to_run = eligible

    # ── per-country loop ──────────────────────────────────────
    summary_rows = []
    rvm_cache    = {}

    for ctr in countries_to_run:
        sub = df[df["ctr_n"] == ctr]
        T   = sub["vv1"].values.astype(float)
        M   = sub["margin"].values.astype(float)
        n   = len(sub)
        yr_range = f"{int(sub['yr'].min())}–{int(sub['yr'].max())}"

        print(f"\n{'─'*50}")
        print(f"  {ctr}  ({n:,} rows, {yr_range})")
        print(f"  Mean T={T.mean():,.0f}  Mean M={M.mean():,.0f}  "
              f"Mean µ={(M/T).mean():.4f}")

        # RVM
        rvm = rvm_ensemble(T, n_runs=args.runs, seed=args.seed)
        rvm_cache[ctr] = rvm

        safe = ctr.replace(" ", "_").replace("/", "-")

        # Plot A — scaled margin
        plot_scaled_margin(
            T, M, rvm, ctr,
            f"{OUT_CTR}/{safe}_fig1_scaled_margin.png"
        )
        print(f"  ✓ scaled margin plot saved")

        # Plot B — universal F(x)
        plot_universal_Fx(
            T, M, rvm, ctr,
            f"{OUT_CTR}/{safe}_fig2_universal_Fx.png"
        )
        print(f"  ✓ universal F(x) plot saved")

        # Plot C — fraud check
        mean_z, flagged = plot_fraud_check(
            T, M, rvm, ctr,
            f"{OUT_CTR}/{safe}_fig3_fraud_check.png"
        )
        verdict = "⚠ FLAGGED" if flagged else "✓ OK"
        print(f"  Fraud score: {mean_z:.3f}  {verdict}")

        summary_rows.append({
            "country":     ctr,
            "n_units":     n,
            "yr_min":      int(sub["yr"].min()),
            "yr_max":      int(sub["yr"].max()),
            "mean_T":      round(T.mean(), 1),
            "mean_M":      round(M.mean(), 1),
            "mean_mu":     round((M/T).mean(), 6),
            "mu_analytical": round(MU_MEAN, 6),
            "fraud_score": round(mean_z, 3),
            "flagged":     flagged,
        })

    # ── pooled plot (all countries together) ──────────────────
    if not args.country:
        print(f"\n{'─'*50}")
        print("  Generating pooled plots (all countries)...")
        T_all = df[df["ctr_n"].isin(eligible)]["vv1"].values.astype(float)
        M_all = df[df["ctr_n"].isin(eligible)]["margin"].values.astype(float)
        rvm_all = rvm_ensemble(T_all, n_runs=args.runs, seed=args.seed)

        plot_scaled_margin(T_all, M_all, rvm_all, "All Countries (pooled)",
                           f"{OUT_POOLED}/fig1_scaled_margin_pooled.png")
        plot_universal_Fx(T_all, M_all, rvm_all, "All Countries (pooled)",
                          f"{OUT_POOLED}/fig2_universal_Fx_pooled.png")
        plot_fraud_check(T_all, M_all, rvm_all, "All Countries (pooled)",
                         f"{OUT_POOLED}/fig3_fraud_check_pooled.png")

        # all-countries F(x) overlay
        plot_all_countries_Fx(
            df, eligible, rvm_cache,
            f"{OUT_POOLED}/fig4_all_countries_Fx_overlay.png"
        )

    # ── summary table ─────────────────────────────────────────
    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values("fraud_score", ascending=False)

    summary_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "rvm_outputs", "summary.csv")
    summary_df.to_csv(summary_path, index=False)

    # fraud bar chart
    if len(summary_df) > 1:
        plot_fraud_barchart(summary_df, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "rvm_outputs", "fraud_barchart.png"))

    # ── print final ranking ───────────────────────────────────
    print("\n" + "═"*55)
    print("  FRAUD SCORE RANKING")
    print("═"*55)
    cols = ["country", "n_units", "mean_mu", "fraud_score", "flagged"]
    print(summary_df[cols].to_string(index=False))
    print(f"\n  Saved: {summary_path}")
    print(f"  Plots: rvm_outputs/per_country/  ({len(countries_to_run)*3} files)")
    print("\n" + "═"*55)
    print("  All done.")
    print("═"*55)


if __name__ == "__main__":
    main()
