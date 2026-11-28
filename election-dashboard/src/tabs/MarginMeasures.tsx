import React, { useState } from 'react';
import KpiCard from '../components/KpiCard';
import { INDIA_MU_ANALYTICAL } from '../data/staticData';

const MarginMeasures: React.FC = () => {
  // Interactive Calculator State
  const [winnerVotes, setWinnerVotes] = useState<number>(345000);
  const [runnerupVotes, setRunnerupVotes] = useState<number>(275000);
  const [totalTurnout, setTotalTurnout] = useState<number>(680000);

  const rawMargin = Math.max(0, winnerVotes - runnerupVotes);
  const specificMargin = totalTurnout > 0 ? rawMargin / totalTurnout : 0;
  const scaledSpecificMargin = specificMargin / INDIA_MU_ANALYTICAL;

  // Real representative constituency case studies
  const cases = [
    {
      constituency: 'Ghaziabad (UP, 2019)',
      winner: 'V.K. Singh (BJP)',
      total_votes: 1547347,
      win_votes: 944503,
      run_votes: 443003,
      raw_m: 501500,
      spec_m: 0.3241,
      scaled_x: 1.626,
      category: 'Extreme Landslide',
    },
    {
      constituency: 'Machhlishahr (UP, 2019)',
      winner: 'B.P. Saroj (BJP)',
      total_votes: 1045234,
      win_votes: 488397,
      run_votes: 488216,
      raw_m: 181,
      spec_m: 0.000173,
      scaled_x: 0.00087,
      category: 'Knife-Edge Tie',
    },
    {
      constituency: 'Darjeeling (WB, 2019)',
      winner: 'Raju Bista (BJP)',
      total_votes: 1289456,
      win_votes: 750067,
      run_votes: 336624,
      raw_m: 413443,
      spec_m: 0.3206,
      scaled_x: 1.609,
      category: 'Regional Blowout',
    },
    {
      constituency: 'Arambagh (WB, 2019)',
      winner: 'Aparupa Poddar (TMC)',
      total_votes: 1423450,
      win_votes: 649929,
      run_votes: 648787,
      raw_m: 1142,
      spec_m: 0.000802,
      scaled_x: 0.00402,
      category: 'Ultra Competitive',
    },
    {
      constituency: 'Gopalganj (Bihar, 2014)',
      winner: 'Janak Ram (BJP)',
      total_votes: 978456,
      win_votes: 478773,
      run_votes: 191837,
      raw_m: 286936,
      spec_m: 0.2933,
      scaled_x: 1.472,
      category: 'Wave Landslide',
    },
    {
      constituency: 'Samastipur (Bihar, 2014)',
      winner: 'Ram Chandra Paswan (LJP)',
      total_votes: 912345,
      win_votes: 270401,
      run_votes: 263529,
      raw_m: 6872,
      spec_m: 0.00753,
      scaled_x: 0.0378,
      category: 'Marginal Win',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Margin Measures & Scaling Formulation</h1>
        <p className="text-sm text-slate-500 mt-1">
          Mathematical progression from raw vote counts to the scale-invariant universal forensic variable x = μ / ⟨μ⟩.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Raw Margin (M)"
          value="V₁ − V₂"
          subtitle="Non-comparable across constituency sizes"
          color="blue"
        />
        <KpiCard
          label="Specific Margin (μ)"
          value="M / T"
          subtitle="Turnout-normalized percentage margin"
          color="purple"
        />
        <KpiCard
          label="Scaled Margin (y)"
          value="M / ⟨M⟩"
          subtitle="Normalized by ensemble raw average"
          color="orange"
        />
        <KpiCard
          label="Scaled Specific Margin (x)"
          value="μ / ⟨μ⟩"
          subtitle="Universal dimensionless invariant for F(x)"
          color="green"
        />
      </div>

      {/* 4 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Measure 1 */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-blue-600 tracking-wider">Measure 1: Absolute Count</span>
            <span className="text-xs font-mono bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-semibold">Dimension: Votes</span>
          </div>
          <h3 className="text-lg font-bold text-slate-800">Raw Margin (M)</h3>
          <div className="math-block">
            M = V_winner − V_runnerup
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Measures the raw vote surplus of the winning candidate over the second-place candidate. 
            While intuitive for local recounts, it cannot be compared across constituencies with unequal electorates 
            (e.g., Lakshadweep with ~50k voters vs Outer Delhi with ~3 million voters).
          </p>
        </div>

        {/* Measure 2 */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-purple-600 tracking-wider">Measure 2: Turnout Fraction</span>
            <span className="text-xs font-mono bg-purple-50 text-purple-700 px-2 py-0.5 rounded font-semibold">Dimensionless [0, 1]</span>
          </div>
          <h3 className="text-lg font-bold text-slate-800">Specific Margin (μ)</h3>
          <div className="math-block text-purple-300">
            μ = M / T = (V_winner − V_runnerup) / T_valid
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Divides raw margin by total valid votes cast (T). Expresses victory margin as a fraction of total vote turnout. 
            This standardizes local size differences, allowing equitable comparison of competitiveness between rural and megacity seats.
          </p>
        </div>

        {/* Measure 3 */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-orange-600 tracking-wider">Measure 3: Ensemble Normalized</span>
            <span className="text-xs font-mono bg-orange-50 text-orange-700 px-2 py-0.5 rounded font-semibold">Relative Scale</span>
          </div>
          <h3 className="text-lg font-bold text-slate-800">Scaled Margin</h3>
          <div className="math-block text-amber-300">
            y = M / ⟨M⟩
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Normalizes the raw margin by the national or state average raw margin ⟨M⟩ across all elections in that cohort. 
            Centers the distribution around unity (mean = 1.0), but remains vulnerable to demographic turnout growth over decades.
          </p>
        </div>

        {/* Measure 4 */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-emerald-600 tracking-wider">Measure 4: Universal Scaling Invariant</span>
            <span className="text-xs font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-semibold">Universal Coordinate</span>
          </div>
          <h3 className="text-lg font-bold text-slate-800">Scaled Specific Margin (x)</h3>
          <div className="math-block text-emerald-300">
            x = μ / ⟨μ⟩ , where ⟨μ⟩_India = 0.1993
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            The fundamental parameter of the Random Voting Model. By dividing specific margin by the theoretical or empirical ensemble mean ⟨μ⟩, 
            the resulting distribution F(x) becomes universal and collapse-invariant across countries, decades, and electorate sizes.
          </p>
        </div>
      </div>

      {/* Interactive Margin Calculator */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
        <h2 className="section-title mb-1">Interactive Margin Calculator</h2>
        <p className="text-xs text-slate-500">
          Enter candidate vote totals and total turnout to see real-time computation across all margin metrics.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="text-xs font-semibold text-slate-600 block mb-1">Winner Votes (V₁)</label>
            <input
              type="number"
              value={winnerVotes}
              onChange={(e) => setWinnerVotes(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-600 block mb-1">Runner-up Votes (V₂)</label>
            <input
              type="number"
              value={runnerupVotes}
              onChange={(e) => setRunnerupVotes(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-600 block mb-1">Total Turnout (T)</label>
            <input
              type="number"
              value={totalTurnout}
              onChange={(e) => setTotalTurnout(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-sm font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Real-time Computed Values */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs mt-3">
          <div>
            <span className="text-slate-500 font-medium block">Raw Margin M</span>
            <span className="font-mono font-bold text-slate-900 text-base">{rawMargin.toLocaleString()} votes</span>
          </div>
          <div>
            <span className="text-slate-500 font-medium block">Specific Margin μ</span>
            <span className="font-mono font-bold text-purple-700 text-base">
              {specificMargin.toFixed(4)} ({(specificMargin * 100).toFixed(2)}%)
            </span>
          </div>
          <div>
            <span className="text-slate-500 font-medium block">Scaled Specific Margin x</span>
            <span className="font-mono font-bold text-emerald-700 text-base">
              x = {scaledSpecificMargin.toFixed(4)}
            </span>
          </div>
        </div>
      </div>

      {/* Case Studies Table */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
        <h2 className="section-title mb-1">Empirical Demonstration: Indian Lok Sabha Case Studies</h2>
        <p className="text-xs text-slate-500">
          Comparing raw margin vs specific margin reveals how turnout scale distorts raw numbers without normalization.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <th className="p-3">Constituency & Year</th>
                <th className="p-3">Winner</th>
                <th className="p-3 text-right">Total Turnout</th>
                <th className="p-3 text-right">Raw Margin (M)</th>
                <th className="p-3 text-right">Specific Margin (μ)</th>
                <th className="p-3 text-right">Scaled Margin (x)</th>
                <th className="p-3 text-center">Category</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {cases.map((c) => (
                <tr key={c.constituency} className="hover:bg-slate-50">
                  <td className="p-3 font-medium text-slate-900">{c.constituency}</td>
                  <td className="p-3 text-slate-600">{c.winner}</td>
                  <td className="p-3 text-right font-mono text-slate-700">{c.total_votes.toLocaleString()}</td>
                  <td className="p-3 text-right font-mono font-semibold text-slate-800">{c.raw_m.toLocaleString()}</td>
                  <td className="p-3 text-right font-mono text-purple-700 font-medium">{c.spec_m.toFixed(4)}</td>
                  <td className="p-3 text-right font-mono text-emerald-700 font-bold">{c.scaled_x.toFixed(3)}</td>
                  <td className="p-3 text-center">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        c.scaled_x > 1.4
                          ? 'bg-amber-100 text-amber-800'
                          : c.scaled_x < 0.1
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {c.category}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MarginMeasures;
