# Pre-EVM vs Post-EVM Indian Parliamentary Election Analysis
## Comparative Study of Four Pre-EVM (1991–1999) vs Four Post-EVM (2004–2019) General Elections

**Date Generated**: 2026-10-24 19:29:57  
**Data File**: `data/processed/final_20const_14states.csv`  
**Methodology**: Relative Vote Model (RVM) 3-candidate null distribution & analytical universality  
**Output Directory**: `outputs/pre vs post evm last 4 yrs/`  
**Simulation Runs**: 25 ensemble runs per cohort  
**Plot Resolution**: 600 DPI (Publication Quality)  

---

## Executive Summary

To perform a methodologically fair and temporally balanced comparison, this study restricts analysis to the **four general elections immediately preceding nationwide Electronic Voting Machine (EVM) adoption** (1991, 1996, 1998, 1999) against the **four general elections conducted under nationwide EVM coverage** (2004, 2009, 2014, 2019).

### Key Findings:
1. **Sample Size Parity**: The balanced 4-vs-4 framework yields **1,972** pre-EVM constituency-elections and **1,847** post-EVM constituency-elections across 14 major Indian states. This eliminates the severe sample-size imbalance present when aggregating 1951–1999 (which pooled 13 elections over 48 years).
2. **Specific Margin Shift**: The pooled empirical mean specific margin (margin divided by total valid votes, $\mu = M/T$) shifted from **0.1136** in the pre-EVM cohort to **0.1327** in the post-EVM cohort (difference: $\Delta\langle\mu\rangle = +0.0191$, relative change: **+16.8%**). The median margin shifted from **0.0884** to **0.1092**.
3. **Statistical Significance vs Effect Size**: The difference between the two distributions is statistically significant due to the large sample size (Kolmogorov-Smirnov $D = 0.1006$, $p = 7.25e-09$; Mann-Whitney $U = 1619702$, $p = 3.30e-09$). However, the standardized effect size is small (Cohen's $d = +0.188$).
4. **RVM Null Model Adherence**: Both pre-EVM and post-EVM scaled specific margin distributions ($x = \mu / \langle\mu\rangle$) adhere strongly to the analytical universal curve $F(x)$ and the simulated RVM bands. Neither pooled cohort nor any individual state crossed the established deviation threshold ($|z| > 3.0$), indicating consistent universal structural behavior across both technological regimes.

---

## 1. Study Design & Methodological Rationale

### Why a Matched 4-Election Window is Methodologically Superior:
- **Controlling Secular Political Evolution**: In 1989–1991, the Indian political system underwent a structural transition away from the single-party dominant Congress system into an era of multi-party coalition politics, Mandal-Mandir social mobilizations, and regional party proliferation. Comparing 1991–1999 with 2004–2019 controls for party-system fragmentation and voter turnout maturity.
- **Temporal Window Balance**: 1991–1999 spans ~8 years (4 elections: 1991, 1996, 1998, 1999) whereas 2004–2019 spans 15 years (4 elections: 2004, 2009, 2014, 2019). This prevents 1950s agrarian electoral dynamics from distorting the baseline.
- **Sample Balance**: 1,972 vs 1,847 records (nearly a 1:1 ratio) prevents the pre-EVM era from dominating the variance structure.
- **Technological Transition Note**: EVMs were piloted experimentally in select state assembly and parliamentary constituencies between 1982 and 2003, but 2004 marked the definitive nationwide transition across all 543 Lok Sabha constituencies.

---

## 2. Pooled 14-State Statistical Comparison

| Metric | Pre-EVM (1991–1999) | Post-EVM (2004–2019) | Absolute Shift | Relative Shift |
|:---|:---:|:---:|:---:|:---:|
| **Elections Analyzed** | 4 (1991, 1996, 1998, 1999) | 4 (2004, 2009, 2014, 2019) | — | — |
| **Total Sample Size (N)** | 1,972 | 1,847 | -125 | -6.3% |
| **Mean Specific Margin <mu>** | 0.11362 | 0.13273 | +0.01912 | +16.8% |
| **95% Confidence Interval** | [0.10931, 0.11792] | [0.12790, 0.13756] | — | — |
| **Median Specific Margin** | 0.08841 | 0.10920 | +0.02079 | +23.5% |
| **Standard Deviation** | 0.09744 | 0.10585 | +0.00841 | — |
| **Theoretical Expectation <mu>_theory** | 0.19929 | 0.19929 | — | — |

### Hypothesis Tests & Effect Sizes:
- **Kolmogorov-Smirnov Test**: $D = 0.1006$, $p = 7.2522e-09$
- **Mann-Whitney U Test**: $U = 1619702$, $p = 3.3018e-09$
- **Welch's Two-Sample t-Test**: $t = -5.7952$, $p = 7.3866e-09$
- **Cohen's d (Standardized Effect Size)**: $d = +0.1882$ (indicates a small standardized shift)

---

## 3. State-Wise Comparison (All 14 Major States)

| State | N Pre | N Post | Mean Pre | Mean Post | Δμ | % Change | Median Pre | Median Post | KS p-value | RVM |z| Pre | RVM |z| Post | Status |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Andhra Pradesh | 168 | 151 | 0.0812 | 0.0943 | +0.0131 | +16.1% | 0.0651 | 0.0784 | 1.50e-02 | 0.989 | 0.905 | Pass |
| Assam | 56 | 56 | 0.1387 | 0.1155 | -0.0232 | -16.7% | 0.1105 | 0.0879 | 4.68e-01 | 0.699 | 0.870 | Pass |
| Bihar | 214 | 160 | 0.1204 | 0.1395 | +0.0192 | +15.9% | 0.0981 | 0.1200 | 7.27e-02 | 1.089 | 1.340 | Pass |
| Gujarat | 104 | 104 | 0.1433 | 0.1772 | +0.0339 | +23.6% | 0.1135 | 0.1517 | 3.04e-01 | 1.642 | 0.754 | Pass |
| Karnataka | 112 | 112 | 0.0967 | 0.0931 | -0.0036 | -3.7% | 0.0834 | 0.0750 | 9.39e-01 | 0.807 | 0.755 | Pass |
| Kerala | 80 | 80 | 0.0552 | 0.0829 | +0.0277 | +50.2% | 0.0367 | 0.0759 | 2.55e-03 | 0.802 | 0.835 | Pass |
| Madhya Pradesh | 160 | 116 | 0.1054 | 0.1762 | +0.0709 | +67.2% | 0.0880 | 0.1495 | 1.93e-05 | 1.007 | 0.958 | Pass |
| Maharashtra | 192 | 192 | 0.1279 | 0.1352 | +0.0073 | +5.7% | 0.1087 | 0.1173 | 5.19e-01 | 0.853 | 0.907 | Pass |
| Odisha | 84 | 84 | 0.1373 | 0.1142 | -0.0231 | -16.8% | 0.1275 | 0.0945 | 2.68e-01 | 1.235 | 0.770 | Pass |
| Punjab | 39 | 52 | 0.0859 | 0.0716 | -0.0143 | -16.6% | 0.0833 | 0.0596 | 1.63e-01 | 0.827 | 2.062 | Pass |
| Rajasthan | 100 | 100 | 0.1000 | 0.1807 | +0.0807 | +80.7% | 0.0916 | 0.1704 | 3.75e-06 | 1.142 | 0.899 | Pass |
| Tamil Nadu | 156 | 155 | 0.1866 | 0.1717 | -0.0149 | -8.0% | 0.1821 | 0.1630 | 1.57e-02 | 1.362 | 1.622 | Pass |
| Uttar Pradesh | 339 | 317 | 0.0887 | 0.1288 | +0.0401 | +45.2% | 0.0637 | 0.0967 | 1.64e-05 | 1.020 | 0.879 | Pass |
| West Bengal | 168 | 168 | 0.1265 | 0.1274 | +0.0009 | +0.7% | 0.1093 | 0.1158 | 6.06e-01 | 0.919 | 1.097 | Pass |

---

## 4. Election Year Audit & Historical Nuances

| State | Pre Elections | Pre Missing | Post Elections | Post Missing | Historical Context |
|:---|:---:|:---:|:---:|:---:|:---|
| Andhra Pradesh | 4 | None | 4 | None | Telangana carved out in 2014; residual AP seats reflected in 2019. |
| Assam | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Bihar | 4 | None | 4 | None | Bifurcated in Nov 2000 (Jharkhand, Chhattisgarh, Uttarakhand carved out); seat count lowered post-2000. |
| Gujarat | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Karnataka | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Kerala | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Madhya Pradesh | 4 | None | 4 | None | Bifurcated in Nov 2000 (Jharkhand, Chhattisgarh, Uttarakhand carved out); seat count lowered post-2000. |
| Maharashtra | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Odisha | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Punjab | 3 | 1991 | 4 | None | 1991 general elections in Punjab cancelled due to militant insurgency; polls held in 1992. |
| Rajasthan | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Tamil Nadu | 4 | None | 4 | None | Complete 4 general elections in both eras. |
| Uttar Pradesh | 4 | None | 4 | None | Bifurcated in Nov 2000 (Jharkhand, Chhattisgarh, Uttarakhand carved out); seat count lowered post-2000. |
| West Bengal | 4 | None | 4 | None | Complete 4 general elections in both eras. |

---

## 5. Visual Artifacts Generated

All figures have been rendered at **600 DPI** and accompanied by vector PDF counterparts:

### Overview Figures (`outputs/pre vs post evm last 4 yrs/figures/`):
1. **`fig01_pooled_Fx_pre_vs_post.png`**: Side-by-side universal $F(x)$ empirical distributions vs analytical universal curve and simulated RVM band.
2. **`fig02_pooled_scaled_margin.png`**: Scaled margin $M/\langle M\rangle$ log-log density comparison.
3. **`fig03_mean_margin_comparison.png`**: Pooled mean (with 95% CIs) and median specific margin bar plots.
4. **`fig04_sample_sizes.png`**: Grouped bar chart of constituency counts per state across both eras.
5. **`fig05_statewise_mean_margin.png`**: State-by-state mean specific margin comparison.
6. **`fig06_statewise_Fx_grid.png`**: 14-panel grid overlaying pre- and post-EVM empirical $F(x)$ with analytical theory.
7. **`fig07_fraud_score_comparison.png`**: State-wise comparison of RVM deviation $|z|$-scores vs the $|z|=3.0$ threshold.
8. **`fig08_mu_kde_pre_vs_post.png`**: Continuous Kernel Density Estimation (KDE) comparing specific margin distributions.
9. **`fig09_yearly_trend.png`**: Year-by-year trajectory through 1991, 1996, 1998, 1999, 2004, 2009, 2014, and 2019.
10. **`fig10_statewise_delta_margin.png`**: Sorted horizontal bar chart of margin differences (Post minus Pre) per state.

### State-Wise Detailed Figures (`outputs/pre vs post evm last 4 yrs/figures/statewise/`):
- 14 individual side-by-side figures (`andhra_pradesh_pre_vs_post_rvm.png`, `bihar_pre_vs_post_rvm.png`, ..., `west_bengal_pre_vs_post_rvm.png`).

---

## 6. Rigorous Interpretation & Scientific Guardrails

1. **Statistical Associations vs Causal Inference**: Observed changes between the 1991–1999 and 2004–2019 general elections represent statistical associations across distinct historical eras. They **do not prove that EVMs caused margin changes** nor do they provide evidence of electoral fraud.
2. **Confounding Factors**:
   - **Delimitation Commission of 2008**: Substantial redrawing of constituency boundaries between the 2004 and 2009 elections altered demographic compositions.
   - **State Reorganizations (2000 & 2014)**: The creation of Chhattisgarh (from MP), Jharkhand (from Bihar), Uttarakhand (from UP) in late 2000, and Telangana (from AP) in 2014 altered state-level seat compositions.
   - **Voter Turnout & Registration Dynamics**: Total valid votes ($vv1$) increased substantially due to demographic expansion, higher youth registration, and increased voter turnout drives by the Election Commission of India (ECI).
   - **Bipolarization vs Multipolarization**: State-specific shifts in coalition arrangements (e.g. NDA vs UPA vs regional third fronts) directly influence winning margins independently of voting hardware.
3. **Null Model Validity**: The Rescaled Vote Model (RVM) serves as an idealized null baseline. Strong compliance with $F(x)$ confirms that voting margins in Indian parliamentary elections largely preserve universal statistical properties across both paper ballot and electronic ballot eras.

---

## 7. Reproducibility

To reproduce the exact analysis, tables, figures, and report, run:
```bash
python src/pre_post_evm_last4yrs.py --runs 25 --dpi 600 --seed 42
```

- **Python**: 3.13.2  
- **NumPy**: 2.2.6  
- **Pandas**: 2.3.3  
- **SciPy**: 1.15.1  
- **Matplotlib**: 3.10.6

---
*Report compiled automatically by the ElectionForensics RVM pipeline.*