import React from 'react';
import { TrendingUp, TrendingDown, Shield, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function PredictionCard({ data, loading, className = '' }) {
  // Skeleton / Loading State
  if (loading) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg animate-pulse flex flex-col justify-between h-52 ${className}`}>
        <div className="flex justify-between items-center">
          <div className="h-4 bg-slate-700 rounded w-1/3"></div>
          <div className="h-6 bg-slate-700 rounded-full w-16"></div>
        </div>
        <div className="space-y-2 my-4">
          <div className="h-8 bg-slate-700 rounded w-1/2"></div>
          <div className="h-3 bg-slate-700 rounded w-1/4"></div>
        </div>
        <div className="h-6 bg-slate-700 rounded w-full"></div>
      </div>
    );
  }

  // Fallback if data hasn't loaded yet
  if (!data) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex items-center justify-center h-52 text-slate-500 ${className}`}>
        <p className="text-sm">Select a ticker to view prediction insights.</p>
      </div>
    );
  }

  const isUp = data.direction === 'UP';

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex flex-col justify-between hover:border-slate-600 transition-all ${className}`}>
      {/* Header: Widget Title & Directional Badge */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-slate-400 font-semibold text-xs uppercase tracking-wider">
            Model Inference
          </h3>
          <span className="text-[10px] bg-slate-700/60 text-slate-300 px-1.5 py-0.5 rounded font-mono">
            {data.ticker}
          </span>
        </div>

        {/* Direction Badge */}
        <span
          className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-extrabold tracking-wide ${
            isUp
              ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
              : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
          }`}
        >
          {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {data.direction}
        </span>
      </div>

      {/* Primary Value: Target Price & Target Return */}
      <div className="my-2">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-extrabold text-white tracking-tight">
            ${typeof data.target_price === 'number' ? data.target_price.toFixed(2) : data.target_price}
          </span>
          <span
            className={`flex items-center text-xs font-bold ${
              isUp ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
            {isUp ? 'Bullish Target' : 'Bearish Target'}
          </span>
        </div>
        <p className="text-[11px] text-slate-400 mt-1">
          Estimated price target for selected horizon
        </p>
      </div>

      {/* Footer: Strategy Suitability Badge */}
      <div className="flex items-center justify-between border-t border-slate-700/80 pt-3 mt-2">
        <div className="flex items-center gap-1.5 text-xs text-slate-300">
          <Shield size={15} className="text-indigo-400" />
          <span>Strategy Fit:</span>
        </div>
        <span className="text-xs font-bold text-indigo-300 bg-indigo-500/15 border border-indigo-500/30 px-2.5 py-0.5 rounded-md font-mono uppercase tracking-wider">
          {data.recommended_strategy || 'N/A'}
        </span>
      </div>
    </div>
  );
}