import React from 'react';
import { TrendingUp, TrendingDown, Shield, ArrowUpRight, ArrowDownRight, DollarSign } from 'lucide-react';

export default function PredictionCard({ data, loading, className = '' }) {
  // Skeleton / Loading State
  if (loading) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg animate-pulse flex flex-col justify-between h-56 ${className}`}>
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
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex items-center justify-center h-56 text-slate-500 ${className}`}>
        <p className="text-sm">Select a ticker to view prediction insights.</p>
      </div>
    );
  }

  const currentPrice = typeof data.current_price === 'number' ? data.current_price : null;
  const targetPrice = typeof data.target_price === 'number' ? data.target_price : null;

  const changeValue =
  currentPrice !== null && targetPrice !== null && currentPrice !== 0
    ? ((targetPrice - currentPrice) / currentPrice) * 100
    : null;

  // Calculate percentage change between current price and target price
  const percentChange = changeValue !== null ? changeValue.toFixed(2) : null;

  // Prefer the real price movement; fall back to the label (normalized)
  const labelIsUp = String(data.direction || '').trim().toUpperCase() === 'UP';
  const isUp = changeValue !== null ? changeValue >= 0 : labelIsUp;

  // What the badge displays, so text always matches color
  const directionLabel = isUp ? 'UP' : 'DOWN';

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg flex flex-col justify-between hover:border-slate-600 transition-all ${className}`}>
      {/* Header: Company Name, Ticker Badge & Directional Badge */}
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-white font-bold text-base tracking-wide">
              {data.company_name || data.ticker}
            </h3>
            <span className="text-[10px] bg-slate-700/80 text-emerald-400 px-1.5 py-0.5 rounded font-mono font-semibold border border-slate-600">
              {data.ticker}
            </span>
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">Model Inference</span>
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
          {directionLabel}
        </span>
      </div>

      {/* Primary Value Container: Target Price & Most Recent Closed Price */}
      <div className="my-3 p-3 bg-slate-900/60 rounded-lg border border-slate-700/50">
        <div className="flex items-baseline justify-between">
          {/* Target Price */}
          <div>
            <span className="text-[10px] text-slate-400 block font-mono uppercase tracking-wider">
              Target Price
            </span>
            <div className="flex items-baseline gap-1.5 mt-0.5">
              <span className="text-2xl font-extrabold text-white tracking-tight font-mono">
                ${targetPrice !== null ? targetPrice.toFixed(2) : 'N/A'}
              </span>
              <span className={`flex items-center text-xs font-bold ${isUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                {percentChange !== null ? `${percentChange > 0 ? '+' : ''}${percentChange}%` : ''}
              </span>
            </div>
          </div>

          {/* Most Recent Closed Day Stock Price */}
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono uppercase tracking-wider">
              Last Close
            </span>
            <span className="text-lg font-bold text-slate-300 font-mono block mt-0.5">
              {currentPrice !== null ? `$${currentPrice.toFixed(2)}` : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer: Strategy Suitability Badge */}
      <div className="flex items-center justify-between border-t border-slate-700/80 pt-3">
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