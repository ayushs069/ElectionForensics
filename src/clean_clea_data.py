import os
import pandas as pd

# Define the columns to keep (lowercase as they appear in the data)
columns_to_keep = ['ctr_n', 'yr', 'cst_n', 'vv1', 'cv1', 'seat']

# Define countries to keep (≥ 400 constituencies)
countries_to_keep = [
    'Australia',
    'Bangladesh',
    'Belarus',
    'Canada',
    'Chile',
    'Denmark',
    'Ethiopia',
    'France',
    'Germany',
    'Ghana',
    'Hungary',
    'India',
    'Japan',
    'Kenya',
    'Lithuania',
    'Malawi',
    'Malaysia',
    'Myanmar',
    'New Zealand',
    'Nigeria',
    'Pakistan',
    'Papua New Guinea',
    'Philippines',
    'Solomon Islands',
    'Taiwan',
    'Tanzania',
    'Thailand',
    'Trinidad and Tobago',
    'Uganda',
    'UK',
    'Ukraine',
    'United States',
    'Zimbabwe'
]

def clean_clea_dataset(file_path):
    """
    Clean CLEA dataset according to specified rules
    """
    print(f"Processing {file_path}...")
    
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    print(f"Initial shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Keep only specified columns
    available_columns = [col for col in columns_to_keep if col in df.columns]
    if len(available_columns) < len(columns_to_keep):
        missing = set(columns_to_keep) - set(available_columns)
        print(f"Warning: Missing columns: {missing}")
    
    df = df[available_columns]
    print(f"After selecting columns: {df.shape}")
    
    # Remove rows where VV1 = -990 or VV1 = 0
    if 'vv1' in df.columns:
        df = df[~df['vv1'].isin([-990, 0])]
        print(f"After removing vv1 = -990 or 0: {df.shape}")
    
    # Remove rows where CV1 = -990
    if 'cv1' in df.columns:
        df = df[df['cv1'] != -990]
        print(f"After removing cv1 = -990: {df.shape}")
    
    # Keep only specified countries
    if 'ctr_n' in df.columns:
        df = df[df['ctr_n'].isin(countries_to_keep)]
        print(f"After filtering countries: {df.shape}")
    
    return df

# Process both files
print("="*80)
print("Processing file 1: clea_lc_20251015-A-K.xlsx")
print("="*80)
df1 = clean_clea_dataset('clea_lc_20251015-A-K.xlsx')

print("\n" + "="*80)
print("Processing file 2: clea_lc_20251015-L-Z.xlsx")
print("="*80)
df2 = clean_clea_dataset('clea_lc_20251015-L-Z.xlsx')

# Combine the datasets
print("\n" + "="*80)
print("Combining datasets...")
print("="*80)
df_combined = pd.concat([df1, df2], ignore_index=True)
print(f"Combined shape: {df_combined.shape}")

# Display summary statistics
print("\n" + "="*80)
print("Summary of cleaned dataset:")
print("="*80)
print(f"Total rows: {len(df_combined)}")
print(f"Columns: {df_combined.columns.tolist()}")
print(f"\nCountries included:")
if 'ctr_n' in df_combined.columns:
    country_counts = df_combined['ctr_n'].value_counts().sort_index()
    print(country_counts)

# Check for unique constituencies per country
if 'ctr_n' in df_combined.columns and 'cst_n' in df_combined.columns:
    print(f"\nUnique constituencies per country:")
    constituency_counts = df_combined.groupby('ctr_n')['cst_n'].nunique().sort_values(ascending=False)
    print(constituency_counts)

# Save the cleaned dataset
output_file = 'clea_cleaned_candidate_level.xlsx'
df_combined.to_excel(output_file, index=False)
print(f"\n✓ Cleaned dataset saved to: {output_file}")

# Also save as CSV for easier viewing
csv_file = 'clea_cleaned_candidate_level.csv'
df_combined.to_csv(csv_file, index=False)
print(f"✓ Also saved as CSV: {csv_file}")

print("\nFirst few rows of cleaned data:")
print(df_combined.head(10))
