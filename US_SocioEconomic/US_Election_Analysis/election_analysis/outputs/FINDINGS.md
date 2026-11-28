# US 2020 County Election — Socioeconomic Analysis
## Key Findings Report

---

## Dataset Overview
- **Source:** US 2020 Presidential Election + ACS Socioeconomic Data, County Level
- **Coverage:** 3,141 US counties (2 dropped: Loving County TX pop=64, 1 invalid entry)
- **Variables used:** Vote shares, turnout proxy, income, education, density, Gini, race/ethnicity, occupation

---

## H1.1 — Income / Wealth → Turnout & Vote Choice

| Finding | Value |
|---|---|
| Pearson r (Log Income → Dem Margin) | **+0.221** *** |
| Pearson r (Gini Index → Dem Margin) | **+0.246** *** |
| Direction | Higher income → more Democratic lean |
| Inequality | Higher Gini → more Democratic (urban/diverse counties) |

**Nuance:** The positive income-Dem relationship is **non-linear** and driven by urban high-income counties (tech hubs, coastal metros). Rural high-income counties still vote Republican. Gini's positive sign reflects that high-inequality counties are often urban minorities + rich professionals, a Democratic coalition.

---

## H1.2 — Education → Vote Choice

| Finding | Value |
|---|---|
| Pearson r (Higher Education % → Dem Margin) | **+0.525** *** |
| Pearson r (Low Education % → Dem Margin) | **-0.121** *** |
| Highest bivariate predictor in education block | Higher Ed % |

**Key result:** Education is the **single strongest demographic predictor** of Democratic vote share. Counties in the top quintile of higher education average **+24.3 pp** more Democratic than bottom quintile. This aligns with the post-2016 "diploma divide" literature.

---

## H1.3 — Urbanization & Density → Vote

| Finding | Value |
|---|---|
| Pearson r (Log Density → Dem Margin) | **+0.510** *** |
| Q1 Rural counties — mean Dem Margin | **-56.4 pp** |
| Q4 Urban counties — mean Dem Margin | **+12.1 pp** |
| Urban/Rural gap | **~68 pp** |

**Urbanization is the second-strongest predictor.** The rural-urban electoral divide is the dominant spatial feature of US elections.

---

## H1.3 — Race / Diversity

| Variable | r (→ Dem Margin) |
|---|---|
| White % | **-0.544** *** (strongest negative predictor) |
| Black % | **+0.441** *** |
| Diversity Index | **+0.452** *** |
| Hispanic % | **+0.141** *** |

**White % is the strongest single bivariate predictor of Dem margin** (negative). Counties with high Black population share strongly favour Democrats. Hispanic counties show a weak positive lean but with high variance (Cuban-American vs Mexican-American community differences).

---

## H1 — Occupation Structure

| Occupation | r → Dem Margin | r → Turnout |
|---|---|---|
| Mgmt/Prof/Science/Arts | +0.355 *** | +0.196 *** |
| Service | +0.177 *** | -0.146 *** |
| Resources & Construction | -0.465 *** | -0.148 *** |
| Transportation | -0.305 *** | -0.088 *** |
| Sales & Office | +0.072 *** | +0.015 (ns) |

**Resource/Construction counties vote strongly Republican.** Knowledge-economy (Mgmt/Prof) counties vote Democratic. Turnout is highest in knowledge-economy counties and lowest in service-heavy counties.

---

## Multi-Variable Regression Results

### OLS → Democrat Margin
- **R² = 0.718** (all 11 features, standardised)
- **5-fold CV R² = 0.668**
- Model explains ~72% of county-level partisan variation from socioeconomic vars alone

**Top positive predictors (standardised coef):**
1. Higher Education %
2. Log Population Density
3. Diversity Index
4. Black %

**Top negative predictors:**
1. White %
2. Resources/Construction %
3. Low Education %

### OLS → Turnout
- **R² = 0.492**, CV R² = 0.450
- Socioeconomic vars explain ~49% of turnout variation

### Logistic → Democrat Win (binary)
- **CV Accuracy = 0.907** (91% of counties correctly classified as Dem/Rep win)
- Baseline (all Republican): ~74% accuracy — model adds **+17 pp** lift

---

## Turnout Findings

| Variable | r → Turnout |
|---|---|
| Log Median Income | +0.362 *** |
| Higher Education % | +0.396 *** |
| Log Pop Density | +0.143 *** |
| Diversity Index | -0.064 *** |

- **Richer, more educated counties vote at higher rates** — consistent with resource model of turnout (Verba, Schlozman & Brady 1995)
- Turnout proxy median = 0.50 (votes/population, including children/non-citizens — not comparable to VAP turnout)

---

## Caveats & Limitations

1. **Turnout proxy** = votes / total population (not voting-age population). Overestimates turnout suppression in child-heavy / non-citizen-heavy counties.
2. **Ecological fallacy:** County-level correlations do not imply individual-level behaviour.
3. **Census 2011 data:** Some demographic variables may not perfectly reflect 2020 population (ACS 5-year estimates used — current to ~2019).
4. **Confounding:** Education and income are correlated (r=0.65); race and urbanisation are correlated. Multicollinearity inflates SE in OLS but doesn't bias coefficients severely here.
5. **No causal identification:** These are observational associations. Education → vote choice is likely partially mediated by urbanisation and occupation.

---

## Files Generated

| File | Contents |
|---|---|
| `outputs/clean.csv` | Cleaned dataset with derived variables |
| `outputs/bivariate_dem_margin.csv` | All bivariate correlations → Dem margin |
| `outputs/bivariate_turnout.csv` | All bivariate correlations → turnout |
| `outputs/ols_coefficients_margin.csv` | Multiple OLS standardised coefficients |
| `outputs/ols_coefficients_turnout.csv` | Multiple OLS → turnout |
| `outputs/logistic_coefficients.csv` | Logistic log-odds → Dem win |
| `outputs/model_summary.csv` | R², accuracy metrics |
| `plots/fig1_*` | Outcome distributions |
| `plots/fig2_*` | Turnout distribution |
| `plots/fig3_*` | Correlation heatmap |
| `plots/fig4_*` | Income & Gini vs margin |
| `plots/fig5_*` | Education vs margin |
| `plots/fig6_*` | Urbanisation vs margin |
| `plots/fig7_*` | Race vs margin |
| `plots/fig8_*` | Occupation correlations |
| `plots/fig9_*` | Turnout vs socioeconomic |
| `plots/fig10_*` | Regression coefficients |
| `plots/fig11_*` | Actual vs predicted |
| `plots/fig12_*` | Quintile analysis |

---

*Analysis: US 2020 Presidential Election, County Level | Methods: Pearson correlation, OLS multiple regression, Logistic regression, 5-fold cross-validation*
