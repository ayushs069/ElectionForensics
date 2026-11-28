# CSES IMD Analysis — Key Findings
## H1 + H2 | 204,246 respondents | 54 countries | 1996–2016

---

## H1: Demographic/Socioeconomic Factors → Voter Turnout

### Logistic Regression CV Accuracy: 85.5%

| Variable | Direction | Finding |
|---|---|---|
| Age | ✅ Positive | Older people vote significantly more. Strongest individual predictor. |
| Education | ✅ Positive | Higher education → higher turnout consistently across all income levels |
| Income Quintile | ✅ Positive | Richer respondents vote more. Q5 vs Q1 gap ≈ 8–10pp |
| Employed | ✅ Positive | Employed people vote more than non-employed |
| Unemployed | ❌ Negative | Unemployed have lowest turnout — economic disengagement = political disengagement |
| Gender | ≈ Neutral | Minimal difference between male and female turnout in survey data |

### Key H1 Plots
- **Plot 1:** Gender/Education/Income side-by-side → education shows steepest gradient
- **Plot 2:** Age groups → clear monotonic rise: <25 votes least, 65+ votes most
- **Plot 3:** Employment → Retired highest turnout, Unemployed lowest
- **Plot 4:** Heatmap → education effect holds even at lowest income levels
- **Plot 5:** Correlation summary → age & education dominate
- **Plot 6:** Odds ratios → age OR highest, unemployed OR < 1.0 (reduces turnout)
- **Plot 7:** Country-level turnout → wide variation (social desirability bias note)

---

## H2: Economic Conditions → Electoral Outcomes
### Election-Level | 159 elections | 138 with incumbent data

| Variable | vs Turnout | vs Incumbent Support |
|---|---|---|
| GDP Growth (election year) | Weak positive | Positive (economic voting confirmed) |
| GDP Growth (previous year) | Weak positive | Positive (retrospective voting) |
| GDP per Capita | Positive | Positive |
| Unemployment Rate | Negative | Negative (punish incumbent) |
| Inflation (log) | Negative | Negative (punish incumbent) |

### Key H2 Findings
- **Economic voting confirmed:** Higher GDP growth → higher incumbent support (Plot 3)
- **Punishment effect:** High unemployment & inflation → lower incumbent support (Plots 3, 5)
- **Turnout:** Economic distress (high unemployment, inflation) weakly reduces turnout
- **Development:** Richer countries (higher GDP/capita) vote at higher rates (Plot 6)
- **Time trend:** Turnout relatively stable 1996–2016 despite GDP fluctuations (Plot 4)

### Caveat
- voted_incumbent is SURVEY self-report, not official vote share
- N=159 elections — correlations significant but small sample for macro analysis
- Inflation max=79.5% (Belarus/Turkey) — log transformation applied

---

## Model Performance
| Model | Metric | Value |
|---|---|---|
| H1 Logistic Regression | 5-fold CV Accuracy | 85.5% |
| H1 Baseline (all voted=1) | Accuracy | 85.4% |
| Note | Turnout=1 is 85% of sample — model near baseline | Check odds ratios not accuracy |

*Note: High base rate (85% voted=1 due to CSES overreport bias) means accuracy metric is misleading. Focus on odds ratios and correlations for interpretation.*

