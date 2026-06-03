# Election Analysis Project (RVM)

This project performs analysis on election data from India and around the world, focusing on the distribution of voter margins and turnout. It uses a theoretical model (RVM) to predict "universal" competition patterns and identifies potential anomalies.

## Project Structure

- `src/`: Core Python scripts for analysis.
    - `rvm_analysis.py`: Main script for world-wide election data analysis.
    - `india_rvm_analysis.py`: Specialized script for India parliamentary election data.
    - `anomaly.py`: Utility for identifying data anomalies.
    - `clean_clea_data.py`: Data cleaning and filtering.
    - `aggregate_to_constituency.py`: Aggregates candidate-level data to constituency-level.
    - `convert_to_300dpi.py`: Utility to export plots in high resolution (300 dpi).
- `data/`:
    - `raw/`: Original datasets (CSV/XLSX).
    - `processed/`: Cleaned and ready-to-use datasets.
- `docs/`: Project reports, reference documents, and structure outlines.
- `outputs/`: 
    - `rvm_outputs/`: Plots and summaries for world data.
    - `rvm_outputs_india/`: Plots and summaries for India data.
    - `300dpi/`: High-resolution versions of all plots.

## Project Flow

1. **Data Preparation**:
   - Raw data from `data/raw/` is cleaned and aggregated using `src/clean_clea_data.py` and `src/aggregate_to_constituency.py`.
   - Resulting datasets are stored in `data/processed/`.
2. **Analysis**:
   - Run `src/rvm_analysis.py` for global data or `src/india_rvm_analysis.py` for India-specific data.
   - These scripts simulate the expected margin distribution and compare it with the actual data.
   - Outputs (plots and summaries) are generated in the `outputs/` folder.
3. **Detection**:
   - The analysis calculates a "Fraud Score" based on deviations from the expected model, flagging entities (countries or states) with significant anomalies.
4. **Export**:
   - Use `src/convert_to_300dpi.py` to generate high-quality plots for reports.

## Setup & Usage

### 1. Installation
Install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Running Analysis
To run the full global analysis:
```bash
python src/rvm_analysis.py --data data/processed/constituency_level_results.csv
```

To run India-specific analysis:
```bash
python src/india_rvm_analysis.py
```
