import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts';
import { INDIA_SUMMARY, INDIA_MU_ANALYTICAL } from '../data/staticData';
import KpiCard from '../components/KpiCard';
import PlotGrid from '../components/PlotGrid';
import { getIndiaPerStatePlotPath, INDIA_STATES_KEYS } from '../utils/plotPaths';
import { Info, AlertTriangle } from 'lucide-react';

const IndianResults: React.FC = () => {
  const [selectedState, setSelectedState] = useState<string>('Bihar');

  const sortedByScore = [...INDIA_SUMMARY].sort((a, b) => b.fraud_score - a.fraud_score);
  const highestState = sortedByScore[0];
  const lowestState = sortedByScore[sortedByScore.length - 1];

  const stateKey = INDIA_STATES_KEYS[selectedState] ?? selectedState.toUpperCase().replace(/ /g, '_');

  const statePlots = [1, 2, 3].map((fig) => ({
    src: getIndiaPerStatePlotPath(stateKey, fig as 1 | 2 | 3),
    title:
      fig === 1
        ? `${selectedState} – Scaled Margin Histogram`
        : fig === 2
        ? `${selectedState} – Universal F(x) Fit`
        : `${selectedState} – Fraud Score Check`,
  }));

  const edaPlots = [
    { src: '/plots/india/eda/eda4_margin_dist.png', title: 'All-India Margin Distribution' },
    { src: '/plots/india/eda/eda6_mu_over_years.png', title: 'Mean μ Over Years (1951–2019)' },
    { src: '/plots/india/eda/eda1_records_per_state.png', title: 'Constituency Records Per State' },
    { src: '/plots/india/eda/eda9_margin_boxplot_by_state.png', title: 'State-wise Margin Boxplot' },
  ];

  const pooledPlots = [
    { src: '/plots/india/pooled/fig1_scaled_margin_pooled.png', title: 'Pooled Scaled Margin' },
    { src: '/plots/india/pooled/fig2_universal_Fx_pooled.png', title: 'Pooled Universal F(x)' },
    { src: '/plots/india/pooled/fig4_all_states_Fx_overlay.png', title: 'All States F(x) Overlay' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="section-title">Indian Electoral Results</h2>
        <p className="text-sm text-slate-500 mb-6">
          RVM analysis of 14 Indian states spanning general elections from 1951–2019 using ECI data.
        </p>

        {/* KPI Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <KpiCard label="States Analysed" value={14} subtitle="≥200 constituencies" color="blue" />
          <KpiCard label="All States Clean" value="✓ Clean" subtitle="Max score: 2.52 < 3.0" color="green" />
          <KpiCard label="Highest Score" value={`${highestState.state} (${highestState.fraud_score.toFixed(2)})`} subtitle="Most deviation" color="orange" />
          <KpiCard label="Lowest Score" value={`${lowestState.state} (${lowestState.fraud_score.toFixed(2)})`} subtitle="Best conformance" color="purple" />
        </div>
      </div>

      {/* Fraud Score Chart */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <h3 className="font-semibold text-slate-700 mb-1 text-sm">Fraud Score by State</h3>
        <p className="text-xs text-slate-400 mb-4">All states below the 3.0 threshold — no evidence of systematic fraud.</p>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={sortedByScore} margin={{ top: 10, right: 20, left: 10, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="state" angle={-45} textAnchor="end" tick={{ fontSize: 10, fill: '#64748b' }} interval={0} />
            <YAxis domain={[0, 4]} tick={{ fontSize: 11, fill: '#64748b' }} />
            <Tooltip
              formatter={(val: number) => [val.toFixed(3), 'Fraud Score']}
              contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
            />
            <ReferenceLine y={3} stroke="#ef4444" strokeDasharray="6 3" label={{ value: 'Threshold (3.0)', position: 'right', fontSize: 10, fill: '#ef4444' }} />
            <Bar dataKey="fraud_score" fill="#22c55e" radius={[4, 4, 0, 0]}>
              {sortedByScore.map((entry, idx) => (
                <Cell key={idx} fill={entry.fraud_score >= 3 ? '#ef4444' : '#22c55e'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Mean μ Chart */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <h3 className="font-semibold text-slate-700 mb-1 text-sm">Mean Specific Margin (μ) by State</h3>
        <p className="text-xs text-slate-400 mb-4">
          Dashed line = analytical RVM prediction (μ = {INDIA_MU_ANALYTICAL.toFixed(4)})
        </p>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={INDIA_SUMMARY} margin={{ top: 10, right: 20, left: 10, bottom: 80 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="state" angle={-45} textAnchor="end" tick={{ fontSize: 10, fill: '#64748b' }} interval={0} />
            <YAxis domain={[0, 0.35]} tick={{ fontSize: 11, fill: '#64748b' }} />
            <Tooltip
              formatter={(val: number) => [val.toFixed(4), 'Mean μ']}
              contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
            />
            <ReferenceLine y={INDIA_MU_ANALYTICAL} stroke="#3b82f6" strokeDasharray="6 3" label={{ value: `RVM μ = ${INDIA_MU_ANALYTICAL.toFixed(4)}`, position: 'right', fontSize: 10, fill: '#3b82f6' }} />
            <Bar dataKey="mean_mu" fill="#60a5fa" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Table */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-700 text-sm">State-wise Summary Table</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">State</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">N Records</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wide">Years</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Mean μ</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Fraud Score</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {sortedByScore.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-800">{row.state}</td>
                  <td className="px-4 py-3 text-right text-slate-600">{row.n_units.toLocaleString()}</td>
                  <td className="px-4 py-3 text-center text-slate-500 text-xs">{row.yr_min}–{row.yr_max}</td>
                  <td className="px-4 py-3 text-right font-mono text-slate-700">{row.mean_mu.toFixed(4)}</td>
                  <td className="px-4 py-3 text-right font-mono text-slate-700">{row.fraud_score.toFixed(3)}</td>
                  <td className="px-4 py-3">
                    {row.flagged ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                        <AlertTriangle className="w-3 h-3" /> Flagged
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                        ✓ Clean
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* EDA Plots */}
      <div>
        <h3 className="font-semibold text-slate-700 mb-3 text-sm">Exploratory Data Analysis (India 1951–2019)</h3>
        <PlotGrid images={edaPlots} columns={2} />
      </div>

      {/* Per-State Plots */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <div className="flex flex-wrap items-center gap-4 mb-5">
          <h3 className="font-semibold text-slate-700 text-sm">Per-State RVM Analysis</h3>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            {INDIA_SUMMARY.map((s) => (
              <option key={s.state} value={s.state}>{s.state}</option>
            ))}
          </select>
        </div>
        <PlotGrid images={statePlots} columns={3} />
      </div>

      {/* Pooled Plots */}
      <div>
        <h3 className="font-semibold text-slate-700 mb-3 text-sm">Pooled India Analysis</h3>
        <PlotGrid images={pooledPlots} columns={3} />
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4">
        <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-amber-800">
          <strong>Disclaimer:</strong> Statistical deviation ≠ evidence of electoral manipulation.
          All 14 Indian states analysed returned fraud scores below the 3.0 threshold, indicating no systematic
          statistical anomaly in Indian general election data as modelled by the RVM framework.
        </p>
      </div>
    </div>
  );
};

export default IndianResults;
