"""
generate_report_figs.py
========================
Generates publication-quality figures (600 dpi) for the paper:
  - Fig 3 : Mean Specific Margin bar chart (redesigned: neutral colour, values, no title)
  - Fig 4 : EDA7 – Scaled µ vs Analytical (formal, 600 dpi)
  - Fig 5 : Pooled Universal F(x) (formal, 600 dpi)
  - Fig 6 : Uttar Pradesh Universal F(x) (formal, 600 dpi)
  - Fig 7 : West Bengal Universal F(x) (formal, 600 dpi)

Output: outputs/india/report_600dpi_images/
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

# ── paths ─────────────────────────────────────────────────────────────────────
BASE   = r"d:\sem-5_projects\PRJ-3"
OUT    = os.path.join(BASE, "outputs", "india", "report_600dpi_images")
os.makedirs(OUT, exist_ok=True)

DATA_IMP  = os.path.join(BASE, "outputs", "rvm_outputs_14states_IMP")
SUMM_CSV  = os.path.join(DATA_IMP, "summary.csv")
DATA_CSV  = os.path.join(BASE, "data", "processed", "final_20const_14states.csv")

EDA7_SRC   = os.path.join(DATA_IMP, "eda",      "eda7_scaled_mu_vs_analytical.png")
POOL_SRC   = os.path.join(DATA_IMP, "pooled",   "fig2_universal_Fx_pooled.png")
UP_SRC     = os.path.join(DATA_IMP, "per_state","UTTAR_PRADESH_fig2_universal_Fx.png")
WB_SRC     = os.path.join(DATA_IMP, "per_state","WEST_BENGAL_fig2_universal_Fx.png")

DPI = 600

# ── publication rcParams ──────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family"        : "serif",
    "font.serif"         : ["Times New Roman", "DejaVu Serif"],
    "axes.labelsize"     : 10,
    "axes.titlesize"     : 10,
    "xtick.labelsize"    : 9,
    "ytick.labelsize"    : 9,
    "legend.fontsize"    : 9,
    "figure.dpi"         : 150,
    "axes.spines.top"    : False,
    "axes.spines.right"  : False,
    "axes.linewidth"     : 0.8,
    "xtick.major.width"  : 0.8,
    "ytick.major.width"  : 0.8,
    "xtick.major.size"   : 3,
    "ytick.major.size"   : 3,
})

# ── analytical formula ────────────────────────────────────────────────────────
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

def log_histogram(values, n_bins=55):
    v = np.asarray(values, dtype=float)
    v = v[v > 0]
    if len(v) < 5:
        return np.array([]), np.array([])
    bins  = np.logspace(np.log10(v.min()), np.log10(v.max()), n_bins + 1)
    cnts, edges = np.histogram(v, bins=bins, density=True)
    centers = np.sqrt(edges[:-1] * edges[1:])
    ok = cnts > 0
    return centers[ok], cnts[ok]


# ══════════════════════════════════════════════════════════════════════════════
# FIG 3  ─  Mean Specific Margin bar chart  (redesigned for paper)
# ══════════════════════════════════════════════════════════════════════════════
def make_fig3():
    df = pd.read_csv(SUMM_CSV)
    # sort highest → lowest
    df = df.sort_values("mean_mu", ascending=True)   # ascending=True → barh shows highest at top

    RVM_MEAN = 0.1993          # theoretical RVM mean
    BAR_CLR  = "#5B7FA6"      # single neutral steel-blue for all bars
    lw_spine = 0.8

    fig_h = max(4.0, len(df) * 0.32 + 0.8)
    fig, ax = plt.subplots(figsize=(6.5, fig_h))

    bars = ax.barh(
        df["state"], df["mean_mu"],
        color=BAR_CLR, edgecolor="white", linewidth=0.4, height=0.65
    )

    # dashed theoretical line
    ax.axvline(RVM_MEAN, color="black", linestyle="--", linewidth=1.1,
               label=r"RVM theoretical mean $(\mu=0.1993)$", zorder=5)

    # value labels at end of each bar
    for bar, val in zip(bars, df["mean_mu"]):
        ax.text(
            val + 0.001,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}",
            va="center", ha="left",
            fontsize=7.5, color="#222222"
        )

    ax.set_xlabel(r"Mean Specific Margin, $\mu = M/T$", fontsize=10, labelpad=4)
    ax.set_xlim(0, max(df["mean_mu"].max() * 1.18, RVM_MEAN * 1.12))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))

    ax.legend(fontsize=8.5, frameon=True, framealpha=0.9,
              edgecolor="#cccccc", loc="lower right")

    ax.tick_params(axis="y", labelsize=8.5)
    ax.tick_params(axis="x", labelsize=8.5)
    ax.spines["left"].set_linewidth(lw_spine)
    ax.spines["bottom"].set_linewidth(lw_spine)

    fig.tight_layout(pad=0.5)
    out_path = os.path.join(OUT, "fig3_mean_specific_margin_by_state.png")
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 3 saved → {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 4  ─  EDA7: Scaled µ vs Analytical  (formal redraw, 600 dpi)
# ══════════════════════════════════════════════════════════════════════════════
def make_fig4():
    csv_path = DATA_CSV if os.path.exists(DATA_CSV) else None
    if csv_path is None:
        # fallback: just re-save the original at 600 dpi via image copy
        print("  ! Data CSV not found for Fig 4 — resampling original image to 600 dpi")
        _resave_png(EDA7_SRC, os.path.join(OUT, "fig4_scaled_mu_vs_analytical.png"))
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]

    mu_all = df["margin"].values / df["vv1"].values
    mu_all = mu_all[mu_all > 0]
    x_emp  = mu_all / mu_all.mean()

    x_anal  = np.linspace(0, 5, 600)
    Fx_anal = F_x_analytical(x_anal)

    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    ax.hist(x_emp, bins=80, density=True,
            color="#7BAFD4", edgecolor="white", linewidth=0.3,
            alpha=0.75, label="India data", zorder=2)
    ax.plot(x_anal, Fx_anal, "-", color="#C0392B", linewidth=1.8,
            label="Analytical $F(x)$", zorder=3)

    ax.set_xlim(0, 5)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=10, labelpad=4)
    ax.set_ylabel("Density", fontsize=10, labelpad=4)
    ax.legend(fontsize=9, frameon=True, framealpha=0.9, edgecolor="#cccccc")

    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    fig.tight_layout(pad=0.5)

    out_path = os.path.join(OUT, "fig4_scaled_mu_vs_analytical.png")
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ Fig 4 saved → {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 5  ─  Pooled Universal F(x)  — formal redraw
# ══════════════════════════════════════════════════════════════════════════════
def make_fig5():
    csv_path = DATA_CSV if os.path.exists(DATA_CSV) else None
    if csv_path is None:
        print("  ! Data CSV not found for Fig 5 — resampling original image")
        _resave_png(POOL_SRC, os.path.join(OUT, "fig5_universal_Fx_pooled.png"))
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]

    _plot_universal_Fx_formal(
        T=df["vv1"].values.astype(float),
        M=df["margin"].values.astype(float),
        label="All India (pooled)",
        out_path=os.path.join(OUT, "fig5_universal_Fx_pooled.png"),
        seed=42
    )
    print(f"  ✓ Fig 5 saved")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 6  ─  Uttar Pradesh Universal F(x)
# ══════════════════════════════════════════════════════════════════════════════
def make_fig6():
    csv_path = DATA_CSV if os.path.exists(DATA_CSV) else None
    if csv_path is None:
        print("  ! Data CSV not found for Fig 6 — resampling original image")
        _resave_png(UP_SRC, os.path.join(OUT, "fig6_universal_Fx_uttar_pradesh.png"))
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]
    sub = df[df["state_n"].str.strip().str.upper() == "UTTAR PRADESH"]

    _plot_universal_Fx_formal(
        T=sub["vv1"].values.astype(float),
        M=sub["margin"].values.astype(float),
        label="Uttar Pradesh",
        out_path=os.path.join(OUT, "fig6_universal_Fx_uttar_pradesh.png"),
        seed=42
    )
    print(f"  ✓ Fig 6 saved")


# ══════════════════════════════════════════════════════════════════════════════
# FIG 7  ─  West Bengal Universal F(x)
# ══════════════════════════════════════════════════════════════════════════════
def make_fig7():
    csv_path = DATA_CSV if os.path.exists(DATA_CSV) else None
    if csv_path is None:
        print("  ! Data CSV not found for Fig 7 — resampling original image")
        _resave_png(WB_SRC, os.path.join(OUT, "fig7_universal_Fx_west_bengal.png"))
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()
    df = df[(df["vv1"] > 0) & (df["margin"] >= 0) & (df["margin"] <= df["vv1"])]
    sub = df[df["state_n"].str.strip().str.upper() == "WEST BENGAL"]

    _plot_universal_Fx_formal(
        T=sub["vv1"].values.astype(float),
        M=sub["margin"].values.astype(float),
        label="West Bengal",
        out_path=os.path.join(OUT, "fig7_universal_Fx_west_bengal.png"),
        seed=42
    )
    print(f"  ✓ Fig 7 saved")


# ══════════════════════════════════════════════════════════════════════════════
# SHARED HELPER — formal Universal F(x) plot
# ══════════════════════════════════════════════════════════════════════════════
def rvm_once(turnouts, rng, n_cand=3):
    N = len(turnouts)
    margins = np.empty(N)
    for i, T in enumerate(turnouts):
        T_int = max(int(T), 2)
        w     = rng.uniform(0, 1, n_cand)
        p     = w / w.sum()
        votes = rng.multinomial(T_int, p)
        s     = np.sort(votes)[::-1]
        margins[i] = s[0] - s[1]
    return margins

def rvm_ensemble(turnouts, n_runs=20, seed=42):
    rng     = np.random.default_rng(seed)
    results = []
    for _ in range(n_runs):
        m  = rvm_once(turnouts, rng)
        mu = m / turnouts
        results.append((m, mu))
    return results

def rvm_mean_std(rvm_results, extractor, ref_x, n_bins=55):
    pdfs = []
    for (m, mu) in rvm_results:
        xr, yr = log_histogram(extractor(m, mu), n_bins)
        if len(xr) == 0:
            continue
        pdfs.append(np.interp(ref_x, xr, yr, left=np.nan, right=np.nan))
    mat = np.array(pdfs)
    return np.nanmean(mat, axis=0), np.nanstd(mat, axis=0)

def _plot_universal_Fx_formal(T, M, label, out_path, seed=42, n_runs=20):
    mu_emp  = M / T
    x_emp   = mu_emp / mu_emp.mean()
    xb, Fxb = log_histogram(x_emp)

    rvm = rvm_ensemble(T, n_runs=n_runs, seed=seed)
    rvm0_x = rvm[0][1] / rvm[0][1].mean()
    xr, _  = log_histogram(rvm0_x)
    rm, rs = rvm_mean_std(rvm, lambda m, mu: mu / mu.mean(), xr)

    x_anal  = np.logspace(-1.3, 0.8, 600)
    Fx_anal = F_x_analytical(x_anal)

    fig, ax = plt.subplots(figsize=(5.0, 4.2))

    # RVM band & mean
    ax.fill_between(xr, np.clip(rm - rs, 1e-5, None), rm + rs,
                    color="gray", alpha=0.22, zorder=1)
    ax.plot(x_anal, Fx_anal, "-", color="#C0392B", linewidth=1.8,
            label="Analytical $F(x)$", zorder=5)
    ax.plot(xr, rm, "k--", linewidth=1.1, label="RVM", zorder=4)
    ax.scatter(xb, Fxb, s=14, facecolors="none",
               edgecolors="#2471A3", linewidths=0.8,
               label=f"{label} (data)", zorder=6)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(8e-2, 1.2e1)
    ax.set_ylim(1e-3, 2e1)
    ax.set_xlabel(r"$x = \mu\,/\,\langle\mu\rangle$", fontsize=10, labelpad=4)
    ax.set_ylabel(r"$F(x)$", fontsize=10, labelpad=4)
    ax.legend(fontsize=8.5, frameon=True, framealpha=0.9,
              edgecolor="#cccccc", loc="upper right")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK — reopen PNG, set its DPI metadata to 600, re-save
# ══════════════════════════════════════════════════════════════════════════════
def _resave_png(src, dst):
    from PIL import Image
    img = Image.open(src)
    img.save(dst, dpi=(600, 600))
    print(f"  ✓ Resampled (metadata only) → {dst}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Generating publication figures (600 dpi)")
    print("="*60)

    print("\n[Fig 3] Mean Specific Margin bar chart ...")
    make_fig3()

    print("\n[Fig 4] Scaled µ vs Analytical ...")
    make_fig4()

    print("\n[Fig 5] Pooled Universal F(x) ...")
    make_fig5()

    print("\n[Fig 6] Uttar Pradesh Universal F(x) ...")
    make_fig6()

    print("\n[Fig 7] West Bengal Universal F(x) ...")
    make_fig7()

    print("\n" + "="*60)
    print(f"  All figures saved to: {OUT}")
    print("="*60 + "\n")
