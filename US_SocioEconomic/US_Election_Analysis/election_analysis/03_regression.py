"""
03_regression.py — Regression Analysis
H1: Socioeconomic drivers of turnout & vote share
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings("ignore")

CLEAN = "/home/claude/election_analysis/outputs/clean.csv"
PLOTS = "/home/claude/election_analysis/plots"
OUT   = "/home/claude/election_analysis/outputs"

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
BLUE, RED = "#3674B5", "#C0392B"

df = pd.read_csv(CLEAN, index_col=0).dropna(subset=["log_median_income"])

# ── Feature set ─────────────────────────────────────────────────────────────
FEATURES = [
    ("log_median_income",    "Log Median Income"),
    ("Gini Index",           "Gini Index"),
    ("higher_ed",            "Higher Education %"),
    ("low_ed",               "Low Education %"),
    ("log_density",          "Log Pop Density"),
    ("diversity_idx",        "Diversity Index"),
    ("NH-White percentage",  "White %"),
    ("NH-Black percentage",  "Black %"),
    ("Hispanic or Latino percentage", "Hispanic %"),
    ("Percentage engaged in Management, business, science, and arts occupations", "Mgmt/Prof Occ %"),
    ("Percentage engaged in Resources and Construction", "Resources/Constr %"),
]

feat_cols  = [f[0] for f in FEATURES]
feat_names = [f[1] for f in FEATURES]

X_raw = df[feat_cols].copy()
y_margin  = df["dem_margin"].copy()
y_turnout = df["turnout_proxy"].copy()
y_win     = df["dem_win"].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)
X_df = pd.DataFrame(X_scaled, columns=feat_names, index=df.index)

# ─────────────────────────────────────────────────────────────────────────────
# 1. OLS: each feature → Dem Margin (simple bivariate)
# ─────────────────────────────────────────────────────────────────────────────
results_simple = []
for col, name in zip(feat_cols, feat_names):
    valid = df[[col, "dem_margin"]].dropna()
    r, p = stats.pearsonr(valid[col], valid["dem_margin"])
    slope, intercept, _, _, _ = stats.linregress(valid[col], valid["dem_margin"])
    results_simple.append({
        "Feature": name,
        "Pearson r": round(r, 3),
        "p-value": round(p, 4),
        "OLS slope": round(slope, 4),
        "Significant": "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
    })

df_simple = pd.DataFrame(results_simple).sort_values("Pearson r")
df_simple.to_csv(f"{OUT}/bivariate_dem_margin.csv", index=False)
print("Bivariate OLS → Dem Margin:")
print(df_simple.to_string(index=False))

# Same for turnout
results_turn = []
for col, name in zip(feat_cols, feat_names):
    valid = df[[col, "turnout_proxy"]].dropna()
    r, p = stats.pearsonr(valid[col], valid["turnout_proxy"])
    slope, intercept, _, _, _ = stats.linregress(valid[col], valid["turnout_proxy"])
    results_turn.append({
        "Feature": name,
        "Pearson r": round(r, 3),
        "p-value": round(p, 4),
        "OLS slope": round(slope, 4),
        "Significant": "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
    })

df_turn = pd.DataFrame(results_turn).sort_values("Pearson r")
df_turn.to_csv(f"{OUT}/bivariate_turnout.csv", index=False)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Multiple OLS: all features → Dem Margin
# ─────────────────────────────────────────────────────────────────────────────
reg_margin = LinearRegression()
reg_margin.fit(X_scaled, y_margin)
y_pred_margin = reg_margin.predict(X_scaled)
r2_margin = r2_score(y_margin, y_pred_margin)
cv_r2_margin = cross_val_score(reg_margin, X_scaled, y_margin, cv=5, scoring="r2").mean()

reg_turn = LinearRegression()
reg_turn.fit(X_scaled, y_turnout)
y_pred_turn = reg_turn.predict(X_scaled)
r2_turn = r2_score(y_turnout, y_pred_turn)
cv_r2_turn = cross_val_score(reg_turn, X_scaled, y_turnout, cv=5, scoring="r2").mean()

print(f"\nMultiple OLS — Dem Margin: R²={r2_margin:.3f}, CV-R²={cv_r2_margin:.3f}")
print(f"Multiple OLS — Turnout:    R²={r2_turn:.3f}, CV-R²={cv_r2_turn:.3f}")

coef_margin = pd.DataFrame({
    "Feature": feat_names,
    "Coefficient (std)": reg_margin.coef_
}).sort_values("Coefficient (std)")

coef_turn = pd.DataFrame({
    "Feature": feat_names,
    "Coefficient (std)": reg_turn.coef_
}).sort_values("Coefficient (std)")

coef_margin.to_csv(f"{OUT}/ols_coefficients_margin.csv", index=False)
coef_turn.to_csv(f"{OUT}/ols_coefficients_turnout.csv", index=False)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Logistic regression: features → Dem Win (binary)
# ─────────────────────────────────────────────────────────────────────────────
log_reg = LogisticRegression(max_iter=500, random_state=42)
log_reg.fit(X_scaled, y_win)
acc = log_reg.score(X_scaled, y_win)
cv_acc = cross_val_score(log_reg, X_scaled, y_win, cv=5, scoring="accuracy").mean()
print(f"\nLogistic Regression — Dem Win: Accuracy={acc:.3f}, CV-Acc={cv_acc:.3f}")

coef_log = pd.DataFrame({
    "Feature": feat_names,
    "Log-odds coeff": log_reg.coef_[0]
}).sort_values("Log-odds coeff")
coef_log.to_csv(f"{OUT}/logistic_coefficients.csv", index=False)

# ─────────────────────────────────────────────────────────────────────────────
# FIG 10 — Coefficient plots
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 7))

for ax, df_coef, title, col in zip(
    axes,
    [coef_margin, coef_turn, coef_log],
    [f"OLS Coefficients → Dem Margin\n(Std. features, R²={r2_margin:.3f})",
     f"OLS Coefficients → Turnout\n(Std. features, R²={r2_turn:.3f})",
     f"Logistic Coeff → Dem Win\n(CV Accuracy={cv_acc:.3f})"],
    ["Coefficient (std)", "Coefficient (std)", "Log-odds coeff"]
):
    colors = [BLUE if v > 0 else RED for v in df_coef[col]]
    ax.barh(df_coef["Feature"], df_coef[col], color=colors, alpha=0.85, edgecolor="white")
    ax.axvline(0, color="black", lw=1.2)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Coefficient")

plt.suptitle("Regression Analysis: Socioeconomic Predictors of 2020 US County-Level Electoral Outcomes",
             fontweight="bold", y=1.02, fontsize=12)
plt.tight_layout()
fig.savefig(f"{PLOTS}/fig10_regression_coefficients.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 10 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 11 — Actual vs Predicted (OLS margin)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
residuals = y_margin - y_pred_margin

axes[0].scatter(y_pred_margin, y_margin, c=[BLUE if v > 0 else RED for v in y_margin],
                alpha=0.2, s=12)
axes[0].plot([-100, 100], [-100, 100], "k--", lw=1.5, label="Perfect prediction")
axes[0].set_xlabel("Predicted Dem Margin")
axes[0].set_ylabel("Actual Dem Margin")
axes[0].set_title(f"OLS Actual vs Predicted\n(Dem Margin, R²={r2_margin:.3f})", fontweight="bold")
axes[0].legend()

axes[1].hist(residuals, bins=50, color="#8E44AD", alpha=0.8, edgecolor="white")
axes[1].axvline(0, color="black", ls="--", lw=1.5)
axes[1].set_xlabel("Residual (pp)")
axes[1].set_ylabel("Count")
axes[1].set_title(f"Residuals — Mean={residuals.mean():.2f}, SD={residuals.std():.2f}",
                  fontweight="bold")

plt.tight_layout()
fig.savefig(f"{PLOTS}/fig11_actual_vs_predicted.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 11 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIG 12 — Education quintile analysis
# ─────────────────────────────────────────────────────────────────────────────
df["ed_quintile"] = pd.qcut(df["higher_ed"], 5,
                             labels=["Q1\n(Lowest)","Q2","Q3","Q4","Q5\n(Highest)"])
df["income_quintile"] = pd.qcut(df["log_median_income"], 5,
                                 labels=["Q1\n(Lowest)","Q2","Q3","Q4","Q5\n(Highest)"])

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, qcol, title in zip(
    axes,
    ["ed_quintile", "income_quintile"],
    ["Education Quintile (Higher Ed %)", "Income Quintile (Log Median Income)"]
):
    summary = df.groupby(qcol, observed=True).agg(
        dem_margin=("dem_margin", "mean"),
        turnout=("turnout_proxy", "mean"),
        n=("dem_margin", "count")
    ).reset_index()
    
    x = range(len(summary))
    ax2 = ax.twinx()
    bars = ax.bar(x, summary["dem_margin"], color=[BLUE if v>0 else RED for v in summary["dem_margin"]],
                  alpha=0.7, label="Dem Margin")
    line, = ax2.plot(x, summary["turnout"] * 100, "ko-", lw=2, ms=7, label="Turnout %")
    ax.axhline(0, color="gray", ls="--", lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(summary[qcol])
    ax.set_xlabel(title)
    ax.set_ylabel("Mean Dem Margin (%)", color=BLUE)
    ax2.set_ylabel("Mean Turnout × 100", color="black")
    ax.set_title(f"Electoral Outcomes by {title.split('(')[0].strip()}", fontweight="bold")
    
    lines = [bars, line]
    ax.legend([bars, line], ["Dem Margin", "Turnout × 100"], loc="upper left")

plt.tight_layout()
fig.savefig(f"{PLOTS}/fig12_quintile_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("Fig 12 saved")

# ─────────────────────────────────────────────────────────────────────────────
# Summary stats table
# ─────────────────────────────────────────────────────────────────────────────
summary_stats = {
    "Metric": [
        "N counties", "Dem wins", "Rep wins",
        "Mean Dem Margin", "Median Turnout",
        "OLS R² (Dem Margin)", "CV R² (Dem Margin)",
        "OLS R² (Turnout)", "CV R² (Turnout)",
        "Logistic CV Accuracy (Dem Win)"
    ],
    "Value": [
        len(df),
        int(df["dem_win"].sum()),
        int((1 - df["dem_win"]).sum()),
        f"{df['dem_margin'].mean():.2f} pp",
        f"{df['turnout_proxy'].median():.3f}",
        f"{r2_margin:.3f}",
        f"{cv_r2_margin:.3f}",
        f"{r2_turn:.3f}",
        f"{cv_r2_turn:.3f}",
        f"{cv_acc:.3f}"
    ]
}
pd.DataFrame(summary_stats).to_csv(f"{OUT}/model_summary.csv", index=False)
print("\nModel summary saved")
print("\n✓ All regression outputs done")
