import React, { useState } from 'react';
import { Shield, Bell, RefreshCw, Radio, Menu, X } from 'lucide-react';
import { useApp } from '../../context/AppContext';

const Navbar = () => {
  const { 
    triggerRefresh, 
    isSidebarOpen, 
    toggleSidebar, 
    isSidebarCollapsed, 
    toggleSidebarCollapse 
  } = useApp();
  const [isSpinning, setIsSpinning] = useState(false);

  const handleRefresh = () => {
    setIsSpinning(true);
    triggerRefresh();
    setTimeout(() => setIsSpinning(false), 700);
  };

  const handleMenuClick = () => {
    if (window.innerWidth < 768) {
      toggleSidebar();
    } else {
      toggleSidebarCollapse();
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-sm transition-all duration-200">
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Clickable Menu Toggle Button (Desktop Collapse + Mobile Drawer) */}
        <button
          onClick={handleMenuClick}
          className="p-2 text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-all duration-200 flex items-center justify-center focus:outline-none active:scale-95 group"
          title="Toggle Navigation Menu (Expand / Collapse)"
          aria-label="Toggle Navigation Menu"
        >
          <Menu className="w-5 h-5 transition-transform duration-300 group-hover:scale-110 text-slate-700 group-hover:text-blue-600" />
        </button>

        <div className="p-2 bg-blue-900 text-white rounded-lg shadow-md flex items-center justify-center shrink-0">
          <Shield className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <h1 className="text-sm sm:text-base font-bold text-slate-900 leading-tight truncate">
            Adaptive UEBA Intelligence
          </h1>
          <p className="hidden sm:block text-[11px] text-slate-500 font-mono truncate">
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
          onClick={handleRefresh}
          className="p-2 text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-all"
          title="Refresh Data across active dashboard"
        >
          <RefreshCw className={`w-4 h-4 ${isSpinning ? 'animate-spin text-blue-600' : ''}`} />
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
