"""
01_clean.py — Data Cleaning & Feature Engineering
US 2020 County Election + Socioeconomic Dataset
"""

import pandas as pd
import numpy as np

RAW = "/mnt/user-data/uploads/US_Election_dataset_v1.csv"
OUT = "/home/claude/election_analysis/outputs/clean.csv"

# ── Load ────────────────────────────────────────────────────────────────────
df = pd.read_csv(RAW, index_col=0)
print(f"Raw shape: {df.shape}")

# ── Fix percent cols (stored as "1.70%") ────────────────────────────────────
pct_cols = [
    "Population with less than 9th grade education",
    "Population with 9th to 12th grade education, no diploma",
    "High School graduate and equivalent",
    "Some College,No Degree",
    "Associates Degree",
    "Bachelors Degree",
    "Graduate or professional degree",
]
for c in pct_cols:
    df[c] = df[c].str.replace("%", "", regex=False).astype(float)

# ── Fix income cols — handle dash (Loving County TX, pop=64, no ACS data) ──
for c in ["Median income (dollars)", "Mean income (dollars)"]:
    df[c] = (df[c]
             .str.replace(",", "", regex=False)
             .str.strip()
             .replace("-", np.nan)
             .astype(float))

# Drop Loving County (pop=64, no median income, statistical outlier)
drop_mask = df["Total Population"] < 100
print(f"Dropping {drop_mask.sum()} counties with pop < 100 (Loving County TX)")
df = df[~drop_mask].copy()

# ── Derived variables ────────────────────────────────────────────────────────
df["total_votes"] = (
    df["2020 Democrat vote raw"] +
    df["2020 Republican vote raw"] +
    df["2020 other vote raw"]
)
df["turnout_proxy"] = df["total_votes"] / df["Total Population"]

df["dem_win"] = (df["2020 Democrat vote %"] > df["2020 Republican vote %"]).astype(int)
df["dem_margin"] = df["2020 Democrat vote %"] - df["2020 Republican vote %"]

df["higher_ed"] = df["Bachelors Degree"] + df["Graduate or professional degree"]
df["low_ed"] = (
    df["Population with less than 9th grade education"] +
    df["Population with 9th to 12th grade education, no diploma"]
)

race_cols = [
    "NH-White percentage", "NH-Black percentage",
    "NH-American Indian and Alaska Native percentage", "NH-Asian percentage",
    "NH-Native Hawaiian and Other Pacific Islander percentage",
    "NH-Some Other Race percentage", "NH-Two or More Races percentage",
    "Hispanic or Latino percentage",
]
race_pcts = df[race_cols] / 100
df["diversity_idx"] = 1 - (race_pcts ** 2).sum(axis=1)

df["log_density"] = np.log1p(df["Density per square km"])
df["log_median_income"] = np.log(df["Median income (dollars)"])

# Sanity filter on turnout
before = len(df)
df = df[(df["turnout_proxy"] > 0.01) & (df["turnout_proxy"] <= 1.5)]
print(f"Dropped {before - len(df)} rows with bad turnout proxy. Final: {len(df)}")

print(df[["dem_margin","higher_ed","log_median_income","turnout_proxy","diversity_idx"]].describe())
df.to_csv(OUT, index=True)
print(f"Saved → {OUT}")
