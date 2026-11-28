# Electoral Forensics Research Dashboard

### Universal Statistical Patterns and Electoral Forensics of Indian General Elections
**BML Munjal University &bull; PRJ-IV Project**  
**Mentored by:** Dr. Hirdesh Kumar Pharasi  
**Submitted by:** Ayush Singh (230556), Anuj Pratap Singh (230525), Dhiren (230524)

---

## 🎯 Architecture & Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Backend:** Python FastAPI, Uvicorn, NumPy, SciPy (for real-time Random Voting Model simulations)
- **Data Integration:** 100% local research datasets from Election Commission of India (ECI) & CLEA (University of Michigan)
- **Visuals:** High-resolution 600 DPI research figures, GIS contour maps (Delaunay triangulation), interactive distributions, and live Monte Carlo simulation console.

---

## 🚀 Quick Start (Single Click)

Double-click `start_dashboard.bat` in the project root:
```bat
start_dashboard.bat
```
This automatically starts:
1. **Python FastAPI Backend** at `http://localhost:8000` (API Docs: `http://localhost:8000/docs`)
2. **React Vite Dashboard** at `http://localhost:3000`

### Manual Commands:
```bash
# Terminal 1: Backend
python start_backend.py

# Terminal 2: Frontend
cd election-dashboard
npm run dev
```

---

## 📑 Dashboard Tabs & Features

1. **World Research:**
   - 29 democracies analysed using CLEA candidate-level dataset.
   - Fraud Score ranking bar chart with $z = 3.0$ forensic threshold.
   - Per-country interactive inspector (scaled margin histogram, universal $F(x)$ fit, and fraud score check).
   - Forensic context distinguishing institutional distortions (US gerrymandering, UK safe seats) from verified fraud (Ethiopia $z=27.0$, Belarus $z=4.95$).

2. **Indian Results:**
   - Comprehensive RVM analysis across 14 major Indian states (1951–2019, 7,997 constituency records).
   - State-wise Fraud Score bar chart (all states $\le 2.522 < 3.0$, confirming democratic integrity).
   - Mean specific margin $\mu$ comparisons against theoretical $\langle\mu\rangle = 0.1993$.
   - Interactive per-state plot viewer and pooled 14-state figures.

3. **Indian Year-Wise RVM:**
   - Longitudinal tracking across 7 states (UP, Bihar, Gujarat, MP, Rajasthan, Tamil Nadu, West Bengal) from 1951 to 2024.
   - State & year interactive selectors displaying original research plots.
   - Time-series charts for mean $\mu$ and deviation scores $z$, highlighting historical outlier events (e.g., 1977 post-Emergency anti-incumbency wave).

4. **Pre-EVM vs Post-EVM Analysis:**
   - Symmetric 5-vs-5 cohort design: 1989–1999 ($n=2,455$) vs 2004–2024 ($n=2,296$).
   - Kolmogorov-Smirnov (KS) two-sample test, Mann-Whitney U test, and Welch's t-test tables.
   - State-by-state detailed inspector and yearly progression bar charts.
   - Proof of structural invariance: EVM rollout introduced no systematic distortion.

5. **Contour Plot Analysis:**
   - Spatial margin landscapes for Uttar Pradesh (80 seats), Bihar (40 seats), and West Bengal (42 seats).
   - Centroids mapped with Delaunay triangulation and Clough-Tocher 2D cubic splines.
   - Side-by-side longitudinal comparison across 2014, 2019, and 2024 general elections.
   - Interactive summary showing highest and lowest margin constituencies.

6. **RVM Model (Mathematical & Live Simulation):**
   - Closed-form analytical solution: $P(\mu) = \frac{(1-\mu)(5+7\mu)}{(1+\mu)^2(1+2\mu)^2}$ with $\langle\mu\rangle = 0.2285$.
   - Universal trajectory: $F(x) = \langle\mu\rangle \times P(x\langle\mu\rangle)$.
   - Live interactive Monte Carlo console connected to the FastAPI backend (with in-browser fallback).
   - 5-step simulation workflow and Maxwell-Boltzmann statistical physics analogy.

7. **Margin Measures & Scaling:**
   - Mathematical progression: Raw Margin ($M$) $\to$ Specific Margin ($\mu$) $\to$ Scaled Margin ($y$) $\to$ Scaled Specific Margin ($x$).
   - Interactive live margin calculator with custom vote inputs.
   - Real constituency case studies (Ghaziabad 501k blowout vs Machhlishahr 181-vote tie).

8. **Data Architecture & Pipelines:**
   - Interactive flowcharts for both CLEA Global Pipeline and ECI Indian Pipeline.
   - Stage-by-stage artifact inspector (inputs, outputs, sanitization criteria, and code references).
   - Complete audit counts and verification metrics.
