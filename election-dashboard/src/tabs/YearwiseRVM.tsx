import React, { useState, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
  ScatterChart, Scatter, Cell,
} from 'recharts';
import { YEARWISE_SUMMARY } from '../data/staticData';
import ImageViewer from '../components/ImageViewer';
import { getYearwisePlotPath } from '../utils/plotPaths';
import { AlertTriangle, Info } from 'lucide-react';

const STATE_OPTIONS = [
  { key: 'UTTAR_PRADESH', label: 'Uttar Pradesh' },
  { key: 'BIHAR', label: 'Bihar' },
  { key: 'GUJARAT', label: 'Gujarat' },
  { key: 'MADHYA_PRADESH', label: 'Madhya Pradesh' },
  { key: 'RAJASTHAN', label: 'Rajasthan' },
  { key: 'TAMIL_NADU', label: 'Tamil Nadu' },
  { key: 'WEST_BENGAL', label: 'West Bengal' },
];

const FLAGGED_EVENTS: Record<string, Record<number, string>> = {
  UTTAR_PRADESH: { 1977: "Post-Emergency anti-incumbency wave" },
  BIHAR: { 1977: "Post-Emergency anti-incumbency wave" },
  GUJARAT: { 1977: "Post-Emergency anti-incumbency wave" },
  MADHYA_PRADESH: { 1977: "Post-Emergency anti-incumbency wave" },
  RAJASTHAN: { 1977: "Post-Emergency anti-incumbency wave" },
};

const YearwiseRVM: React.FC = () => {
  const [selectedState, setSelectedState] = useState<string>('UTTAR_PRADESH');
  const [selectedYear, setSelectedYear] = useState<number>(1977);

  const stateData = useMemo(
    () => YEARWISE_SUMMARY.filter((r) => r.state === selectedState).sort((a, b) => a.year - b.year),
    [selectedState]
  );

  const availableYears = stateData.map((r) => r.year);

  const handleStateChange = (key: string) => {
    setSelectedState(key);
    const newData = YEARWISE_SUMMARY.filter((r) => r.state === key);
    if (newData.length > 0) setSelectedYear(newData[0].year);
  };

  const selectedRow = stateData.find((r) => r.year === selectedYear);
  const stateLabelObj = STATE_OPTIONS.find((s) => s.key === selectedState);
  const stateLabel = stateLabelObj?.label ?? selectedState;

  const plotSrc = getYearwisePlotPath(selectedState, selectedYear);
  const event = FLAGGED_EVENTS[selectedState]?.[selectedYear];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="section-title">Year-Wise RVM Analysis</h2>
        <p className="text-sm text-slate-500 mb-6">
          Constituency-level μ distribution compared to RVM predictions for each election year per state.
        </p>

        {/* Controls */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">State</label>
            <select
              value={selectedState}
              onChange={(e) => handleStateChange(e.target.value)}
              className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              {STATE_OPTIONS.map((s) => (
                <option key={s.key} value={s.key}>{s.label}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">Election Year</label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              {availableYears.map((yr) => {
                const row = stateData.find((r) => r.year === yr)!;
                return (
                  <option key={yr} value={yr}>
                    {yr} {row.flagged ? '⚠' : ''}
                  </option>
                );
              })}
            </select>
          </div>
        </div>
      </div>

      {/* Plot + Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ImageViewer src={plotSrc} title={`${stateLabel} ${selectedYear} – RVM Analysis`} />
        </div>
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
            <h4 className="font-semibold text-slate-700 text-sm mb-3">Selected Election Stats</h4>
            {selectedRow ? (
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-500">State</dt>
                  <dd className="font-medium text-slate-800">{stateLabel}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Year</dt>
                  <dd className="font-medium text-slate-800">{selectedRow.year}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Constituencies</dt>
                  <dd className="font-medium text-slate-800">{selectedRow.n_const}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Mean μ</dt>
                  <dd className="font-mono text-slate-800">{selectedRow.mean_mu.toFixed(4)}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">RVM Dev. Z</dt>
                  <dd className={`font-mono font-semibold ${selectedRow.rvm_dev_z > 3 ? 'text-red-600' : 'text-green-600'}`}>
                    {selectedRow.rvm_dev_z.toFixed(3)}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Status</dt>
                  <dd>
                    {selectedRow.flagged ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-red-700 bg-red-100 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="w-3 h-3" /> Flagged
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded-full">
                        ✓ Normal
                      </span>
                    )}
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="text-slate-400 text-sm">No data for selected year.</p>
            )}
          </div>
          {event && (
            <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl p-3">
              <Info className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs font-semibold text-amber-800 mb-0.5">Historical Context</p>
                <p className="text-xs text-amber-700">{event}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mean μ Line Chart */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <h3 className="font-semibold text-slate-700 mb-4 text-sm">Mean μ Over Elections – {stateLabel}</h3>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={stateData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} domain={['auto', 'auto']} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }} />
            <ReferenceLine y={0.199289} stroke="#3b82f6" strokeDasharray="4 2" label={{ value: 'RVM μ=0.199', position: 'right', fontSize: 9, fill: '#3b82f6' }} />
            <Line type="monotone" dataKey="mean_mu" stroke="#6366f1" strokeWidth={2} dot={{ r: 4, fill: '#6366f1' }} name="Mean μ" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Z-score Scatter */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-5">
        <h3 className="font-semibold text-slate-700 mb-1 text-sm">RVM Deviation Z-Score – {stateLabel}</h3>
        <p className="text-xs text-slate-400 mb-4">Red dots = flagged (Z &gt; 3.0)</p>
        <ResponsiveContainer width="100%" height={240}>
          <ScatterChart margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="year" type="number" domain={['dataMin - 2', 'dataMax + 2']} tick={{ fontSize: 11, fill: '#64748b' }} name="Year" />
            <YAxis dataKey="rvm_dev_z" tick={{ fontSize: 11, fill: '#64748b' }} name="Z-Score" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ payload }) => {
                if (!payload || payload.length === 0) return null;
                const d = payload[0].payload as (typeof stateData)[0];
                return (
                  <div className="bg-white border border-slate-200 rounded-lg p-2 text-xs shadow-md">
                    <p className="font-semibold">{d.year}</p>
                    <p>Z-Score: {d.rvm_dev_z.toFixed(3)}</p>
                    <p>Mean μ: {d.mean_mu.toFixed(4)}</p>
                    <p>N: {d.n_const}</p>
                  </div>
                );
              }}
            />
            <ReferenceLine y={3} stroke="#ef4444" strokeDasharray="6 3" label={{ value: 'Threshold Z=3', position: 'right', fontSize: 9, fill: '#ef4444' }} />
            <Scatter data={stateData} name="Elections">
              {stateData.map((entry, idx) => (
                <Cell key={idx} fill={entry.flagged ? '#ef4444' : '#6366f1'} r={6} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Table */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-700 text-sm">Year-wise Summary – {stateLabel}</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Year</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Constituencies</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Mean μ</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Z-Score</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {stateData.map((row, idx) => (
                <tr key={idx} className={`hover:bg-slate-50 transition-colors ${row.year === selectedYear ? 'bg-blue-50' : ''}`}>
                  <td className="px-4 py-3 font-medium text-slate-800">{row.year}</td>
                  <td className="px-4 py-3 text-right text-slate-600">{row.n_const}</td>
                  <td className="px-4 py-3 text-right font-mono text-slate-700">{row.mean_mu.toFixed(4)}</td>
                  <td className={`px-4 py-3 text-right font-mono font-semibold ${row.rvm_dev_z > 3 ? 'text-red-600' : 'text-green-600'}`}>
                    {row.rvm_dev_z.toFixed(3)}
                  </td>
                  <td className="px-4 py-3">
                    {row.flagged ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                        <AlertTriangle className="w-3 h-3" /> Flagged
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                        ✓ Normal
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl p-4">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> Flagged years (Z &gt; 3.0) correspond to known political events such as the
          1977 post-Emergency anti-incumbency wave, which produced unusually large margins across many constituencies.
          These are historically explained outliers, not indicators of fraud.
        </p>
      </div>
    </div>
  );
};

export default YearwiseRVM;
