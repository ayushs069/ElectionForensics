# Pre-EVM vs Post-EVM Indian Parliamentary Election Analysis

**Generated**: 2026-10-18 15:41:46  
**Dataset**: `final_20const_14states.csv`  
**Script**: `src/pre_post_evm_analysis.py`  
**RVM runs per group**: 25  
**Output DPI**: 600

---

## 1. Data Overview

| Category | Years | Count |
|----------|-------|-------|
| Pre-EVM elections | [np.int64(1951), np.int64(1957), np.int64(1962), np.int64(1967), np.int64(1971), np.int64(1977), np.int64(1980), np.int64(1984), np.int64(1989), np.int64(1991), np.int64(1996), np.int64(1998), np.int64(1999)] | 6,110 constituency-elections |
| Post-EVM elections | [np.int64(2004), np.int64(2009), np.int64(2014), np.int64(2019)] | 1,847 constituency-elections |
| **Excluded** (by-election batches) | [np.int64(1985), np.int64(1992)] | — |

> **EVM cutoff**: 2004. EVMs were introduced experimentally before 2004 in some
> constituencies but were adopted nationwide for the 2004 general election.
> The 1985 (n=27) and 1992 (n=13) rows are mid-term/by-election batches and
> are excluded from both groups to avoid sample-size bias.

---

## 2. Pooled Statistical Comparison (14 States)

| Metric | Pre-EVM | Post-EVM |
|--------|---------|----------|
| N | 6,110 | 1,847 |
| Mean μ | 0.164526 | 0.132732 |
| Median μ | 0.128032 | 0.109204 |
| Std dev | 0.137300 | 0.105849 |
| 95% CI (mean) | (0.16108, 0.16797) | (0.12790, 0.13756) |
| Theoretical ⟨μ⟩ | 0.199289 | 0.199289 |

**Relative change**: -19.32%  
**Cohen's d**: 0.2433  
**Mann-Whitney U**: 6257441 (p = 1.1829e-12)  
**KS statistic**: 0.1010 (p = 4.8403e-13)

---

## 3. State-wise Summary

| State | N Pre | N Post | Mean μ Pre | Mean μ Post | Δμ | KS p | Fraud Pre | Fraud Post |
|-------|-------|--------|------------|-------------|-----|------|-----------|------------|
| Andhra Pradesh | 512 | 151 | 0.15681 | 0.09430 | -0.06251 | 1.749e-05 | 1.825 | 0.860 |
| Assam | 130 | 56 | 0.18767 | 0.11548 | -0.07219 | 3.980e-04 | 0.984 | 0.732 |
| Bihar | 678 | 160 | 0.17977 | 0.13954 | -0.04023 | 7.609e-03 | 1.129 | 1.042 |
| Gujarat | 285 | 104 | 0.16195 | 0.17716 | +0.01522 | 5.189e-01 | 1.026 | 0.846 |
| Karnataka | 335 | 112 | 0.18004 | 0.09313 | -0.08691 | 2.788e-09 | 0.871 | 0.914 |
| Kerala | 243 | 80 | 0.09487 | 0.08288 | -0.01199 | 3.708e-01 | 1.240 | 0.619 |
| Madhya Pradesh | 491 | 116 | 0.17098 | 0.17624 | +0.00525 | 6.895e-01 | 1.061 | 0.865 |
| Maharashtra | 613 | 192 | 0.19224 | 0.13524 | -0.05699 | 5.221e-04 | 1.347 | 0.908 |
| Odisha | 256 | 84 | 0.17891 | 0.11416 | -0.06475 | 1.978e-04 | 1.168 | 0.930 |
| Punjab | 162 | 52 | 0.14069 | 0.07164 | -0.06905 | 8.168e-04 | 0.840 | 1.837 |
| Rajasthan | 304 | 100 | 0.16534 | 0.18071 | +0.01536 | 1.099e-01 | 0.930 | 0.871 |
| Tamil Nadu | 524 | 155 | 0.16956 | 0.17167 | +0.00212 | 5.035e-03 | 1.210 | 1.137 |
| Uttar Pradesh | 1071 | 317 | 0.16418 | 0.12882 | -0.03536 | 2.960e-03 | 0.705 | 0.871 |
| West Bengal | 506 | 168 | 0.12614 | 0.12735 | +0.00121 | 6.875e-02 | 0.961 | 0.965 |

---

## 4. Interpretation

- All differences are **statistical associations** between the pre-EVM and post-EVM eras.
- This analysis **does not** establish causality or constitute evidence of electoral fraud.
- Many confounding factors exist: constituency delimitation, population growth,
  expansion of voter rolls, changing competition levels, and economic factors.
- The RVM (Random Voting Model) is a null model assuming random vote allocation;
  systematic deviation from it indicates non-random structure, not manipulation.

---

## 5. Reproducibility

```
python src/pre_post_evm_analysis.py --runs 25 --dpi 600 --seed 42
```

**Python**: 3.13.2  
**NumPy**: 2.2.6  
**Pandas**: 2.3.3  
**SciPy**: 1.15.1

---
*Analysis performed using the project's existing RVM methodology.*
*No existing results were modified.*