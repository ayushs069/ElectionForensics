# CSES IMD Cleaned Dataset (`cses_clean.csv`)

## Overview

This directory contains the cleaned and standardized dataset derived from the **Comparative Study of Electoral Systems (CSES) Integrated Module Dataset (IMD)** (`cses_imd.csv`). 

The cleaned dataset (`cses_clean.csv`) is specifically prepared for statistical and econometrics analysis of **individual-level voter turnout, socioeconomic demographics, and national macroeconomic indicators** across global democratic elections between **1996 and 2016**.

- **File Name:** `cses_clean.csv`
- **Dimensions:** **204,333 rows × 20 columns**
- **Original Source File:** `cses_imd.csv` (395,797 rows × 406 columns)
- **Rows Filtered / Dropped:** 191,464 rows (48.37%) due to missing core data or non-binary turnout records

---

## Dataset Structure & Data Dictionary

The cleaned dataset consists of **20 variables** organized into demographic, electoral, economic, and engineered helper categories:

| Column Name | Data Type | Description | Valid Values / Range | Missing % |
| :--- | :---: | :--- | :--- | :---: |
| `country` | `string` | Name of the election country | 54 unique countries | 0.00% |
| `election_year` | `int64` | Year of the national election | 1996 – 2016 | 0.00% |
| `age` | `float64` | Respondent age in years | 15 – 115 | 0.00% |
| `gender` | `float64` | Respondent gender | `1.0` = Male, `2.0` = Female, `3.0` = Other | 0.00% |
| `education` | `float64` | Highest level of education attained | `0.0` = None, `1.0` = Primary, `2.0` = Secondary, `3.0` = Post-Secondary, `4.0` = University, `6.0` = Other | 0.00% |
| `income_quintile` | `float64` | Household income quintile | `1.0` (Lowest) to `5.0` (Highest), `6.0` = Bottom/Top tier | 0.00% |
| `region` | `float64` | Regional sub-national numeric code | Regional numeric codes | 16.74% |
| `employment_status` | `float64` | Primary employment status | `0.0` – `5.0` (`0`–`4` Employed, `5` Unemployed, etc.) | 0.00% |
| `turnout` | `float64` | **Target Variable:** Reported voter turnout | `0.0` = Did not vote, `1.0` = Voted | 0.00% |
| `turnout_switcher` | `float64` | Turnout consistency across elections | `1.0` – `6.0` | 36.96% |
| `voted_incumbent` | `float64` | Voted for incumbent government party | `0.0` = Did not vote incumbent, `1.0` = Voted incumbent | **29.39%** |
| `gdp_growth_elec_year` | `float64` | Annual GDP growth rate (%) in election year | Real continuous % (e.g., `-8.50%` to `+10.43%`) | 0.00% |
| `gdp_growth_prev_year` | `float64` | Annual GDP growth rate (%) in year prior | Real continuous % | 0.00% |
| `gdp_per_capita` | `float64` | GDP per capita (PPP in USD) | Real continuous USD | 0.00% |
| `unemployment_rate` | `float64` | National unemployment rate (%) | Real continuous % (`0.70%` to `25.10%`) | 0.00% |
| `inflation_rate` | `float64` | Annual inflation rate (%) | Real continuous % (`-5.55%` to `+79.53%`) | 0.00% |
| `population` | `float64` | Total national population | Positive integers | 0.00% |
| `employed` | `float64` | **Helper Column:** Binary employment indicator | `1.0` = Employed (status 0–4), `0.0` = Otherwise | 0.00% |
| `unemployed` | `float64` | **Helper Column:** Binary unemployment indicator | `1.0` = Unemployed (status 5), `0.0` = Otherwise | 0.00% |
| `edu_label` | `string` | **Helper Column:** Descriptive education category | `"None"`, `"Primary"`, `"Secondary"`, `"Post-Secondary"`, `"University"`, `"Other"` | 0.00% |

---

## Data Cleaning Methodology

The transformation from `cses_imd.csv` to `cses_clean.csv` followed a standardized reproducible data processing pipeline:

### 1. Feature Selection
Out of 406 original columns, 19 core variables were extracted (`IMD1005` through `IMD5057_1`). The respondent identifier (`IMD1005`) and occupation ISCO codes were removed to streamline row-level analytical processing.

### 2. Missing Value Code Recoding
CSES uses numeric codes to indicate missing, refused, or non-applicable responses. These were recoded to standard IEEE floating-point `NaN`:
- **Demographics (`age`, `gender`, `education`, `income_quintile`, `employment_status`):** Recoded `7, 8, 9`, `97, 98, 99`, `9997, 9998, 9999` $\rightarrow$ `NaN`.
- **Electoral Behavior (`turnout`, `voted_incumbent`, `turnout_switcher`):** Recoded `9999993, 9999996, 9999997, 9999998, 9999999` $\rightarrow$ `NaN`. `turnout` filtered strictly to binary values (`0` and `1`).
- **Macroeconomic Indicators (`gdp_growth`, `unemployment_rate`, `inflation_rate`, `population`):** Recoded sentinel missing codes (`99.0`, `999.0`, `9999.0`, `999999.0`, `99999999`) $\rightarrow$ `NaN`.

### 3. Core Variable Filtering
Rows containing `NaN` in any of the **9 core analytical variables** (`turnout`, `age`, `gender`, `education`, `income_quintile`, `employment_status`, `gdp_growth_elec_year`, `unemployment_rate`, `inflation_rate`) were dropped. Non-core supplementary variables (`region`, `turnout_switcher`, `voted_incumbent`, `gdp_growth_prev_year`, `gdp_per_capita`, `population`) were preserved even if `NaN`.

### 4. Feature Engineering
Three helper variables were engineered:
- **`employed`**: `1.0` if `employment_status` $\in [0, 1, 2, 3, 4]$, else `0.0`.
- **`unemployed`**: `1.0` if `employment_status` == `5`, else `0.0`. *(Confirmed zero overlap between `employed` and `unemployed`)*.
- **`edu_label`**: Explicit categorical mapping for `education` values (`0` $\rightarrow$ `"None"`, `1` $\rightarrow$ `"Primary"`, `2` $\rightarrow$ `"Secondary"`, `3` $\rightarrow$ `"Post-Secondary"`, `4` $\rightarrow$ `"University"`, `6` $\rightarrow$ `"Other"`).

---

## Dataset Summary Statistics

### Turnout Distribution (`turnout`)
- **Voted (`1.0`):** 174,605 respondents (85.45%)
- **Did Not Vote (`0.0`):** 29,728 respondents (14.55%)

### Voted Incumbent Distribution (`voted_incumbent`)
- **Did Not Vote Incumbent (`0.0`):** 86,751 respondents (42.46%)
- **Voted Incumbent (`1.0`):** 57,518 respondents (28.15%)
- **Missing / Non-applicable (`NaN`):** 60,064 respondents (29.39%)

### Education Breakdown (`edu_label`)
- **Primary:** 63,011 (30.84%)
- **Secondary:** 59,090 (28.92%)
- **University:** 38,046 (18.62%)
- **Post-Secondary:** 32,113 (15.72%)
- **None:** 12,054 (5.90%)
- **Other:** 19 (0.01%)

### Geographical & Temporal Coverage
- **Countries Covered:** 54 Countries (including USA, Canada, Great Britain, Germany, France, Japan, Australia, Brazil, Mexico, South Africa, South Korea, etc.)
- **Election Year Span:** **1996 – 2016**

---

## Quick Start (Python Usage)

```python
import pandas as pd

# Load clean CSES dataset
df = pd.read_csv("cses_clean.csv")

print(f"Dataset Shape: {df.shape}")
print("\nSample Data:")
print(df[["country", "election_year", "age", "edu_label", "turnout", "voted_incumbent"]].head())

# Check Incumbent Voting Rate by Income Quintile (excluding NaNs)
incumbent_by_income = df.groupby("income_quintile")["voted_incumbent"].mean()
print("\nIncumbent Voting Rate by Income Quintile:")
print(incumbent_by_income)
```
