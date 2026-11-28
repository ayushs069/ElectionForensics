import React from 'react';
import {
  Globe,
  BarChart2,
  TrendingUp,
  GitCompare,
  Map,
  Cpu,
  Ruler,
  Database,
} from 'lucide-react';

const TAB_IDS = ['world', 'india', 'yearwise', 'prepost', 'contour', 'rvm-model', 'margins', 'pipeline'];

const NAV_ITEMS = [
  { id: 'world', label: 'World Research', icon: Globe },
  { id: 'india', label: 'Indian Results', icon: BarChart2 },
  { id: 'yearwise', label: 'Year-Wise RVM', icon: TrendingUp },
  { id: 'prepost', label: 'Pre-EVM vs Post-EVM', icon: GitCompare },
  { id: 'contour', label: 'Contour Maps', icon: Map },
  { id: 'rvm-model', label: 'RVM Model', icon: Cpu },
  { id: 'margins', label: 'Margin Measures', icon: Ruler },
  { id: 'pipeline', label: 'Data Pipeline', icon: Database },
];

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-white border-r border-slate-200 flex flex-col shadow-sm z-20">
      {/* Logo / Title */}
      <div className="px-5 py-5 border-b border-slate-100">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <BarChart2 className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-bold text-slate-800 leading-tight">ElecForensics</span>
        </div>
        <p className="text-xs text-slate-500 leading-tight mt-1">Research Dashboard</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onTabChange(id)}
            className={`sidebar-link w-full text-left ${activeTab === id ? 'active' : ''}`}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-100 bg-slate-50">
        <p className="text-xs text-slate-500 font-medium">PRJ-IV</p>
        <p className="text-xs text-slate-400 mt-0.5">BML Munjal University</p>
      </div>
    </aside>
  );
};

export { TAB_IDS };
export default Sidebar;
