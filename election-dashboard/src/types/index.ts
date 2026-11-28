export interface IndiaSummaryRow {
  state: string;
  n_units: number;
  yr_min: number;
  yr_max: number;
  mean_T: number;
  mean_M: number;
  mean_mu: number;
  mu_analytical: number;
  fraud_score: number;
  flagged: boolean;
}

export interface WorldFraudRow {
  country: string;
  fraud_score: number;
  flagged: boolean;
  mean_mu: number;
  n_units: number;
}

export interface YearwiseRow {
  state: string;
  year: number;
  n_const: number;
  mean_mu: number;
  rvm_dev_z: number;
  flagged: boolean;
  plot_file: string;
}

export interface PrePostRow {
  state: string;
  n_pre: number;
  n_post: number;
  mean_pre: number;
  mean_post: number;
  delta_mu: number;
  pct_change_mu: number;
  fraud_pre: number;
  flagged_pre: boolean;
  fraud_post: number;
  flagged_post: boolean;
  ks_stat: number;
  ks_p: number;
  mw_p: number;
}

export interface ContourRow {
  state: string;
  year: number;
  n_matched: number;
  highest_cst: string;
  highest_margin: number;
  lowest_cst: string;
  lowest_margin: number;
  boundary: string;
}

export interface YearlyProgressionRow {
  yr: number;
  count: number;
  mean: number;
  median: number;
  std: number;
  sem: number;
  era: string;
}
