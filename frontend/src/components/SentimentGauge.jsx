import React from 'react';
import { Activity, Smile, Meh, Frown } from 'lucide-react';

export default function SentimentGauge({ data, loading, className = '' }) {
  // Skeleton / Loading State
  if (loading) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg animate-pulse flex flex-col justify-between h-52 ${className}`}>
        <div className="flex justify-between items-center">
          <div className="h-4 bg-slate-700 rounded w-1/3"></div>
          <div className="h-5 bg-slate-700 rounded-full w-12"></div>
        </div>
        <div className="space-y-2 my-auto">
          <div className="h-6 bg-slate-700 rounded w-1/2 mx-auto"></div>
          <div className="h-3 bg-slate-700 rounded w-1/3 mx-auto"></div>
        </div>
        <div className="h-4 bg-slate-700 rounded w-full"></div>
      </div>
    );
  }

  // Fallback state if no data available
  if (!data) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex items-center justify-center h-52 text-slate-500 ${className}`}>
        <p className="text-sm">No news sentiment loaded.</p>
      </div>
    );
  }

  const compound = data.compound_score ?? 0;
  const posPct = Math.round((data.pos_score ?? 0) * 100);
  const neuPct = Math.round((data.neu_score ?? 0) * 100);
  const negPct = Math.round((data.neg_score ?? 0) * 100);

  // Map compound score (-1.0 to 1.0) into gauge needle percentage (0% to 100%)
  const gaugePercentage = Math.min(Math.max(((compound + 1) / 2) * 100, 0), 100);

  // Determine visual label & icon based on compound score
  let label = 'Neutral';
  let labelColor = 'text-amber-400';
  let Icon = Meh;

  if (compound >= 0.15) {
    label = 'Bullish Sentiment';
    labelColor = 'text-emerald-400';
    Icon = Smile;
  } else if (compound <= -0.15) {
    label = 'Bearish Sentiment';
    labelColor = 'text-rose-400';
    Icon = Frown;
  }

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex flex-col justify-between hover:border-slate-600 transition-all ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-2">
          <Activity size={16} className="text-emerald-400" />
          <h3 className="text-slate-400 font-semibold text-xs uppercase tracking-wider">
            NLP News Sentiment
          </h3>
        </div>
        <span className="text-[10px] bg-slate-700/60 text-slate-300 px-1.5 py-0.5 rounded font-mono">
          FinBERT / VADER
        </span>
      </div>

      {/* Main Meter & Score */}
      <div className="my-2 text-center">
        {/* Semi-circle Gauge Arc */}
        <div className="relative w-48 h-12 mx-auto overflow-hidden">
          <div className="w-48 h-48 rounded-full border-10 border-slate-700 border-t-emerald-500 border-r-emerald-500/40 border-l-rose-500/40 border-b-rose-500 transform -rotate-45" />
          {/* Gauge Needle */}
          <div
            className="absolute bottom-0 left-1/2 w-1 h-10 bg-white origin-bottom -translate-x-1/2 transition-transform duration-500 ease-out shadow-md"
            style={{ transform: `translateX(-50%) rotate(${gaugePercentage * 1.8 - 90}deg)` }}
          />
        </div>

        <div className="flex items-center justify-center gap-1.5 mt-2">
          <Icon size={18} className={labelColor} />
          <span className={`text-sm font-extrabold ${labelColor}`}>{label}</span>
        </div>

        <div className="text-xs font-mono text-slate-400 mt-0.5">
          Compound Score: <span className="text-white font-bold">{compound.toFixed(2)}</span>
        </div>
      </div>

      {/* FinBERT Distribution Breakdown Bar */}
      <div className="pt-3 border-t border-slate-700/80">
        <div className="flex justify-between text-[11px] text-slate-400 mb-1 font-medium">
          <span className="text-emerald-400 font-semibold">Pos: {posPct}%</span>
          <span className="text-slate-300 font-semibold">Neu: {neuPct}%</span>
          <span className="text-rose-400 font-semibold">Neg: {negPct}%</span>
        </div>

        {/* Stacked Percentage Bar */}
        <div className="h-2 w-full bg-slate-700 rounded-full overflow-hidden flex">
          <div style={{ width: `${posPct}%` }} className="bg-emerald-500 transition-all duration-300" />
          <div style={{ width: `${neuPct}%` }} className="bg-slate-400 transition-all duration-300" />
          <div style={{ width: `${negPct}%` }} className="bg-rose-500 transition-all duration-300" />
        </div>
      </div>
    </div>
  );
}