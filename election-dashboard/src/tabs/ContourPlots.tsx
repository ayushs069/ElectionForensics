import React, { useState } from 'react';
import KpiCard from '../components/KpiCard';
import ImageViewer from '../components/ImageViewer';
import { CONTOUR_DATA } from '../data/staticData';

const STATES = ['Bihar', 'Uttar Pradesh', 'West Bengal'] as const;
const RECENT_YEARS = [2014, 2019, 2024] as const;

type StateName = typeof STATES[number];
type RecentYear = typeof RECENT_YEARS[number];

const ContourPlots: React.FC = () => {
  const [selectedState, setSelectedState] = useState<StateName>('Uttar Pradesh');
  const [selectedYear, setSelectedYear] = useState<RecentYear>(2019);
  const [comparisonMode, setComparisonMode] = useState<boolean>(false);

  const getStateFolder = (state: StateName) => {
    if (state === 'Uttar Pradesh') return 'UP';
    if (state === 'Bihar') return 'BIHAR';
    return 'WB';
  };

  const getContourPath = (state: StateName, year: number) => {
    const folder = getStateFolder(state);
    const statePrefix = state.replace(' ', '_');
    return `/plots/contour/Last3_Elections/${folder}/${statePrefix}_${year}_contour.png`;
  };

  const currentData = CONTOUR_DATA.find(
    (c) => c.state === selectedState && c.year === selectedYear
  ) || CONTOUR_DATA[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Spatial Analysis — Winning Margin Contour Plots</h1>
        <p className="text-sm text-slate-500 mt-1">
          Constituency-level geographic margin landscapes mapped via Delaunay triangulation and cubic spline interpolation 
          across the three major politically dynamic states: Uttar Pradesh (80 seats), Bihar (40 seats), and West Bengal (42 seats).
        </p>
      </div>

      {/* KPI Cards for Selected State & Year */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label={`Selected Election`}
          value={`${selectedState} (${selectedYear})`}
          subtitle={`${currentData.n_matched} Constituencies Mapped`}
          color="blue"
        />
        <KpiCard
          label="Highest Victory Margin"
          value={currentData.highest_margin.toLocaleString()}
          subtitle={`Constituency: ${currentData.highest_cst}`}
          color="red"
        />
        <KpiCard
          label="Lowest Victory Margin"
          value={currentData.lowest_margin.toLocaleString()}
          subtitle={`Constituency: ${currentData.lowest_cst}`}
          color="purple"
        />
        <KpiCard
          label="Delimitation Boundary"
          value="Post-2008 Order"
          subtitle="Election Commission of India GIS boundary"
          color="green"
        />
      </div>

      {/* Controls Bar */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">State:</span>
          {STATES.map((state) => (
            <button
              key={state}
              onClick={() => setSelectedState(state)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                selectedState === state
                  ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {state}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Election Year:</span>
          {RECENT_YEARS.map((yr) => (
            <button
              key={yr}
              onClick={() => {
                setSelectedYear(yr);
                setComparisonMode(false);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                !comparisonMode && selectedYear === yr
                  ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {yr}
            </button>
          ))}
          <button
            onClick={() => setComparisonMode(!comparisonMode)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              comparisonMode
                ? 'bg-purple-600 text-white border-purple-600 shadow-sm'
                : 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100'
            }`}
          >
            {comparisonMode ? 'Single View' : 'Compare 2014 vs 2019 vs 2024'}
          </button>
        </div>
      </div>

      {/* Main Display Area */}
      {!comparisonMode ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <ImageViewer
              src={getContourPath(selectedState, selectedYear)}
              title={`${selectedState} — ${selectedYear} General Election Vote Margin Contour`}
              className="w-full"
            />
          </div>

          <div className="space-y-4">
            {/* Color Scale Legend Card */}
            <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-3">
              <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">How to Read Contours</h3>
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-red-600 flex-shrink-0" />
                  <span className="text-slate-700 font-medium">Red / Orange</span>
                  <span className="text-slate-400">— High margins (one-sided wins)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-yellow-400 flex-shrink-0" />
                  <span className="text-slate-700 font-medium">Yellow / Green</span>
                  <span className="text-slate-400">— Moderate margins (normal)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-blue-600 flex-shrink-0" />
                  <span className="text-slate-700 font-medium">Blue / Cyan</span>
                  <span className="text-slate-400">— Close contests (knife-edge)</span>
                </div>
              </div>
            </div>

            {/* Political Analysis Card */}
            <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-2 text-xs text-slate-600">
              <h3 className="font-semibold text-slate-800 uppercase tracking-wider">Geographic Findings</h3>
              {selectedState === 'Uttar Pradesh' && (
                <p>
                  In 2014 and 2019, western and central UP formed a continuous high-margin ridge (peaking in Ghaziabad with over 500k margin). 
                  In 2024, the landscape fragmented substantially with competitive blue/green pockets emerging across eastern UP and Awadh.
                </p>
              )}
              {selectedState === 'Bihar' && (
                <p>
                  2019 saw intense NDA concentration (Madhubani margin &gt;454k), whereas 2014 and 2024 showed localized competitive pockets around Saran, Samastipur, and southern Bihar.
                </p>
              )}
              {selectedState === 'West Bengal' && (
                <p>
                  Contour plots highlight intense bipolarity in 2019 and 2024. Darjeeling in the north consistently registered massive margins, while central and south Bengal showed tight contests (Arambagh margin of just 1,142 in 2019).
                </p>
              )}
            </div>

            {/* Methodology Note */}
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs text-slate-500 space-y-1">
              <p className="font-semibold text-slate-700">Triangulation Method</p>
              <p>
                Each constituency centroid is derived from official Survey of India / ECI shapefiles. 
                Spatial interpolation uses Delaunay triangulation with Clough-Tocher 2D cubic splines bounded by state borders.
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* 3-Year Comparison Mode */
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {RECENT_YEARS.map((yr) => (
              <div key={yr} className="space-y-2">
                <div className="text-center font-bold text-slate-800 text-sm bg-white py-1.5 rounded-lg border border-slate-200">
                  {selectedState} — {yr}
                </div>
                <ImageViewer
                  src={getContourPath(selectedState, yr)}
                  title={`${selectedState} (${yr})`}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContourPlots;
