import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Calendar } from 'lucide-react';
import { fetchPrediction, fetchSentiment, fetchExplanation } from '../services/api';
import PredictionCard from '../components/PredictionCard';
import SentimentGauge from '../components/SentimentGauge';
import ShapChart from '../components/ShapChart';
import HeadlinesStream from '../components/HeadlinesStream';

export default function Dashboard() {
  const [inputs, setInputs] = useState({
    ticker: 'AAPL',
    horizon: '1D',
  });

  const [activeTicker, setActiveTicker] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [data, setData] = useState({
    prediction: null,
    sentiment: null,
    explanation: null,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setInputs((prev) => ({ 
      ...prev, 
      [name]: value.toUpperCase() 
    }));
  };

  // Asynchronous REST calls triggered in parallel via Promise.all
  const loadTickerData = async (symbol, timeHorizon) => {
    setLoading(true);
    setError(null);

    setData({
      prediction: null,
      sentiment: null,
      explanation: null,
    });

    try {
      const [predictionRes, sentimentRes, explanationRes] = await Promise.all([
        fetchPrediction(symbol, timeHorizon),
        fetchSentiment(symbol),
        fetchExplanation(symbol),
      ]);

      setData({
        prediction: predictionRes,
        sentiment: sentimentRes,
        explanation: explanationRes,
      });
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to fetch analysis data. Please check backend service status.');
    } finally {
      setLoading(false);
    }
  };

  // Initial load on component mount
  useEffect(() => {
    loadTickerData(activeTicker, inputs.horizon);
  }, []);

  // Form submission handler for ticker search
  const handleSearch = (e) => {
    e.preventDefault();
    if (!inputs.ticker.trim()) return;
    const formatted = inputs.ticker.trim();
    setActiveTicker(formatted);
    loadTickerData(formatted, inputs.horizon);
  };

  // Horizon change handler
  const handleHorizonChange = (selectedHorizon) => {
    setInputs((prev) => ({ ...prev, horizon: selectedHorizon }));
    loadTickerData(activeTicker, selectedHorizon);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* 3.1 Header Controls: Search Input, Horizon Picker, and CTA Button */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Ticker Search Form */}
        <form onSubmit={handleSearch} className="flex items-center gap-3 w-full md:w-auto flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
            <input
              type="text"
              name="ticker"
              value={inputs.ticker}
              onChange={handleInputChange}
              placeholder="ENTER TICKER (e.g. AAPL, NVDA, TSLA)"
              className="w-full bg-slate-900 border border-slate-700 text-white font-mono uppercase pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:border-emerald-500 text-sm tracking-wider"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 text-white font-semibold px-5 py-2 rounded-lg text-sm transition-all flex items-center gap-2 shadow-md shrink-0"
          >
            {loading ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <span>Analyze Ticker</span>
            )}
          </button>
        </form>

        {/* Horizon Picker Toggle Group */}
        <div className="flex items-center gap-2 bg-slate-900/80 p-1 rounded-lg border border-slate-700/80 shrink-0">
          <span className="text-xs text-slate-400 font-mono px-2 flex items-center gap-1">
            <Calendar size={13} />
            Horizon:
          </span>
          {['1D', '5D', '1M'].map((item) => (
            <button
              key={item}
              onClick={() => handleHorizonChange(item)}
              className={`px-3 py-1 text-xs font-mono rounded-md transition-all ${
                inputs.horizon === item
                  ? 'bg-emerald-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {/* Error Alert Display */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg text-xs font-mono">
          {error}
        </div>
      )}

      {/* 3.2 Dashboard Grid Wireframe */}
      {/* Row 1: Top Analysis Widgets */}
      <div className="flex flex-wrap grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Model Inferences (POST /v1/predictions) */}
        <PredictionCard 
          key={`pred-${activeTicker}`}
          data={data.prediction} 
          loading={loading} 
          className="w-full md:w-[calc(50%-12px)] shrink grow-0"
        />

        {/* Card 2: NLP Sentiment Gauge (GET /v1/news/{ticker}) */}
        <SentimentGauge 
          key={`sent-${activeTicker}`}
          data={data.sentiment} 
          loading={loading} 
          className="w-full md:w-[calc(50%-12px)] shrink grow-0"
        />

        {/* Card 3: Model Explainability SHAP Chart (GET /v1/explain/{ticker}) */}
        <ShapChart 
          key={`shap-${activeTicker}`}
          data={data.explanation} 
          loading={loading} 
          className="w-full"
        />

        {/* Card 4: Live Headlines Stream (GET /v1/news/{ticker}) - Full Width Row */}
        <HeadlinesStream
          key={`news-${activeTicker}`}
          articles={data.sentiment?.articles || []}
          loading={loading}
          className="w-full"
        />
      </div>
    </div>
  );
}