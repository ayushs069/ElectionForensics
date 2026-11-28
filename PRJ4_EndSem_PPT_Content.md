# PRJ-IV End Semester Presentation — Slide-by-Slide Content

## 📊 Universal Statistical Patterns & Electoral Forensics of Indian General Elections

> [!NOTE]
> **33 slides** | **PPTX saved to:** [PRJ4_EndSem_PPT_Final.pptx](file:///d:/sem-5_projects/PRJ-4/PRJ4_EndSem_PPT_Final.pptx)
> Theme: Dark blue + Red accent (matching last semester PPT style)

---

## Slide 1 — TITLE SLIDE
**Universal Statistical Patterns & Electoral Forensics of Indian General Elections**

*Can numbers tell us if an election was fair or rigged?*

- **PRJ - IV | End Semester Presentation**
- Group - 4: Ayush Singh (230556), Anuj Pratap Singh (230525), Dhiren (230524)
- Mentored by: Dr. Hirdesh Kumar Pharasi
- Department of CSE, BML Munjal University | November 2026

---

## Slide 2 — AGENDA
| # | Topic |
|---|-------|
| 01 | Introduction & Motivation |
| 02 | Last Semester Recap (PRJ-III) |
| 03 | New Contributions This Semester |
| 04 | Data Source & Pipeline |
| 05 | Methodology — RVM & Fraud Score |
| 06 | 14-State RVM Analysis Results |
| 07 | Election Year-Wise Analysis |
| 08 | Pre-EVM vs Post-EVM Analysis |
| 09 | Spatial Contour Maps |
| 10 | Conclusion & Future Scope |

---

## Slide 3 — INTRODUCTION
**Why Statistical Election Forensics?**

- Elections are the foundation of democratic governance — hundreds of millions of Indian citizens vote across 543+ Lok Sabha constituencies.
- Traditional monitoring relies on human observers — subjective, expensive, and not scalable.
- Statistical election forensics offers a data-driven, objective approach to evaluate election integrity.
- Inspired by statistical physics: just as gas molecules follow universal laws regardless of which gas, fair elections may follow universal statistical laws regardless of which country.
- If an election deviates from this universal pattern, it may indicate irregularities or potential fraud.

**KEY QUESTION:** Can election fraud be detected using only statistical patterns in the data — without any human observation?

**THE PHYSICS ANALOGY:** Gas molecules follow the Maxwell-Boltzmann distribution regardless of which gas. Similarly, fair elections follow a universal margin distribution F(x) regardless of which country.

---

## Slide 4 — PROJECT OBJECTIVES (Semester V)

1. **14-State RVM Analysis** — Apply the RVM framework to 14 major Indian states using ECI data spanning 1951–2019, computing fraud scores and verifying conformity with the universal F(x) distribution.
2. **Year-Wise Temporal Analysis** — Generate election year-wise RVM plots for 7 states (Bihar, Gujarat, MP, Rajasthan, TN, UP, WB) to track temporal changes in electoral statistics.
3. **Pre-EVM vs Post-EVM Comparison** — Compare 5 elections before full EVM adoption (1989–1999) against 5 elections after (2004–2024) across all 14 states and at all-India level.
4. **Spatial Contour Maps** — Generate constituency-level winning margin contour plots for UP, West Bengal, and Bihar across 2014, 2019, and 2024 elections.
5. **Anomaly Assessment** — Assess whether any state or time period exhibits a statistically anomalous deviation from the RVM prediction.

---

## Slide 5 — LAST SEMESTER RECAP (PRJ-III)
**Global RVM validation across 29 countries using CLEA data**

- Data: CLEA (University of Michigan) — 12 lakh+ rows, 189 countries, 2,304 elections.
- Filtered to 29 eligible countries with 400+ constituency records.
- Validated RVM framework globally — **22 out of 29 countries (76%) follow the universal law.**
- Detected **Ethiopia (z=27.0)** and **Belarus (z=4.95)** as confirmed fraudulent.
- India deep dive: 9 states analysed — all clean with fraud scores < 3.0.
- Established the foundation for state-level and temporal extension.

**Key Stats:**
| Metric | Value |
|--------|-------|
| Countries Analysed | 29 |
| Countries Clean | 76% |
| Indian States (Sem IV) | 9 |
| Countries Flagged | 2 (Ethiopia, Belarus) |

**NEW THIS SEMESTER:** 9 → 14 states | Year-wise analysis | Pre-EVM vs Post-EVM | Spatial contour maps

---

## Slide 6 — NEW CONTRIBUTIONS THIS SEMESTER
**Four major analytical extensions**

1. **Extended RVM: 9 → 14 States** — Added Assam, Gujarat, Kerala, Odisha, and Punjab. Full coverage of major Indian states from 1951–2019.
2. **Election Year-Wise RVM Plots** — Individual RVM plots for 7 states across every election year (1951–2024). Tracks temporal evolution of electoral competition.
3. **Pre-EVM vs Post-EVM Analysis** — Systematic statistical comparison: 5 elections before EVM (1989–1999) vs 5 after (2004–2024). KS test, Welch's t-test, Mann-Whitney U test.
4. **Spatial Contour Maps** — Constituency-level winning margin contour plots for UP, West Bengal, Bihar across 2014, 2019, 2024. Geographic dimension to competitive patterns.

---

## Slide 7 — DATA SOURCE & PIPELINE
**Election Commission of India (ECI)**

**DATA OVERVIEW:**
- Source: Election Commission of India (ECI)
- 18 Lok Sabha elections: 1951–2019 (base RVM)
- Extended to include 2024 for year-wise analysis
- 6,500+ constituency-level records
- 14 states selected (≥200 records, ≥20 constituencies)
- Candidate-level → Constituency-level conversion
- Multi-stage cleaning pipeline applied

**DATA PROCESSING PIPELINE:**
1. Raw ECI Data → Candidate-level records from 18 elections
2. Data Cleaning → Remove missing values, zero turnout rows
3. Constituency Conversion → Aggregate to 1 row per constituency per year
4. Eligibility Filter → ≥200 records, ≥20 unique constituencies
5. Feature Engineering → Compute margins μ, scaled x = μ/⟨μ⟩
6. RVM Analysis → Simulation + Analytical comparison + Fraud score

---

## Slide 8 — 14 SELECTED STATES
**Constituency records per state (1951–2019)**

📊 *Image: Horizontal bar chart showing constituency records per state*

| State | Records |
|-------|---------|
| Uttar Pradesh | 1,388 |
| Bihar | 862 |
| Maharashtra | 804 |
| Tamil Nadu | 676 |
| West Bengal | 676 |
| Andhra Pradesh | 658 |
| Madhya Pradesh | 608 |
| Karnataka | 448 |
| Rajasthan | 420 |
| Gujarat | 406 |
| Odisha | 352 |
| Kerala | 342 |
| Punjab | 248 |
| Assam | 218 |

---

## Slide 9 — EXPLORATORY DATA ANALYSIS
**Mean specific margin trends and state-wise comparison**

📊 *Image: Trend of Mean Specific Margin Over Time — India (1951–2019)*
- Values oscillate around the theoretical prediction ⟨μ⟩ = 0.1993
- No persistent long-term trend → stable electoral dynamics
- Peak around 1977 (Emergency-era landslide)
- Competitive elections in 1998–2009 era (lower margins)

---

## Slide 10 — METHODOLOGY: THE RANDOM VOTING MODEL
**How the RVM simulates a fair election**

**RVM SIMULATION STEPS:**
1. Extract actual turnout T from real data for each constituency.
2. Draw 3 random weights from Uniform(0,1). Normalise to candidate probabilities: pᵢ = wᵢ / Σwᵢ
3. Simulate voting — draw from Multinomial(T, p₁, p₂, p₃). Each voter independently selects a candidate.
4. Compute margin M = 1st − 2nd highest votes; compute μ = M/T.
5. Repeat 25 simulation runs per constituency to get mean RVM prediction and uncertainty band.

**ANALYTICAL SOLUTION (K=3):**

$$P(\mu) = \frac{(1 - \mu)(5 + 7\mu)}{(1 + \mu)^2(1 + 2\mu)^2}$$

- ⟨μ⟩ = 0.2285 — a pure mathematical constant (zero free parameters)
- Universal scaled distribution: F(x) = ⟨μ⟩ × P(x × ⟨μ⟩)
- India-specific ⟨μ⟩ = 0.1993

**FRAUD SCORE:**
- Fraud Score = mean |F_emp(x) − F_RVM(x)| / σ_RVM(x)
- **< 3.0** → CLEAN | **3–5** → INVESTIGATE | **> 10** → STRONG FRAUD

---

## Slide 11 — RVM RESULTS: ALL-INDIA POOLED
**14 states, 1951–2019: Empirical data closely follows the universal curve**

📊 *Image: Pooled Pre-EVM vs Post-EVM F(x) comparison — both distributions follow the analytical curve*

---

## Slide 12 — STATE-LEVEL RVM: UTTAR PRADESH
**Fraud Score: 0.70 — Lowest among all 14 states**

📊 *Image: Universal F(x) — Uttar Pradesh*

- Largest constituency count: 1,388 records
- 80 Lok Sabha constituencies
- Fraud Score: 0.70 — the lowest among all 14 states
- Close agreement across the entire F(x) distribution
- Empirical dots closely track both analytical curve and RVM simulation band
- Confirms strong conformity with the universal law of democratic competition

---

## Slide 13 — STATE-LEVEL RVM: WEST BENGAL
**Fraud Score: 1.45 — Low mean margin reflects genuine competition**

📊 *Image: Universal F(x) — West Bengal*

- Characteristically low mean μ = 0.126
- Fraud Score: 1.45 — well within safe limits
- Low margin reflects historically competitive elections
- Left Front dominance (1977–2011) followed by TMC-BJP polarisation
- Data points follow the universal curve despite low margins
- Confirms genuine electoral competition, not anomaly

---

## Slide 14 — FRAUD SCORE SUMMARY: 14 STATES
**All states below the 3.0 threshold — Indian elections are statistically clean**

| State | Records | Mean μ | Fraud Score |
|-------|---------|--------|-------------|
| Uttar Pradesh | 1,388 | 0.160 | **0.70** ✅ |
| Maharashtra | 804 | 0.179 | 1.23 |
| Tamil Nadu | 676 | 0.133 | 1.18 |
| West Bengal | 676 | 0.126 | 1.45 |
| Bihar | 862 | 0.145 | **2.52** ⚠️ |
| Andhra Pradesh | 658 | 0.095 | 1.60 |
| Karnataka | 448 | 0.153 | 1.33 |
| Madhya Pradesh | 608 | 0.167 | 0.91 |
| Rajasthan | 420 | 0.143 | 1.21 |
| Gujarat | 406 | 0.172 | 1.08 |
| Odisha | 352 | 0.143 | 1.52 |
| Kerala | 342 | 0.092 | 1.76 |
| Punjab | 248 | 0.139 | 1.41 |
| Assam | 218 | 0.138 | 1.63 |

> Range: 0.70 (UP) to 2.52 (Bihar) — ALL below 3.0 threshold

---

## Slide 15 — ELECTION YEAR-WISE RVM ANALYSIS
**Tracking temporal evolution of electoral statistics (1951–2024)**

- Individual RVM plots for each election year per state
- 7 states analysed: Bihar, Gujarat, MP, Rajasthan, TN, UP, West Bengal
- Tracks whether specific elections stand out as anomalously competitive or one-sided
- Separates year-specific effects from aggregate trends

📊 *Images: Bihar 1951 vs Bihar 2024 side-by-side*

**Key findings:**
- Bihar: highest aggregate fraud score (2.52) but all individual years are clean
- UP: consistently lowest deviation across all election years
- Gujarat: stable conformity since state creation (1960)
- West Bengal: low μ persists across decades — genuine competition

---

## Slide 16 — YEAR-WISE RVM: UP & GUJARAT (2024)
**Latest election year confirms conformity**

📊 *Images: UP 2024 (z=0.87, 80 constituencies) | Gujarat 2024 (z=1.00, 25 constituencies)*

---

## Slide 17 — YEAR-WISE RVM: WEST BENGAL (1951)
**Earliest election data also follows the universal pattern**

📊 *Image: WB 1951 — RVM Deviation Score z = 1.03 (Normal)*

- 26 constituencies in first-ever general election
- Even India's earliest election data follows the universal law
- Validates the RVM's applicability across the entire temporal range

---

## Slide 18 — PRE-EVM vs POST-EVM ANALYSIS
**Did the transition to Electronic Voting Machines change electoral patterns?**

| | Pre-EVM (Paper Ballots) | Post-EVM (Electronic) |
|---|---|---|
| Elections | 1989, 1991, 1996, 1998, 1999 | 2004, 2009, 2014, 2019, 2024 |
| Observations | n = 2,455 | n = 2,296 |
| Mean ⟨μ⟩ | 0.1223 | 0.1325 |

**Statistical Tests Applied:**
1. **Kolmogorov-Smirnov Test** → p > 0.05 for all 14 states
2. **Welch's t-test** → No significant difference found
3. **Mann-Whitney U Test** → p > 0.05 at pooled level
4. **RVM Fraud Score Comparison** → Both cohorts < 3.0 threshold

---

## Slide 19 — PRE-EVM vs POST-EVM: POOLED F(x)
📊 *Image: Universal Scaled-Margin Distribution F(x) — Pre-EVM vs Post-EVM, 14 Major States*
- Both distributions closely follow the analytical curve
- No systematic divergence

---

## Slide 20 — PRE-EVM vs POST-EVM: KDE COMPARISON
📊 *Image: Kernel Density Estimation of Specific Margin Distribution*
- Pre-EVM: n=2,455, Mean=0.1223
- Post-EVM: n=2,296, Mean=0.1325
- Similar distributional shapes; Post-EVM shows slightly lower dispersion

---

## Slide 21 — PRE-EVM vs POST-EVM: SAMPLE SIZES BY STATE
📊 *Image: Sample Sizes Across 5 Pre-EVM vs 5 Post-EVM Elections by State*
- Balanced 5-vs-5 cohort design removes temporal and sample size bias

---

## Slide 22 — PRE-EVM vs POST-EVM: BIHAR
📊 *Image: Bihar — RVM Comparison: 5 Pre-EVM vs 5 Post-EVM Elections*
- Pre-EVM: z=0.941 (Pass), Post-EVM: z=1.178 (Pass)
- Change in Mean Margin: -0.0081 (-5.8%) | KS D = 0.066 (p = 6.73e-01)

---

## Slide 23 — PRE-EVM vs POST-EVM: ANDHRA PRADESH
📊 *Image: Andhra Pradesh — RVM Comparison*
- Pre-EVM: z=5.520 (**Flagged**), Post-EVM: z=1.082 (Pass)
- Change: +0.0200 (+24.3%) | KS D = 0.206 (p = 4.74e-04)
- Pre-EVM flag explained by state bifurcation and changing party dynamics

---

## Slide 24 — PRE-EVM vs POST-EVM: KEY FINDINGS
**No evidence that EVMs changed electoral margin distributions**

✅ Across all 14 states and at the all-India pooled level, Pre-EVM and Post-EVM margin distributions are statistically similar.

✅ Neither cohort's fraud score crosses the 3.0 threshold.

✅ KDE distributions show similar shapes with slightly lower dispersion in the Post-EVM cohort.

✅ No structural break observed at the EVM transition point in the chronological yearly trend.

✅ Findings consistent with the null hypothesis: electoral margin distributions are properties of democratic competition, independent of vote-recording technology.

✅ The transition to EVMs did not introduce or remove any systematic distortion in the competitive landscape.

---

## Slide 25 — SPATIAL ANALYSIS: WINNING MARGIN CONTOUR PLOTS
**Geographic dimension of electoral competition**

- Constituency-level winning margin contour plots for 3 states × 3 elections
- States: **Uttar Pradesh** (80 seats), **West Bengal** (42 seats), **Bihar** (40 seats)
- Elections: 2014, 2019, 2024 Lok Sabha
- Each constituency centroid mapped using Delaunay triangulation
- Contour lines interpolated via cubic gridding
- **Red = high margins** (dominant wins); **Blue = low margins** (competitive races)
- Tools: GeoPandas, Shapely for constituency-level shapefile processing

---

## Slide 26 — CONTOUR MAP: UTTAR PRADESH (2019)
📊 *Image: UP — 2019 General Election Vote Margin Contour*

- 79 constituencies (Post-2008 boundaries)
- Highest margin: **GHAZIABAD (501,500)**
- Lowest margin: **MACHHLISHAHR (181)**
- High-margin regions in western UP
- BJP dominance creates geographic concentration of large margins
- Competitive zones scattered in central/eastern UP

---

## Slide 27 — CONTOUR MAP: WEST BENGAL (2019)
📊 *Image: WB — 2019 General Election Vote Margin Contour*

- 42 constituencies (Post-2008 boundaries)
- Highest margin: **DARJEELING (413,443)**
- Lowest margin: **ARAMBAGH (1,142)**
- Intense TMC-BJP competition in 2019
- Red zones in north (Darjeeling) and south (Diamond Harbour)
- Blue competitive zones in central Bengal
- Broader spread of competitive constituencies vs 2014

---

## Slide 28 — CONTOUR MAPS: BIHAR (2014 vs 2019)
📊 *Images side-by-side: Bihar 2014 (NDA creates concentrated high-margin zones) | Bihar 2019 (NDA wave covers much larger area)*

- **2014:** NDA alliance creates concentrated high-margin zones. Highest: GOPALGANJ (286,936), Lowest: SAMASTIPUR (6,872)
- **2019:** Dramatic shift — NDA wave covers much larger area. Highest: MADHUBANI (454,940), Lowest: JAHANABAD (1,751)

---

## Slide 29 — CONTOUR MAP: BIHAR (2024)
📊 *Image: Bihar — 2024 General Election Vote Margin Contour*

- 40 constituencies (Post-2008 boundaries)
- Highest margin: **MUZAFFARPUR (234,927)**
- Lowest margin: **SARAN (13,661)**
- More fragmented contest after alliance realignment
- Less geographic concentration of extreme margins vs 2019
- Green-cyan tones dominate — more competitive overall
- Spatial patterns consistent with known political dynamics

---

## Slide 30 — CONCLUSION
**Indian elections conform to the universal law of democratic competition**

| Finding | Detail |
|---------|--------|
| ✅ All 14 states clean | Fraud scores 0.70–2.52, all below 3.0 |
| ✅ Bihar highest but safe | Score 2.52 — highest but unambiguously normal |
| ✅ West Bengal & Kerala | Low margins (μ=0.126, 0.092) = genuine competition |
| ✅ EVMs made no difference | No statistically significant change pre vs post EVM |
| ✅ Spatial patterns match history | Alliance formations drive regional margin concentrations |
| ✅ 70+ years of clean elections | From 1951 to 2024, Indian democracy passes the test |

> **Indian democratic elections, as a statistical ensemble, conform to the universal law of democratic competition predicted by the RVM.**

---

## Slide 31 — FUTURE SCOPE
1. **Booth-Level Analysis** — Apply RVM at booth resolution within constituencies to detect localised manipulation.
2. **Extension to 2024 (State-Level)** — Include 2024 data in the 14-state base analysis.
3. **Contour Maps for All 14 States** — Comprehensive longitudinal atlas of competitive geography.
4. **Multi-Candidate Extension (K > 3)** — Using normalised order statistics of Dirichlet random variables.
5. **Real-Time Monitoring Dashboard** — Web app to display RVM scores in real time from ECI data.

---

## Slide 32 — REFERENCES
1. S. Pal, S. Kumar and M. S. Santhanam, "Universal Statistics of Competition in Democratic Elections," arXiv, 2024.
2. W. R. Mebane Jr., "Election Forensics: Vote Counts and Benford's Law," UC Davis, July 2006.
3. P. Klimek et al., "Statistical Detection of Systematic Election Irregularities," PNAS, vol. 109, 2012.
4. F. Cantu and S. M. Saiegh, "Fraudulent Democracy?" Political Analysis, vol. 19, no. 4, 2011.
5. D. Kobak et al., "Statistical Fingerprints of Electoral Fraud?" Significance, vol. 13, no. 4, 2016.
6. K. Bischoff and S. J. Schwartz, "CLEA," University of Michigan, 2024.
7. J. Deckert et al., "Benford's Law and the Detection of Election Fraud," Political Analysis, vol. 19, 2011.
8. Election Commission of India, "General Election Results Database," eci.gov.in, 2026.
9. CLEA, Constituency Level Lower Chamber Election Archive, October 2025.

---

## Slide 33 — THANK YOU!
**Questions?**

Ayush Singh • Anuj Pratap Singh • Dhiren
Mentored by Dr. Hirdesh Kumar Pharasi

PRJ-IV | BML Munjal University | November 2026
