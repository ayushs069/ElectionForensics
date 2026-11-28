export const INDIA_STATES_KEYS: Record<string, string> = {
  'Bihar': 'BIHAR',
  'Tamil Nadu': 'TAMIL_NADU',
  'West Bengal': 'WEST_BENGAL',
  'Andhra Pradesh': 'ANDHRA_PRADESH',
  'Madhya Pradesh': 'MADHYA_PRADESH',
  'Maharashtra': 'MAHARASHTRA',
  'Gujarat': 'GUJARAT',
  'Rajasthan': 'RAJASTHAN',
  'Odisha': 'ODISHA',
  'Kerala': 'KERALA',
  'Karnataka': 'KARNATAKA',
  'Punjab': 'PUNJAB',
  'Assam': 'ASSAM',
  'Uttar Pradesh': 'UTTAR_PRADESH',
};

export const getWorldPlotPath = (country: string, figNum: 1 | 2 | 3): string => {
  const countryKey = country.replace(/ /g, '_');
  const figName = figNum === 1 ? 'scaled_margin' : figNum === 2 ? 'universal_Fx' : 'fraud_check';
  return `/plots/world/per_country/${countryKey}_fig${figNum}_${figName}.png`;
};

export const getIndiaPerStatePlotPath = (state: string, figNum: 1 | 2 | 3): string => {
  const stateKey = INDIA_STATES_KEYS[state] ?? state.toUpperCase().replace(/ /g, '_');
  const figName = figNum === 1 ? 'scaled_margin' : figNum === 2 ? 'universal_Fx' : 'fraud_check';
  return `/plots/india/per_state/${stateKey}_fig${figNum}_${figName}.png`;
};

export const getYearwisePlotPath = (state: string, year: number): string => {
  return `/plots/yearwise/${state}/${state}_${year}_rvm.png`;
};

export const getPrePostPlotPath = (state: string): string => {
  const normalized = state.toLowerCase().replace(/ /g, '_');
  return `/plots/prepost/statewise/${normalized}_pre_vs_post_rvm.png`;
};

export const getContourPlotPath = (state: string, year: number): string => {
  const stateMap: Record<string, string> = {
    'Uttar Pradesh': 'UP',
    'Bihar': 'BIHAR',
    'West Bengal': 'WB',
  };
  const folder = stateMap[state] || state;
  const statePrefix = state.replace(/ /g, '_');
  return `/plots/contour/Last3_Elections/${folder}/${statePrefix}_${year}_contour.png`;
};

export const getIndiapooledPlotPath = (figNum: 1 | 2 | 3 | 4): string => {
  const names = ['scaled_margin_pooled', 'universal_Fx_pooled', 'fraud_check_pooled', 'all_states_Fx_overlay'];
  return `/plots/india/pooled/fig${figNum}_${names[figNum - 1]}.png`;
};

export const getPrePostGlobalPlotPath = (figNum: number): string => {
  const figMap: Record<number, string> = {
    1: 'fig01_pooled_Fx_pre_vs_post',
    2: 'fig02_pooled_scaled_margin',
    3: 'fig03_mean_margin_comparison',
    4: 'fig04_sample_sizes',
    5: 'fig05_statewise_mean_margin',
    6: 'fig06_statewise_Fx_grid',
    7: 'fig07_fraud_score_comparison',
    8: 'fig08_mu_kde_pre_vs_post',
    9: 'fig09_yearly_trend',
    10: 'fig10_statewise_delta_margin',
    11: 'fig11_all_india_pooled_Fx',
    12: 'fig12_cumulative_distribution_Fx',
  };
  return `/plots/prepost/${figMap[figNum] || 'fig01_pooled_Fx_pre_vs_post'}.png`;
};
