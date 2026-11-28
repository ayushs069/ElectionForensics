import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import WorldResearch from './tabs/WorldResearch';
import IndianResults from './tabs/IndianResults';
import YearwiseRVM from './tabs/YearwiseRVM';
import PrePostEVM from './tabs/PrePostEVM';
import ContourPlots from './tabs/ContourPlots';
import RVMModel from './tabs/RVMModel';
import MarginMeasures from './tabs/MarginMeasures';
import DataPipeline from './tabs/DataPipeline';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('world');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'world':
        return <WorldResearch />;
      case 'india':
        return <IndianResults />;
      case 'yearwise':
        return <YearwiseRVM />;
      case 'prepost':
        return <PrePostEVM />;
      case 'contour':
        return <ContourPlots />;
      case 'rvm-model':
        return <RVMModel />;
      case 'margins':
        return <MarginMeasures />;
      case 'pipeline':
        return <DataPipeline />;
      default:
        return <WorldResearch />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex font-sans text-slate-800">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content Area (offset by sidebar width 240px) */}
      <div className="flex-1 ml-60 flex flex-col min-h-screen">
        {/* Top Academic Header */}
        <header className="sticky top-0 z-10 bg-white border-b border-slate-200 px-8 py-3.5 flex items-center justify-between shadow-xs">
          <div>
            <h1 className="text-sm font-bold text-slate-800 tracking-tight">
              Universal Statistical Patterns & Electoral Forensics of Indian General Elections
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              PRJ-IV Final Project &bull; School of Engineering & Technology &bull; BML Munjal University &bull; Mentor: Dr. Hirdesh Kumar Pharasi
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md border border-blue-200 font-mono">
              RVM ⟨μ⟩ = 0.1993
            </span>
            <span className="text-xs text-slate-400">|</span>
            <span className="text-xs text-slate-500 font-medium">Ayush &bull; Anuj &bull; Dhiren</span>
          </div>
        </header>

        {/* Dynamic Tab Body */}
        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {renderActiveTab()}
        </main>

        {/* Academic Footer */}
        <footer className="bg-white border-t border-slate-200 px-8 py-4 text-xs text-slate-500 flex flex-wrap justify-between items-center gap-2">
          <span>
            Election Forensics Research Dashboard &bull; Random Voting Model (Pal et al., 2024)
          </span>
          <span className="text-slate-400">
            Data Sources: Election Commission of India (ECI) &amp; CLEA (University of Michigan)
          </span>
        </footer>
      </div>
    </div>
  );
};

export default App;
