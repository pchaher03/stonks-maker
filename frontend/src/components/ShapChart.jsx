import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';
import { Cpu, HelpCircle } from 'lucide-react';

export default function ShapChart({ data, loading, className='' }) {
  // Skeleton / Loading State
  if (loading) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg animate-pulse col-span-1 md:col-span-2 h-80 flex flex-col justify-between ${className}`}>
        <div className="flex justify-between items-center">
          <div className="h-4 bg-slate-700 rounded w-1/3"></div>
          <div className="h-4 bg-slate-700 rounded w-1/6"></div>
        </div>
        <div className="h-48 bg-slate-700/50 rounded w-full my-auto"></div>
        <div className="h-3 bg-slate-700 rounded w-1/4"></div>
      </div>
    );
  }

  // Fallback when data hasn't loaded or is missing
  if (!data || !data.feature_contributions) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg col-span-1 md:col-span-2 flex items-center justify-center h-80 text-slate-500 ${className}`}>
        <p className="text-sm">No SHAP feature attribution data available.</p>
      </div>
    );
  }

  // Transform object schema into array format required by Recharts
  const chartData = Object.entries(data.feature_contributions)
    .map(([feature, value]) => ({
      feature,
      value: Number(value.toFixed(4)),
    }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value)); // Sort by magnitude

  const baseVal =
    typeof data.base_value === 'number'
      ? data.base_value.toFixed(4)
      : 'N/A';

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg col-span-1 md:col-span-2 hover:border-slate-600 transition-all flex flex-col justify-between ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <Cpu size={18} className="text-indigo-400" />
          <h3 className="text-slate-400 font-semibold text-xs uppercase tracking-wider">
            Model Explainability (SHAP XAI)
          </h3>
        </div>
        <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400 bg-slate-900/60 px-2 py-1 rounded border border-slate-700/60">
          <span>Base Value:</span>
          <span className="text-indigo-300 font-bold">{baseVal}</span>
        </div>
      </div>

      {/* Recharts Horizontal Bar Chart */}
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 50, bottom: 5 }}
          >
            <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
            <YAxis
              dataKey="feature"
              type="category"
              stroke="#94a3b8"
              width={110}
              tick={{ fontSize: 11, fontFamily: 'monospace' }}
            />
            <Tooltip
              cursor={{ fill: 'rgba(51, 65, 85, 0.3)' }}
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '0.5rem',
                color: '#f8fafc',
                fontSize: '12px',
              }}
              formatter={(value) => [
                `${value > 0 ? '+' : ''}${value}`,
                'SHAP Impact',
              ]}
            />
            <ReferenceLine x={0} stroke="#475569" strokeWidth={1.5} />
            <Bar dataKey="value" radius={[2, 2, 2, 2]}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.value >= 0 ? '#10b981' : '#f43f5e'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend Footer */}
      <div className="flex justify-between items-center border-t border-slate-700/80 pt-3 text-[11px] text-slate-400">
        <div className="flex gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
            Bullish Impact (+)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
            Bearish Impact (-)
          </span>
        </div>
        <div className="flex items-center gap-1 text-slate-500">
          <HelpCircle size={13} />
          <span>Feature contribution vectors</span>
        </div>
      </div>
    </div>
  );
}