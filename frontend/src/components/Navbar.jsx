import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HardDrive, Database, Cpu } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  return (
    <header className="border-b border-slate-800 bg-slate-950 px-8 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
      {/* Left Section: App Title & Version Badge */}
      <div className="flex items-center gap-3">
        <span className="text-xl font-black tracking-wider text-emerald-400">
          STONKS MAKER
        </span>
        <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
          v1.0
        </span>
      </div>

      {/* Center Section: View Navigation Links */}
      <nav className="flex space-x-8 text-sm font-semibold">
        <Link
          to="/"
          className={`transition ${
            location.pathname === '/'
              ? 'text-emerald-400 border-b-2 border-emerald-400 pb-1'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Dashboard
        </Link>
        <span className="text-slate-600 cursor-not-allowed flex items-center gap-1">
          Analytics <span className="text-[10px] text-slate-600 font-mono">(v2)</span>
        </span>
        <span className="text-slate-600 cursor-not-allowed flex items-center gap-1">
          RAG Chatbot <span className="text-[10px] text-slate-600 font-mono">(v2)</span>
        </span>
      </nav>

      {/* Right Section: Cloud & Infrastructure Status Indicators */}
      <div className="flex items-center gap-2 text-[11px] font-mono">
        {/* Azure ADLS Status Tag */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700/80 px-2.5 py-1 rounded-md text-slate-300">
          <HardDrive size={13} className="text-sky-400" />
          <span>Azure ADLS:</span>
          <span className="text-emerald-400 font-bold">Connected</span>
        </div>

        {/* Databricks Delta Status Tag */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700/80 px-2.5 py-1 rounded-md text-slate-300">
          <Database size={13} className="text-orange-400" />
          <span>DBX Delta:</span>
          <span className="text-emerald-400 font-bold">Gold Active</span>
        </div>
      </div>
    </header>
  );
}