import pandas as pd
import numpy as np
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "constituency_level_results.csv")

print("Loading data...")
df = pd.read_csv(CSV_PATH)

print("Computing scaled_margin and scaled_specific_margin...")
# Calculate mean margin and specific margin per country
country_means = df.groupby('ctr_n')[['margin', 'specific_margin']].mean()

# Map the means back to the original dataframe
df['mean_margin_country'] = df['ctr_n'].map(country_means['margin'])
df['mean_specific_margin_country'] = df['ctr_n'].map(country_means['specific_margin'])

# Compute the scaled columns
# Avoid division by zero just in case
df['scaled_margin'] = np.where(df['mean_margin_country'] != 0, 
                               df['margin'] / df['mean_margin_country'], 
                               np.nan)
                               
df['scaled_specific_margin'] = np.where(df['mean_specific_margin_country'] != 0, 
                                        df['specific_margin'] / df['mean_specific_margin_country'], 
                                        np.nan)

# Drop the temporary mean columns
df = df.drop(columns=['mean_margin_country', 'mean_specific_margin_country'])

print("Saving updated dataset...")
df.to_csv(CSV_PATH, index=False)
print("Done!")
