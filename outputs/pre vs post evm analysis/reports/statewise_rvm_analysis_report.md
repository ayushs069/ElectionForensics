# State-Wise Rescaled Vote Model (RVM) Analysis Report
## Comparative Study: Pre-EVM (1951–1999) vs Nationwide-EVM (2004–2019)

**Date Generated**: 2026-10-18 16:00:52  
**Dataset**: Indian Parliamentary Elections (14 Major States)  
**Pre-EVM Data File**: `outputs/pre vs post evm analysis/data/data_pre_evm.csv`  
**Post-EVM Data File**: `outputs/pre vs post evm analysis/data/data_post_evm.csv`  
**Methodology**: Relative/Rescaled Vote Model (RVM) 3-candidate null hypothesis  
**Output Directory**: `outputs/pre vs post evm analysis/figures/statewise/`

---

## Executive Summary

This report provides an in-depth, state-wise evaluation of the empirical scaled margin distributions $F(x)$
across all **14 major Indian states**, contrasting the **pre-EVM epoch (1951–1999)** against the **nationwide-EVM
epoch (2004–2019)**. The analysis strictly preserves the mathematical and empirical framework of the Rescaled
Vote Model (RVM), where specific victory margin $\mu = M / T$ is normalized by its sample mean $x = \mu / \langle\mu\rangle$.

Key takeaways:
1. **All 14 states were successfully analyzed** with side-by-side comparative RVM figures generated in both PNG and PDF formats.
2. **Data Sufficiency**: Every state meets or exceeds the required threshold of $N \ge 50$ in both periods.
   The smallest post-EVM samples are Punjab ($N=52$) and Assam ($N=56$), while Uttar Pradesh represents the largest ($N=1,071$ pre, $N=317$ post).
3. **Election Year Assignment Validation**: All 4 post-EVM elections (2004, 2009, 2014, 2019) are present across all 14 states.
   Standard pre-EVM general elections (1951–1999, 13 elections) are verified, with historical adjustments accounted for (Gujarat starting post-1960 reorganisation; Assam and Punjab experiencing election postponements in 1984/1991 due to civil unrest).
4. **RVM Scaling Fidelity**: Across both epochs, the universal scaling curve $F(x)$ demonstrates remarkable alignment
   with the theoretical RVM null prediction, affirming that the underlying rescaled competition structure remained robust following electronic voting adoption.

---

## 1. Election Year Validation & Historical Context

The classification rigorously distinguishes standard parliamentary general elections from by-elections:
- **Pre-EVM Cohort (1951–1999)**: 13 general elections (1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999).
- **Post-EVM Cohort (2004–2019)**: 4 nationwide general elections (2004, 2009, 2014, 2019).
- **Excluded Years**: 1985 ($n=27$) and 1992 ($n=13$), representing localized by-election batches.

### State-Wise Election Attendance Audit

| State | Pre Elections Count | Pre Years Present | Pre Missing Years | Post Elections Count | Historical Notes |
|:------|:-------------------:|:------------------|:------------------|:--------------------:|:-----------------|
| **Andhra Pradesh** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Assam** | 11 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1991, 1996, 1998, 1999 | `1984, 1989` | 4 | Pre-EVM missing [1984, 1989] (Assam Agitation/instability) |
| **Bihar** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Gujarat** | 12 | 1951, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `1957` | 4 | 1957 absent (state formed 1960 from Bombay State) |
| **Karnataka** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Kerala** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Madhya Pradesh** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Maharashtra** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Odisha** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Punjab** | 11 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1989, 1996, 1998, 1999 | `1984, 1991` | 4 | Pre-EVM missing [1984, 1991] (President's rule/militancy) |
| **Rajasthan** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Tamil Nadu** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **Uttar Pradesh** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |
| **West Bengal** | 13 | 1951, 1957, 1962, 1967, 1971, 1977, 1980, 1984, 1989, 1991, 1996, 1998, 1999 | `None` | 4 | All standard general elections present |

---

## 2. Sample Size & Data Sufficiency Evaluation

To ensure statistical validity and prevent small-sample artifacts in log-histogram density estimation, each state
was audited against minimum threshold criteria ($N \ge 10$ absolute minimum, $N \ge 50$ robust power):

| State | N (Pre-EVM) | N (Post-EVM) | Total N | Pre $\ge 50$ | Post $\ge 50$ | Sufficiency Status | Notes |
|:------|:-----------:|:------------:|:-------:|:------------:|:-------------:|:------------------:|:------|
| **Andhra Pradesh** | 512 | 151 | 663 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Assam** | 130 | 56 | 186 | ✓ | ✓ | **Adequate (Marginal Post-EVM Sample)** | Post-EVM N=56 (< 70) |
| **Bihar** | 678 | 160 | 838 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Gujarat** | 285 | 104 | 389 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Karnataka** | 335 | 112 | 447 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Kerala** | 243 | 80 | 323 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Madhya Pradesh** | 491 | 116 | 607 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Maharashtra** | 613 | 192 | 805 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Odisha** | 256 | 84 | 340 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Punjab** | 162 | 52 | 214 | ✓ | ✓ | **Adequate (Marginal Post-EVM Sample)** | Post-EVM N=52 (< 70) |
| **Rajasthan** | 304 | 100 | 404 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Tamil Nadu** | 524 | 155 | 679 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **Uttar Pradesh** | 1,071 | 317 | 1,388 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |
| **West Bengal** | 506 | 168 | 674 | ✓ | ✓ | **Sufficient** | Fully powered (N >= 50 in both eras) |

> **Sufficiency Verdict**: All 14 states have sufficient data ($N \ge 50$ in both periods) to construct empirical $F(x)$ curves and conduct two-sample Kolmogorov-Smirnov and Mann-Whitney U tests. No states need to be dropped or disqualified from the comparative analysis.

---

## 3. Comprehensive State-Wise RVM Metrics

Below are the primary statistical metrics and hypothesis test outcomes comparing specific victory margin $\mu = M / T$:

| State | N (Pre / Post) | Mean $\mu$ (Pre) | Mean $\mu$ (Post) | $\Delta\langle\mu\rangle$ | % Change | KS Statistic | KS $p$-value | MW $p$-value | Fraud $|z|$ (Pre / Post) |
|:------|:--------------:|:----------------:|:-----------------:|:--------------------------:|:--------:|:------------:|:------------:|:------------:|:-------------------------:|
| **Andhra Pradesh** | 512 / 151 | 0.1568 | 0.0943 | -0.0625 | -39.9% | 0.2210 | 1.75e-05 | 1.11e-04 | 1.33 / 0.90 |
| **Assam** | 130 / 56 | 0.1877 | 0.1155 | -0.0722 | -38.5% | 0.3225 | 3.98e-04 | 3.33e-04 | 0.97 / 0.87 |
| **Bihar** | 678 / 160 | 0.1798 | 0.1395 | -0.0402 | -22.4% | 0.1450 | 7.61e-03 | 2.20e-02 | 1.13 / 1.34 |
| **Gujarat** | 285 / 104 | 0.1619 | 0.1772 | +0.0152 | +9.4% | 0.0909 | 5.19e-01 | 5.00e-01 | 1.15 / 0.75 |
| **Karnataka** | 335 / 112 | 0.1800 | 0.0931 | -0.0869 | -48.3% | 0.3436 | 2.79e-09 | 2.10e-09 | 1.03 / 0.75 |
| **Kerala** | 243 / 80 | 0.0949 | 0.0829 | -0.0120 | -12.6% | 0.1148 | 3.71e-01 | 7.01e-01 | 0.77 / 0.83 |
| **Madhya Pradesh** | 491 / 116 | 0.1710 | 0.1762 | +0.0053 | +3.1% | 0.0716 | 6.89e-01 | 4.13e-01 | 1.13 / 0.96 |
| **Maharashtra** | 613 / 192 | 0.1922 | 0.1352 | -0.0570 | -29.6% | 0.1663 | 5.22e-04 | 8.68e-06 | 1.65 / 0.91 |
| **Odisha** | 256 / 84 | 0.1789 | 0.1142 | -0.0648 | -36.2% | 0.2656 | 1.98e-04 | 7.14e-05 | 1.66 / 0.77 |
| **Punjab** | 162 / 52 | 0.1407 | 0.0716 | -0.0691 | -49.1% | 0.3079 | 8.17e-04 | 1.31e-04 | 0.92 / 2.06 |
| **Rajasthan** | 304 / 100 | 0.1653 | 0.1807 | +0.0154 | +9.3% | 0.1362 | 1.10e-01 | 7.74e-02 | 1.15 / 0.90 |
| **Tamil Nadu** | 524 / 155 | 0.1696 | 0.1717 | +0.0021 | +1.2% | 0.1563 | 5.03e-03 | 4.15e-01 | 1.48 / 1.62 |
| **Uttar Pradesh** | 1071 / 317 | 0.1642 | 0.1288 | -0.0354 | -21.5% | 0.1145 | 2.96e-03 | 6.11e-03 | 0.88 / 0.88 |
| **West Bengal** | 506 / 168 | 0.1261 | 0.1274 | +0.0012 | +1.0% | 0.1139 | 6.88e-02 | 7.09e-01 | 1.10 / 1.10 |

---

## 4. State-by-State Analytical Findings

### Andhra Pradesh
- **Figure File**: [`andhra_pradesh_pre_vs_post_rvm.png`](../figures/statewise/andhra_pradesh_pre_vs_post_rvm.png) | Vector PDF: [`andhra_pradesh_pre_vs_post_rvm.pdf`](../figures/statewise/andhra_pradesh_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 512$, Post-EVM $n = 151$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1568$ (Pre-EVM) to $0.0943$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0625$ (-39.9%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.2210$ with $p = 1.75e-05$; Mann-Whitney U test gives $p = 1.11e-04$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.329$; Post-EVM mean $|z| = 0.905$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Assam
- **Figure File**: [`assam_pre_vs_post_rvm.png`](../figures/statewise/assam_pre_vs_post_rvm.png) | Vector PDF: [`assam_pre_vs_post_rvm.pdf`](../figures/statewise/assam_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 130$, Post-EVM $n = 56$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1877$ (Pre-EVM) to $0.1155$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0722$ (-38.5%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.3225$ with $p = 3.98e-04$; Mann-Whitney U test gives $p = 3.33e-04$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 0.966$; Post-EVM mean $|z| = 0.870$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Bihar
- **Figure File**: [`bihar_pre_vs_post_rvm.png`](../figures/statewise/bihar_pre_vs_post_rvm.png) | Vector PDF: [`bihar_pre_vs_post_rvm.pdf`](../figures/statewise/bihar_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 678$, Post-EVM $n = 160$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1798$ (Pre-EVM) to $0.1395$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0402$ (-22.4%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1450$ with $p = 7.61e-03$; Mann-Whitney U test gives $p = 2.20e-02$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.135$; Post-EVM mean $|z| = 1.340$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Gujarat
- **Figure File**: [`gujarat_pre_vs_post_rvm.png`](../figures/statewise/gujarat_pre_vs_post_rvm.png) | Vector PDF: [`gujarat_pre_vs_post_rvm.pdf`](../figures/statewise/gujarat_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 285$, Post-EVM $n = 104$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1619$ (Pre-EVM) to $0.1772$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = +0.0152$ (+9.4%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.0909$ with $p = 5.19e-01$; Mann-Whitney U test gives $p = 5.00e-01$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.152$; Post-EVM mean $|z| = 0.754$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Karnataka
- **Figure File**: [`karnataka_pre_vs_post_rvm.png`](../figures/statewise/karnataka_pre_vs_post_rvm.png) | Vector PDF: [`karnataka_pre_vs_post_rvm.pdf`](../figures/statewise/karnataka_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 335$, Post-EVM $n = 112$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1800$ (Pre-EVM) to $0.0931$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0869$ (-48.3%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.3436$ with $p = 2.79e-09$; Mann-Whitney U test gives $p = 2.10e-09$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.027$; Post-EVM mean $|z| = 0.755$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Kerala
- **Figure File**: [`kerala_pre_vs_post_rvm.png`](../figures/statewise/kerala_pre_vs_post_rvm.png) | Vector PDF: [`kerala_pre_vs_post_rvm.pdf`](../figures/statewise/kerala_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 243$, Post-EVM $n = 80$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.0949$ (Pre-EVM) to $0.0829$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0120$ (-12.6%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1148$ with $p = 3.71e-01$; Mann-Whitney U test gives $p = 7.01e-01$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 0.775$; Post-EVM mean $|z| = 0.835$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Madhya Pradesh
- **Figure File**: [`madhya_pradesh_pre_vs_post_rvm.png`](../figures/statewise/madhya_pradesh_pre_vs_post_rvm.png) | Vector PDF: [`madhya_pradesh_pre_vs_post_rvm.pdf`](../figures/statewise/madhya_pradesh_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 491$, Post-EVM $n = 116$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1710$ (Pre-EVM) to $0.1762$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = +0.0053$ (+3.1%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.0716$ with $p = 6.89e-01$; Mann-Whitney U test gives $p = 4.13e-01$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.130$; Post-EVM mean $|z| = 0.958$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Maharashtra
- **Figure File**: [`maharashtra_pre_vs_post_rvm.png`](../figures/statewise/maharashtra_pre_vs_post_rvm.png) | Vector PDF: [`maharashtra_pre_vs_post_rvm.pdf`](../figures/statewise/maharashtra_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 613$, Post-EVM $n = 192$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1922$ (Pre-EVM) to $0.1352$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0570$ (-29.6%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1663$ with $p = 5.22e-04$; Mann-Whitney U test gives $p = 8.68e-06$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.654$; Post-EVM mean $|z| = 0.907$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Odisha
- **Figure File**: [`odisha_pre_vs_post_rvm.png`](../figures/statewise/odisha_pre_vs_post_rvm.png) | Vector PDF: [`odisha_pre_vs_post_rvm.pdf`](../figures/statewise/odisha_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 256$, Post-EVM $n = 84$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1789$ (Pre-EVM) to $0.1142$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0648$ (-36.2%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.2656$ with $p = 1.98e-04$; Mann-Whitney U test gives $p = 7.14e-05$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.663$; Post-EVM mean $|z| = 0.770$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Punjab
- **Figure File**: [`punjab_pre_vs_post_rvm.png`](../figures/statewise/punjab_pre_vs_post_rvm.png) | Vector PDF: [`punjab_pre_vs_post_rvm.pdf`](../figures/statewise/punjab_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 162$, Post-EVM $n = 52$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1407$ (Pre-EVM) to $0.0716$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0691$ (-49.1%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.3079$ with $p = 8.17e-04$; Mann-Whitney U test gives $p = 1.31e-04$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 0.922$; Post-EVM mean $|z| = 2.062$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Rajasthan
- **Figure File**: [`rajasthan_pre_vs_post_rvm.png`](../figures/statewise/rajasthan_pre_vs_post_rvm.png) | Vector PDF: [`rajasthan_pre_vs_post_rvm.pdf`](../figures/statewise/rajasthan_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 304$, Post-EVM $n = 100$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1653$ (Pre-EVM) to $0.1807$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = +0.0154$ (+9.3%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1362$ with $p = 1.10e-01$; Mann-Whitney U test gives $p = 7.74e-02$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.155$; Post-EVM mean $|z| = 0.899$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Tamil Nadu
- **Figure File**: [`tamil_nadu_pre_vs_post_rvm.png`](../figures/statewise/tamil_nadu_pre_vs_post_rvm.png) | Vector PDF: [`tamil_nadu_pre_vs_post_rvm.pdf`](../figures/statewise/tamil_nadu_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 524$, Post-EVM $n = 155$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1696$ (Pre-EVM) to $0.1717$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = +0.0021$ (+1.2%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1563$ with $p = 5.03e-03$; Mann-Whitney U test gives $p = 4.15e-01$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.476$; Post-EVM mean $|z| = 1.622$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### Uttar Pradesh
- **Figure File**: [`uttar_pradesh_pre_vs_post_rvm.png`](../figures/statewise/uttar_pradesh_pre_vs_post_rvm.png) | Vector PDF: [`uttar_pradesh_pre_vs_post_rvm.pdf`](../figures/statewise/uttar_pradesh_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 1,071$, Post-EVM $n = 317$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1642$ (Pre-EVM) to $0.1288$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = -0.0354$ (-21.5%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1145$ with $p = 2.96e-03$; Mann-Whitney U test gives $p = 6.11e-03$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 0.877$; Post-EVM mean $|z| = 0.879$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

### West Bengal
- **Figure File**: [`west_bengal_pre_vs_post_rvm.png`](../figures/statewise/west_bengal_pre_vs_post_rvm.png) | Vector PDF: [`west_bengal_pre_vs_post_rvm.pdf`](../figures/statewise/west_bengal_pre_vs_post_rvm.pdf)
- **Sample Sizes**: Pre-EVM $n = 506$, Post-EVM $n = 168$
- **Specific Margin Evolution**: Mean margin shifted from $\langle\mu\rangle = 0.1261$ (Pre-EVM) to $0.1274$ (Post-EVM), representing a change of $\Delta\langle\mu\rangle = +0.0012$ (+1.0%).
- **Distributional Test**: Kolmogorov-Smirnov test yields $D = 0.1139$ with $p = 6.88e-02$; Mann-Whitney U test gives $p = 7.09e-01$.
- **RVM Deviation (Fraud Score)**: Pre-EVM mean $|z| = 1.100$; Post-EVM mean $|z| = 1.097$. Both remain comfortably below the $|z| > 3.0$ anomaly threshold.
- **Visual Fit**: The side-by-side plot illustrates that both Pre-EVM (left) and Post-EVM (right) empirical distributions closely track the theoretical analytical RVM curve $F(x)$ within the simulated $\pm 1\sigma$ ensemble band.

---

## 5. Catalog of Generated Figures

All 14 side-by-side comparison figures are stored in `outputs/pre vs post evm analysis/figures/statewise/`:

1. **Andhra Pradesh**: `andhra_pradesh_pre_vs_post_rvm.png` / `.pdf`
2. **Assam**: `assam_pre_vs_post_rvm.png` / `.pdf`
3. **Bihar**: `bihar_pre_vs_post_rvm.png` / `.pdf`
4. **Gujarat**: `gujarat_pre_vs_post_rvm.png` / `.pdf`
5. **Karnataka**: `karnataka_pre_vs_post_rvm.png` / `.pdf`
6. **Kerala**: `kerala_pre_vs_post_rvm.png` / `.pdf`
7. **Madhya Pradesh**: `madhya_pradesh_pre_vs_post_rvm.png` / `.pdf`
8. **Maharashtra**: `maharashtra_pre_vs_post_rvm.png` / `.pdf`
9. **Odisha**: `odisha_pre_vs_post_rvm.png` / `.pdf`
10. **Punjab**: `punjab_pre_vs_post_rvm.png` / `.pdf`
11. **Rajasthan**: `rajasthan_pre_vs_post_rvm.png` / `.pdf`
12. **Tamil Nadu**: `tamil_nadu_pre_vs_post_rvm.png` / `.pdf`
13. **Uttar Pradesh**: `uttar_pradesh_pre_vs_post_rvm.png` / `.pdf`
14. **West Bengal**: `west_bengal_pre_vs_post_rvm.png` / `.pdf`

---

## 6. Methodological Notes & Reproducibility

- **RVM Null Model**: Assumes a 3-candidate uniform Dirichlet distribution over the unit simplex with multinomial voter choice for each constituency.
- **Scaling Variable**: $x = \mu / \langle\mu\rangle$, where $\mu = (V_{\text{winner}} - V_{\text{runner-up}}) / T$.
- **Reproducibility Command**:
  ```bash
  python src/statewise_rvm_analysis.py --runs 25 --dpi 300
  ```
- **Scientific Disclaimer**: Statistical differences in margin sizes between historical epochs reflect multifaceted electoral dynamics, including constituency delimitation (notably the 2008 Delimitation), expanding voter registries, multi-party fragmentation, and turnout fluctuations. The RVM serves as a physics-inspired null model of proportional competition.
