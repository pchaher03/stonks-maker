import React from 'react';
import { Newspaper, ExternalLink, Clock, Tag } from 'lucide-react';

export default function HeadlinesStream({ articles, loading, className = '' }) {
  // Skeleton / Loading State
  if (loading) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg animate-pulse col-span-1 md:col-span-3 ${className}`}>
        <div className="flex justify-between items-center mb-4">
          <div className="h-4 bg-slate-700 rounded w-1/4"></div>
          <div className="h-4 bg-slate-700 rounded w-1/12"></div>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-slate-900/50 p-4 rounded-lg space-y-2 border border-slate-700/50">
              <div className="h-4 bg-slate-700 rounded w-3/4"></div>
              <div className="h-3 bg-slate-700 rounded w-1/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Fallback when no articles are loaded
  if (!articles || articles.length === 0) {
    return (
      <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg col-span-1 md:col-span-3 text-center text-slate-500 py-10 ${className}`}>
        <Newspaper size={28} className="mx-auto mb-2 opacity-50" />
        <p className="text-sm">No recent headlines found for this ticker.</p>
      </div>
    );
  }

  // Helper function to format publication dates into relative timestamps
  const formatRelativeTime = (timestamp) => {
    if (!timestamp) return 'Recently';
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));

    if (isNaN(diffInMinutes) || diffInMinutes < 0) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  // Helper to determine headline sentiment badge color & text
  const getSentimentBadge = (article) => {
    // If individual article score is provided or fallback to compound
    const score = article.compound_score ?? article.sentiment_score ?? 0;

    if (score >= 0.05) {
      return (
        <span className="text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full uppercase tracking-wider">
          Positive
        </span>
      );
    } else if (score <= -0.05) {
      return (
        <span className="text-[10px] font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded-full uppercase tracking-wider">
          Negative
        </span>
      );
    }
    return (
      <span className={`text-[10px] font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full uppercase tracking-wider ${className}`}>
        Neutral
      </span>
    );
  };

  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg col-span-1 md:col-span-3 hover:border-slate-600 transition-all flex flex-col justify-between ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <Newspaper size={18} className="text-emerald-400" />
          <h3 className="text-slate-400 font-semibold text-xs uppercase tracking-wider">
            Live Financial News & Headlines
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-mono">
          {articles.length} {articles.length === 1 ? 'Article' : 'Articles'}
        </span>
      </div>

      {/* Scrollable Headline Feed Container */}
      <div className="max-h-72 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-900">
        {articles.map((item, index) => (
          <div
            key={index}
            className="bg-slate-900/60 hover:bg-slate-900 border border-slate-700/60 hover:border-slate-600 p-3.5 rounded-lg transition-all group"
          >
            <div className="flex items-start justify-between gap-3">
              <a
                href={item.url || '#'}
                target="_blank"
                rel="noreferrer"
                className="text-sm font-medium text-slate-200 group-hover:text-emerald-400 transition-colors line-clamp-2 flex-1"
              >
                {item.title}
              </a>
              {getSentimentBadge(item)}
            </div>

            {/* Sub-meta: Source & Timestamp */}
            <div className="flex items-center gap-4 mt-2 text.xs text-slate-400 font-mono text-[11px]">
              <span className="flex items-center gap-1 text-slate-400">
                <Tag size={12} className="text-slate-500" />
                {item.source || 'Financial News'}
              </span>
              <span className="flex items-center gap-1 text-slate-500">
                <Clock size={12} />
                {formatRelativeTime(item.timestamp)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}