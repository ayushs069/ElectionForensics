import React, { useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts';
import { WORLD_FRAUD_DATA } from '../data/staticData';
import KpiCard from '../components/KpiCard';
import PlotGrid from '../components/PlotGrid';
import ImageViewer from '../components/ImageViewer';
import { getWorldPlotPath } from '../utils/plotPaths';
import { AlertTriangle, Info } from 'lucide-react';

const WORLD_COUNTRIES = WORLD_FRAUD_DATA.map((d) => d.country);

const WorldResearch: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState<string>('India');

  const totalCountries = WORLD_FRAUD_DATA.length;
  const flaggedCount = WORLD_FRAUD_DATA.filter((d) => d.flagged).length;
  const cleanCount = totalCountries - flaggedCount;
  const cleanPct = Math.round((cleanCount / totalCountries) * 100);
  const avgCleanFraud =
    WORLD_FRAUD_DATA.filter((d) => !d.flagged).reduce((s, d) => s + d.fraud_score, 0) /
    cleanCount;

  const chartData = [...WORLD_FRAUD_DATA].sort((a, b) => a.fraud_score - b.fraud_score);

  const globalPlots = [
    { src: '/plots/world/fraud_barchart.png', title: 'Fraud Score Bar Chart – All 29 Countries' },
    { src: '/plots/world/pooled/fig2_universal_Fx_pooled.png', title: 'Pooled Universal F(x) Distribution' },
    { src: '/plots/comparative/Q04_world_vs_india_Fx_overlay.png', title: 'India vs World F(x) Overlay' },
    { src: '/plots/comparative/Q07_combined_fraud_ranking.png', title: 'Combined Fraud Score Ranking' },
  ];

  const countryPlots = [1, 2, 3].map((fig) => ({
    src: getWorldPlotPath(selectedCountry, fig as 1 | 2 | 3),
    title:
      fig === 1
        ? `${selectedCountry} – Scaled Margin Distribution`
        : fig === 2
        ? `${selectedCountry} – Universal F(x) Fit`
        : `${selectedCountry} – Fraud Score Check`,
  }));

  const selectedData = WORLD_FRAUD_DATA.find((d) => d.country === selectedCountry);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="section-title">World Research Overview</h2>
        <p className="text-sm text-slate-500 mb-6">
          Global empirical validation of the Random Voting Model across 29 democracies using the CLEA dataset.
        </p>

        {/* KPI Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <KpiCard label="Countries Analysed" value={totalCountries} subtitle="CLEA lower-chamber dataset" color="blue" />
          <KpiCard label="Countries Clean" value={`${cleanPct}%`} subtitle={`${cleanCount} of ${totalCountries} conform`} color="green" />
          <KpiCard label="Countries Flagged" value={flaggedCount} subtitle="Fraud Score ≥ 3.0" color="red" />
          <KpiCard label="Avg Fraud (Clean)" value={avgCleanFraud.toFixed(2)} subtitle="Well within normal range" color="orange" />
        </div>
      </div>

      {/* Bar Chart */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <h3 className="font-semibold text-slate-700 mb-1 text-sm">Fraud Score by Country</h3>
        <p className="text-xs text-slate-400 mb-4">
          Red bars indicate a Fraud Score ≥ 3.0 (statistically significant deviation). Green bars indicate conformance.
        </p>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 90 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              dataKey="country"
              angle={-45}
              textAnchor="end"
              tick={{ fontSize: 10, fill: '#64748b' }}
              interval={0}
            />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
            <Tooltip
              formatter={(val: number) => [val.toFixed(2), 'Fraud Score']}
              contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
            />
            <ReferenceLine
              y={3}
              stroke="#ef4444"
              strokeDasharray="6 3"
              label={{ value: 'Threshold (3.0)', position: 'right', fontSize: 10, fill: '#ef4444' }}
            />
            <Bar dataKey="fraud_score" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, idx) => (
                <Cell key={idx} fill={entry.flagged ? '#ef4444' : '#22c55e'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Table */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-semibold text-slate-700 text-sm">Country Summary Table</h3>
          <span className="text-xs text-slate-400">{totalCountries} records</span>
        </div>
        <div className="overflow-x-auto max-h-80">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 sticky top-0 border-b border-slate-100">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Country</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Constituencies</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Mean μ</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Fraud Score</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {chartData.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2.5 font-medium text-slate-800">{row.country}</td>
                  <td className="px-4 py-2.5 text-right text-slate-600">{row.n_units.toLocaleString()}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-slate-700">{row.mean_mu.toFixed(3)}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-slate-700">{row.fraud_score.toFixed(2)}</td>
                  <td className="px-4 py-2.5">
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

      {/* Global Plots */}
      <div>
        <h3 className="font-semibold text-slate-700 mb-3 text-sm">Global Distribution Plots</h3>
        <PlotGrid images={globalPlots} columns={2} />
      </div>

      {/* Per-Country Inspector */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <div className="flex flex-wrap items-center gap-4 mb-5">
          <h3 className="font-semibold text-slate-700 text-sm">Per-Country Distribution Inspector</h3>
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            {WORLD_COUNTRIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          {selectedData && (
            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span>Mean μ: <strong className="text-slate-700">{selectedData.mean_mu.toFixed(3)}</strong></span>
              <span>Fraud Score: <strong className="text-slate-700">{selectedData.fraud_score.toFixed(2)}</strong></span>
              <span className={`px-2 py-0.5 rounded-full font-medium ${selectedData.flagged ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                {selectedData.flagged ? 'Flagged' : 'Clean'}
              </span>
            </div>
          )}
        </div>
        <PlotGrid images={countryPlots} columns={3} />
      </div>

      {/* Flagged Explanations */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <h3 className="font-semibold text-slate-700 mb-3 text-sm">Flagged Countries – Forensic Context</h3>
        <div className="space-y-3 text-xs text-slate-600">
          <div className="p-3 bg-red-50 rounded-lg border border-red-100">
            <strong className="text-red-700">Ethiopia (Fraud Score: 27.0):</strong> Mean μ = 0.811. Extremely high score indicates an election outcome impossible under fair democratic competition. Confirmed fraudulent by EU, AU, and Carter Center observer missions.
          </div>
          <div className="p-3 bg-red-50 rounded-lg border border-red-100">
            <strong className="text-red-700">Belarus (Fraud Score: 4.95):</strong> Lukashenko era (2004–2019). OSCE refused to validate elections. Systematic conversion of competitive races into artificial landslides.
          </div>
          <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
            <strong className="text-amber-700">UK (4.03) &amp; USA (4.08):</strong> Flagged due to institutional structural factors (permanent safe seats, two-party gerrymandering in the US, first-past-the-post distortion in the UK) rather than fraud.
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4">
        <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-amber-800">
          <strong>Disclaimer:</strong> Statistical deviation from the RVM prediction does not constitute legal proof of fraud.
          Structural electoral system characteristics (such as safe seats, majoritarian distortions, or high incumbency advantage)
          can produce elevated deviation scores without electoral manipulation.
        </p>
      </div>
    </div>
  );
};

export default WorldResearch;
