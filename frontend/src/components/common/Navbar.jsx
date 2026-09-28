import React from 'react';
import { Shield, Bell, RefreshCw, Radio } from 'lucide-react';
import { useApp } from '../../context/AppContext';

const Navbar = () => {
  const { triggerRefresh } = useApp();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-900 text-white rounded-lg shadow-md flex items-center justify-center">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-bold text-slate-900 leading-tight">
            Adaptive UEBA Intelligence
          </h1>
          <p className="text-xs text-slate-500 font-mono">
            CMU CERT r5.2 • Contamination-Resistant Engine Active
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Live System Indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full text-xs font-semibold">
          <Radio className="w-3.5 h-3.5 text-green-600 animate-pulse" />
          <span>Real-time Scoring</span>
        </div>

        {/* Manual Refresh Action */}
        <button
          onClick={triggerRefresh}
          className="p-2 text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-colors"
          title="Refresh Data"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        {/* Analyst Profile Badge */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center border border-blue-200 shadow-sm">
            SOC
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-800">Senior Analyst</p>
            <p className="text-[10px] text-slate-500">Tier 3 Triage</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
