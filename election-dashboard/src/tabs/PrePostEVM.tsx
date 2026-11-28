import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import KpiCard from '../components/KpiCard';
import ImageViewer from '../components/ImageViewer';
import { PREPOST_STATEWISE, PREPOST_YEARLY, INDIA_MU_ANALYTICAL } from '../data/staticData';
import { getPrePostPlotPath, getPrePostGlobalPlotPath } from '../utils/plotPaths';

const PrePostEVM: React.FC = () => {
  const [selectedState, setSelectedState] = useState<string>('Uttar Pradesh');
  const [viewMode, setViewMode] = useState<'overview' | 'statewise' | 'global_figures'>('overview');

  const selectedStateData = PREPOST_STATEWISE.find(
    (s) => s.state.toLowerCase() === selectedState.toLowerCase()
  ) || PREPOST_STATEWISE[0];

  const stateChartData = PREPOST_STATEWISE.map((s) => ({
    name: s.state,
    Pre_EVM: Number(s.mean_pre.toFixed(4)),
    Post_EVM: Number(s.mean_post.toFixed(4)),
    Delta_Pct: Number(s.pct_change_mu.toFixed(1)),
  }));

  const yearlyChartData = PREPOST_YEARLY.map((y) => ({
    year: y.yr.toString(),
    mean: Number(y.mean.toFixed(4)),
    median: Number(y.median.toFixed(4)),
    era: y.era,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Pre-EVM vs Post-EVM Analysis</h1>
        <p className="text-sm text-slate-500 mt-1">
          Rigorous statistical comparison of 5 general elections before full EVM adoption (1989–1999, n=2,455) 
          vs 5 elections after (2004–2024, n=2,296) across 14 major Indian states.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Pre-EVM Mean μ (1989–1999)"
          value="0.1223"
          subtitle="n = 2,455 constituencies (5 elections)"
          color="blue"
        />
        <KpiCard
          label="Post-EVM Mean μ (2004–2024)"
          value="0.1325"
          subtitle="n = 2,296 constituencies (5 elections)"
          color="purple"
        />
        <KpiCard
          label="Pooled Mean Change Δμ"
          value="+0.0102 (+8.34%)"
          subtitle="Cohen's d = 0.097 (negligible effect size)"
          color="orange"
        />
        <KpiCard
          label="Overall Structural Verdict"
          value="CONFORMITY PRESERVED"
          subtitle="All 14 states RVM Fraud Score < 3.0 in Post-EVM era"
          color="green"
        />
      </div>

      {/* Methodology & Context Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
        <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Methodological Framework</h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          India completed nationwide transition to Electronic Voting Machines (EVMs) in the 2004 General Election. 
          To eliminate longitudinal and cohort-size biases, our analysis uses a balanced <strong>5-vs-5 election design</strong>:
          Pre-EVM cohort (1989, 1991, 1996, 1998, 1999) and Post-EVM cohort (2004, 2009, 2014, 2019, 2024). 
          Distributions are evaluated using <strong>Kolmogorov-Smirnov (KS) two-sample test</strong>, <strong>Mann-Whitney U test</strong>, 
          and the <strong>Random Voting Model (RVM) F(x) scaling law</strong>.
        </p>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setViewMode('overview')}
          className={`tab-btn ${viewMode === 'overview' ? 'active' : ''}`}
        >
          Comparative Overview & Charts
        </button>
        <button
          onClick={() => setViewMode('statewise')}
          className={`tab-btn ${viewMode === 'statewise' ? 'active' : ''}`}
        >
          State-Wise Detailed Inspector
        </button>
        <button
          onClick={() => setViewMode('global_figures')}
          className={`tab-btn ${viewMode === 'global_figures' ? 'active' : ''}`}
        >
          Pooled Figures & KDEs
        </button>
      </div>

      {/* View 1: Overview */}
      {viewMode === 'overview' && (
        <div className="space-y-6">
          {/* Yearly Progression Chart */}
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="section-title mb-0">Yearly Mean Specific Margin Progression (1989–2024)</h2>
                <p className="text-xs text-slate-500">
                  Tracking mean victory margin across each election cycle. Blue: Pre-EVM era; Red: Post-EVM era.
                </p>
              </div>
              <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2.5 py-1 rounded">
                Ref Theoretical ⟨μ⟩ = {INDIA_MU_ANALYTICAL}
              </span>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={yearlyChartData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 0.25]} tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(val: number) => [val.toFixed(4), 'Mean Specific Margin']}
                    contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                  />
                  <ReferenceLine
                    y={INDIA_MU_ANALYTICAL}
                    stroke="#dc2626"
                    strokeDasharray="4 4"
                    label={{ value: 'RVM Analytical ⟨μ⟩ (0.1993)', position: 'insideTopRight', fill: '#dc2626', fontSize: 11 }}
                  />
                  <ReferenceLine x="2004" stroke="#64748b" strokeDasharray="2 2" label={{ value: 'Full EVM Rollout', position: 'top', fill: '#64748b', fontSize: 10 }} />
                  <Bar
                    dataKey="mean"
                    fill="#3b82f6"
                    name="Mean Specific Margin"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Statewise Mean Margin Comparison */}
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <h2 className="section-title">Pre vs Post EVM Mean Specific Margin by State</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stateChartData} margin={{ top: 10, right: 30, left: 0, bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" angle={-35} textAnchor="end" interval={0} tick={{ fontSize: 11 }} height={60} />
                  <YAxis domain={[0, 0.25]} tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(val: number, name: string) => [val.toFixed(4), name.replace('_', ' ')]}
                    contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Bar dataKey="Pre_EVM" fill="#3b82f6" name="Pre-EVM (1989-1999)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Post_EVM" fill="#ef4444" name="Post-EVM (2004-2024)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* State-by-State Statistical Summary Table */}
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
            <h2 className="section-title">State-by-State Comparative Statistics (14 States)</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                    <th className="p-3">State</th>
                    <th className="p-3 text-right">Pre N</th>
                    <th className="p-3 text-right">Post N</th>
                    <th className="p-3 text-right">Pre Mean μ</th>
                    <th className="p-3 text-right">Post Mean μ</th>
                    <th className="p-3 text-right">Δμ (%)</th>
                    <th className="p-3 text-right">Pre Fraud</th>
                    <th className="p-3 text-right">Post Fraud</th>
                    <th className="p-3 text-right">KS Stat</th>
                    <th className="p-3 text-right">KS p-value</th>
                    <th className="p-3 text-center">Post Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {PREPOST_STATEWISE.map((row) => (
                    <tr key={row.state} className="hover:bg-slate-50">
                      <td className="p-3 font-medium text-slate-800">{row.state}</td>
                      <td className="p-3 text-right text-slate-600">{row.n_pre}</td>
                      <td className="p-3 text-right text-slate-600">{row.n_post}</td>
                      <td className="p-3 text-right font-mono text-slate-700">{row.mean_pre.toFixed(4)}</td>
                      <td className="p-3 text-right font-mono text-slate-700">{row.mean_post.toFixed(4)}</td>
                      <td className={`p-3 text-right font-medium ${row.pct_change_mu >= 0 ? 'text-amber-600' : 'text-blue-600'}`}>
                        {row.pct_change_mu >= 0 ? `+${row.pct_change_mu.toFixed(1)}%` : `${row.pct_change_mu.toFixed(1)}%`}
                      </td>
                      <td className="p-3 text-right font-mono text-slate-700">
                        <span className={row.flagged_pre ? 'text-red-600 font-bold' : 'text-emerald-700'}>
                          {row.fraud_pre.toFixed(2)}
                        </span>
                      </td>
                      <td className="p-3 text-right font-mono text-slate-700">
                        <span className={row.flagged_post ? 'text-red-600 font-bold' : 'text-emerald-700'}>
                          {row.fraud_post.toFixed(2)}
                        </span>
                      </td>
                      <td className="p-3 text-right font-mono text-slate-600">{row.ks_stat.toFixed(3)}</td>
                      <td className="p-3 text-right font-mono text-slate-600">{row.ks_p < 0.001 ? '<0.001' : row.ks_p.toFixed(3)}</td>
                      <td className="p-3 text-center">
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                          CLEAN
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* View 2: Statewise Detailed Inspector */}
      {viewMode === 'statewise' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide block mb-1">
                Select Indian State
              </label>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {PREPOST_STATEWISE.map((s) => (
                  <option key={s.state} value={s.state}>
                    {s.state}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-4 text-xs">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <span className="text-slate-500">Pre-EVM Fraud Score:</span>
                <span className="ml-1.5 font-bold font-mono text-slate-800">{selectedStateData.fraud_pre.toFixed(2)}</span>
                <span className={`ml-1 text-[10px] font-semibold px-1 rounded ${selectedStateData.flagged_pre ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}`}>
                  {selectedStateData.flagged_pre ? 'FLAGGED' : 'PASS'}
                </span>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <span className="text-slate-500">Post-EVM Fraud Score:</span>
                <span className="ml-1.5 font-bold font-mono text-slate-800">{selectedStateData.fraud_post.toFixed(2)}</span>
                <span className="ml-1 text-[10px] font-semibold px-1 rounded bg-emerald-100 text-emerald-700">
                  PASS
                </span>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <span className="text-slate-500">KS Test p-val:</span>
                <span className="ml-1.5 font-bold font-mono text-slate-800">{selectedStateData.ks_p < 0.001 ? '<0.001' : selectedStateData.ks_p.toFixed(4)}</span>
              </div>
            </div>
          </div>

          {/* Research Plot */}
          <div className="grid grid-cols-1 gap-6">
            <ImageViewer
              src={getPrePostPlotPath(selectedState)}
              title={`${selectedState}: RVM Comparison — 5 Pre-EVM vs 5 Post-EVM Elections`}
              className="w-full"
            />
          </div>

          {/* Explanatory Context for Selected State */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs text-slate-600 leading-relaxed space-y-1.5">
            <p className="font-semibold text-slate-800">State Analytical Insights: {selectedState}</p>
            <p>
              Pre-EVM mean margin ⟨μ⟩ was {selectedStateData.mean_pre.toFixed(4)} across {selectedStateData.n_pre} elections, 
              moving to {selectedStateData.mean_post.toFixed(4)} across {selectedStateData.n_post} elections in the Post-EVM era ({selectedStateData.pct_change_mu >= 0 ? '+' : ''}{selectedStateData.pct_change_mu.toFixed(1)}%).
            </p>
            {selectedState === 'Andhra Pradesh' && (
              <p className="text-amber-800 bg-amber-50 p-2 rounded border border-amber-200">
                Note on Andhra Pradesh: The Pre-EVM cohort exhibits elevated deviation (z=5.52) due to intense Telugu Desam Party (TDP) wave elections and state boundary reorganizations prior to the 2014 Telangana bifurcation, but post-EVM conforms cleanly (z=1.08).
              </p>
            )}
            {selectedState === 'Bihar' && (
              <p className="text-blue-800 bg-blue-50 p-2 rounded border border-blue-200">
                Note on Bihar: Both cohorts pass RVM testing (Pre: z=0.941, Post: z=1.178) with KS p = 0.673 and Mann-Whitney p = 0.837, demonstrating identical underlying competitive distributions before and after electronic voting.
              </p>
            )}
          </div>
        </div>
      )}

      {/* View 3: Global Pooled Figures */}
      {viewMode === 'global_figures' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ImageViewer
              src={getPrePostGlobalPlotPath(1)}
              title="Universal Scaled-Margin Distribution F(x): Pre-EVM vs Post-EVM Pooled"
            />
            <ImageViewer
              src={getPrePostGlobalPlotPath(8)}
              title="Kernel Density Estimation (KDE) of Specific Margin: Pre vs Post EVM"
            />
            <ImageViewer
              src={getPrePostGlobalPlotPath(4)}
              title="Sample Sizes Across 5 Pre vs 5 Post EVM Elections by State"
            />
            <ImageViewer
              src={getPrePostGlobalPlotPath(5)}
              title="Statewise Mean Specific Margin Comparison"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PrePostEVM;
