import pandas as pd

# Load candidate-level data
df = pd.read_csv('clea_cleaned_candidate_level_filtered.csv')
print(f"Loaded {len(df)} candidate-level rows")

group_cols = ['ctr_n', 'yr', 'cst_n']

# Get winner votes: cv1 where seat == 1 (take max in case of ties)
winners = (
    df[df['seat'] == 1]
    .groupby(group_cols, as_index=False)['cv1']
    .max()
    .rename(columns={'cv1': 'winner_votes'})
)

# Get runner-up votes: highest cv1 among seat == 0
runners_up = (
    df[df['seat'] == 0]
    .groupby(group_cols, as_index=False)['cv1']
    .max()
    .rename(columns={'cv1': 'runner_up_votes'})
)

# Get vv1 per constituency (should be same for all candidates in a constituency)
vv1 = (
    df.groupby(group_cols, as_index=False)['vv1']
    .first()
)

# Merge all together
result = vv1.merge(winners, on=group_cols, how='left') \
             .merge(runners_up, on=group_cols, how='left')

# Compute margin and specific margin
result['margin'] = (result['winner_votes'] - result['runner_up_votes']).abs()
result['specific_margin'] = result['margin'] / result['vv1']

# Reorder columns
result = result[['ctr_n', 'yr', 'cst_n', 'vv1',
                 'winner_votes', 'runner_up_votes',
                 'margin', 'specific_margin']]

# Save
result.to_csv('constituency_level_results.csv', index=False)

print(f"\nConstituency-level results: {len(result)} rows")
print(f"Saved to: constituency_level_results.csv")
print(f"\nSample output:")
print(result.head(10).to_string(index=False))
print(f"\nSummary stats for specific_margin:")
print(result['specific_margin'].describe())
