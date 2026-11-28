import React, { useState } from 'react';
import KpiCard from '../components/KpiCard';

interface PipelineStep {
  id: string;
  stageNum: string;
  title: string;
  input: string;
  output: string;
  description: string;
  formulaOrCode?: string;
}

const GLOBAL_STEPS: PipelineStep[] = [
  {
    id: 'g1',
    stageNum: '01',
    title: 'Data Collection & Extraction',
    input: 'CLEA Lower Chamber Archive (Univ. of Michigan)',
    output: '1,200,000+ candidate-level rows (189 countries)',
    description:
      'Merged candidate-level lower house parliamentary election archives across two master dataset tranches (A–K and L–Z). Contains raw candidate names, party allegiances, and recorded votes.',
    formulaOrCode: 'clea_lc_20251015-A-K.xlsx + clea_lc_20251015-L-Z.xlsx',
  },
  {
    id: 'g2',
    stageNum: '02',
    title: 'Data Cleaning & Sanitization',
    input: '1,200,000+ raw records',
    output: '585,000 cleaned candidate records',
    description:
      'Removal of invalid entries: purged CLEA sentinel error codes (-990: unspecified, -991: uncontested, -992: election suspended/invalid), zero turnout rows, and multi-member proportional non-plurality systems.',
    formulaOrCode: 'filter(vv1 > 0 & cv1 >= 0 & seat == 1)',
  },
  {
    id: 'g3',
    stageNum: '03',
    title: 'Eligibility & Robustness Filter',
    input: '189 national datasets',
    output: '29 eligible countries (107,368 constituency rows)',
    description:
      'Imposed rigorous threshold of ≥ 400 constituency-level election observations to guarantee asymptotic sample power for non-parametric distribution tests.',
    formulaOrCode: 'count(constituency_records) >= 400',
  },
  {
    id: 'g4',
    stageNum: '04',
    title: 'Constituency-Level Aggregation',
    input: 'Candidate-level rows',
    output: 'Single row per constituency per election year',
    description:
      'Sorted candidate votes per constituency to extract winner votes (V₁), runner-up votes (V₂), total valid votes (T), and third-place votes.',
    formulaOrCode: 'winner_votes = max(cv1), runner_up = second_max(cv1)',
  },
  {
    id: 'g5',
    stageNum: '05',
    title: 'Feature Engineering & Margin Metrics',
    input: 'Aggregated constituency records',
    output: 'M, μ, scaled margin, and scaled specific margin x',
    description:
      'Computed raw margin M = V₁ − V₂, specific margin μ = M / T, and scaled specific margin x = μ / ⟨μ⟩ for universal alignment.',
    formulaOrCode: 'M = V₁ - V₂;  μ = M / T;  x = μ / ⟨μ⟩',
  },
  {
    id: 'g6',
    stageNum: '06',
    title: 'RVM Simulation & Scoring',
    input: 'Actual turnout T per constituency',
    output: 'Fraud Score z and empirical F(x) vs analytical curve',
    description:
      'Simulated 25 Monte Carlo runs per constituency with Multinomial(T, p) where p ~ Uniform(0,1). Computed bin-normalized z-score deviation.',
    formulaOrCode: 'Fraud Score = mean(|F_emp(x) - F_rvm(x)| / σ_rvm(x))',
  },
];

const INDIA_STEPS: PipelineStep[] = [
  {
    id: 'i1',
    stageNum: '01',
    title: 'ECI Data Acquisition',
    input: 'Election Commission of India (ECI) Archives',
    output: '18 Lok Sabha Elections (1951–2019 + 2024)',
    description:
      'Official constituency-by-constituency election results spanning seven decades of democratic history since Independence.',
    formulaOrCode: 'ECI General Election Results Master Files (1951-2024)',
  },
  {
    id: 'i2',
    stageNum: '02',
    title: 'State Eligibility Threshold',
    input: '36 States and Union Territories',
    output: '14 Major States (7,997 constituency records)',
    description:
      'Filtered states with ≥ 200 records and ≥ 20 unique parliamentary constituencies to eliminate small island or territory sample noise.',
    formulaOrCode: 'records >= 200 & unique_cst >= 20',
  },
  {
    id: 'i3',
    stageNum: '03',
    title: 'Constituency Normalization',
    input: 'Candidate vote lists',
    output: 'Standardized constituency schema',
    description:
      'Harmonized historical spelling variations across 70 years, mapped boundary changes across delimitation commissions (1952, 1963, 1973, 2008).',
    formulaOrCode: 'data/processed/final_20const_14states.csv',
  },
  {
    id: 'i4',
    stageNum: '04',
    title: 'Multi-Branch Analytical Execution',
    input: 'Unified Indian constituency dataset',
    output: 'Four specialized research modules',
    description:
      'Divided dataset into: (A) 14-State baseline RVM analysis; (B) Year-wise temporal breakdown; (C) Balanced 5-vs-5 Pre vs Post EVM study; (D) Spatial GIS winning margin contour plots.',
    formulaOrCode: 'Parallel analytical execution pipeline in Python / SciPy',
  },
  {
    id: 'i5',
    stageNum: '05',
    title: 'Spatial GIS Triangulation',
    input: 'ECI tabular data + Survey of India Shapefiles',
    output: 'High-resolution winning-margin contour maps',
    description:
      'Constituency centroids mapped via Delaunay triangulation. Clough-Tocher 2D cubic spline interpolation within state boundaries for UP, Bihar, WB.',
    formulaOrCode: 'GeoPandas + Shapely + Scipy.spatial.Delaunay',
  },
  {
    id: 'i6',
    stageNum: '06',
    title: 'Forensic Synthesis & Verification',
    input: 'All analytical outputs',
    output: 'Final conclusions & academic report figures',
    description:
      'All 14 states confirmed clean with scores 0.70 to 2.52 (< 3.0 threshold). No technological disruption detected from EVM introduction.',
    formulaOrCode: 'Report verification & 600 DPI publication plots',
  },
];

const DataPipeline: React.FC = () => {
  const [activePipeline, setActivePipeline] = useState<'global' | 'india'>('india');
  const [selectedStep, setSelectedStep] = useState<PipelineStep>(INDIA_STEPS[0]);

  const steps = activePipeline === 'global' ? GLOBAL_STEPS : INDIA_STEPS;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Data Architecture & Processing Pipelines</h1>
        <p className="text-sm text-slate-500 mt-1">
          End-to-end data pipelines: from raw international election registries (CLEA) and ECI records 
          to normalized constituency tables, Monte Carlo simulations, and GIS contour plots.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Global Dataset (CLEA)"
          value="1.2M+ Rows"
          subtitle="29 Eligible Democracies Filtered"
          color="blue"
        />
        <KpiCard
          label="Indian Dataset (ECI)"
          value="7,997 Records"
          subtitle="14 Major States (1951–2019)"
          color="green"
        />
        <KpiCard
          label="Simulation Iterations"
          value="25 Runs / Const."
          subtitle="Multinomial voter allocation"
          color="purple"
        />
        <KpiCard
          label="GIS Delimitation Layers"
          value="Pre & Post 2008"
          subtitle="Shapefiles matched across decades"
          color="orange"
        />
      </div>

      {/* Pipeline Selector */}
      <div className="flex gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => {
            setActivePipeline('india');
            setSelectedStep(INDIA_STEPS[0]);
          }}
          className={`tab-btn ${activePipeline === 'india' ? 'active' : ''}`}
        >
          Indian Election Pipeline (ECI Data — 14 States)
        </button>
        <button
          onClick={() => {
            setActivePipeline('global');
            setSelectedStep(GLOBAL_STEPS[0]);
          }}
          className={`tab-btn ${activePipeline === 'global' ? 'active' : ''}`}
        >
          Global Election Pipeline (CLEA Data — 29 Countries)
        </button>
      </div>

      {/* Interactive Flowchart */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
        <h2 className="section-title mb-1">
          {activePipeline === 'india' ? 'Indian Pipeline Flow' : 'Global Pipeline Flow'} (Click any stage to inspect)
        </h2>
        <p className="text-xs text-slate-500">
          Step-by-step pipeline from data ingest to statistical forensic verdict.
        </p>

        {/* Flowchart Boxes */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
          {steps.map((s, idx) => {
            const isSelected = selectedStep.id === s.id;
            return (
              <div
                key={s.id}
                onClick={() => setSelectedStep(s)}
                className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-blue-50 border-blue-500 shadow-md ring-2 ring-blue-200'
                    : 'bg-slate-50 border-slate-200 hover:border-slate-300 hover:bg-white'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${isSelected ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-700'}`}>
                    STEP {s.stageNum}
                  </span>
                  {idx < steps.length - 1 && (
                    <span className="text-slate-300 text-xs hidden lg:inline">→</span>
                  )}
                </div>
                <h4 className="text-xs font-semibold text-slate-800 leading-tight mb-1">{s.title}</h4>
                <p className="text-[10px] text-slate-500 line-clamp-2">{s.input}</p>
              </div>
            );
          })}
        </div>

        {/* Selected Stage Inspector Drawer */}
        <div className="mt-4 p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-blue-600 text-white text-xs font-mono font-bold rounded">
                STAGE {selectedStep.stageNum}
              </span>
              <h3 className="text-sm font-bold text-slate-900">{selectedStep.title}</h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">ID: {selectedStep.id}</span>
          </div>

          <p className="text-xs text-slate-700 leading-relaxed">{selectedStep.description}</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-1">
            <div className="bg-white p-3 rounded-lg border border-slate-200">
              <span className="text-slate-400 font-semibold uppercase text-[10px] block mb-0.5">Input Artifact</span>
              <span className="font-mono text-slate-800 font-medium">{selectedStep.input}</span>
            </div>
            <div className="bg-white p-3 rounded-lg border border-slate-200">
              <span className="text-slate-400 font-semibold uppercase text-[10px] block mb-0.5">Output Artifact</span>
              <span className="font-mono text-emerald-700 font-medium">{selectedStep.output}</span>
            </div>
          </div>

          {selectedStep.formulaOrCode && (
            <div className="bg-slate-900 text-green-400 p-3 rounded-lg font-mono text-xs overflow-x-auto">
              <span className="text-slate-500 select-none">// Implementation reference: </span>
              {selectedStep.formulaOrCode}
            </div>
          )}
        </div>
      </div>

      {/* Data Ingestion Summary Table */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
        <h2 className="section-title mb-1">Data Ingestion & Integrity Metrics</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <th className="p-3">Analysis Cohort</th>
                <th className="p-3">Primary Source</th>
                <th className="p-3 text-right">Elections</th>
                <th className="p-3 text-right">Units / Rows</th>
                <th className="p-3">Key Filters Applied</th>
                <th className="p-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr className="hover:bg-slate-50">
                <td className="p-3 font-semibold text-slate-900">World 29 Democracies</td>
                <td className="p-3 text-slate-600">CLEA (Univ. of Michigan)</td>
                <td className="p-3 text-right font-mono text-slate-700">2,304</td>
                <td className="p-3 text-right font-mono text-slate-700">107,368</td>
                <td className="p-3 text-slate-600">N ≥ 400 constituency rows; codes -990/-991/-992 removed</td>
                <td className="p-3 text-center">
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold text-[10px]">VERIFIED</span>
                </td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="p-3 font-semibold text-slate-900">India 14 Major States</td>
                <td className="p-3 text-slate-600">Election Commission of India (ECI)</td>
                <td className="p-3 text-right font-mono text-slate-700">18 (1951–2019)</td>
                <td className="p-3 text-right font-mono text-slate-700">7,997</td>
                <td className="p-3 text-slate-600">N ≥ 200 records, unique constituencies ≥ 20</td>
                <td className="p-3 text-center">
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold text-[10px]">VERIFIED</span>
                </td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="p-3 font-semibold text-slate-900">Pre vs Post EVM Study</td>
                <td className="p-3 text-slate-600">ECI Official Results</td>
                <td className="p-3 text-right font-mono text-slate-700">10 (5 pre, 5 post)</td>
                <td className="p-3 text-right font-mono text-slate-700">4,751</td>
                <td className="p-3 text-slate-600">Symmetric 5-vs-5 cohort design (1989-1999 vs 2004-2024)</td>
                <td className="p-3 text-center">
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold text-[10px]">VERIFIED</span>
                </td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="p-3 font-semibold text-slate-900">Spatial Margin Contours</td>
                <td className="p-3 text-slate-600">ECI + Survey of India GIS</td>
                <td className="p-3 text-right font-mono text-slate-700">3 (2014, 2019, 2024)</td>
                <td className="p-3 text-right font-mono text-slate-700">UP, Bihar, WB</td>
                <td className="p-3 text-slate-600">Centroids matched with Post-2008 Delimitation orders</td>
                <td className="p-3 text-center">
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold text-[10px]">VERIFIED</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DataPipeline;
