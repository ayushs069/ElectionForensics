import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

type ColorVariant = 'blue' | 'green' | 'red' | 'orange' | 'purple';

interface KpiCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  color?: ColorVariant;
  trend?: 'up' | 'down' | 'neutral';
}

const COLOR_MAP: Record<ColorVariant, { border: string; bg: string; text: string; icon: string }> = {
  blue: { border: 'border-l-blue-500', bg: 'bg-blue-50', text: 'text-blue-700', icon: 'text-blue-400' },
  green: { border: 'border-l-emerald-500', bg: 'bg-emerald-50', text: 'text-emerald-700', icon: 'text-emerald-400' },
  red: { border: 'border-l-red-500', bg: 'bg-red-50', text: 'text-red-700', icon: 'text-red-400' },
  orange: { border: 'border-l-orange-500', bg: 'bg-orange-50', text: 'text-orange-700', icon: 'text-orange-400' },
  purple: { border: 'border-l-purple-500', bg: 'bg-purple-50', text: 'text-purple-700', icon: 'text-purple-400' },
};

const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  subtitle,
  color = 'blue',
  trend,
}) => {
  const colors = COLOR_MAP[color];

  const TrendIcon =
    trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

  return (
    <div className={`kpi-card border-l-4 ${colors.border}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">{label}</p>
          <p className={`text-2xl font-bold ${colors.text}`}>{value}</p>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        {trend && (
          <div className={`p-2 rounded-lg ${colors.bg}`}>
            <TrendIcon className={`w-4 h-4 ${colors.icon}`} />
          </div>
        )}
      </div>
    </div>
  );
};

export default KpiCard;
