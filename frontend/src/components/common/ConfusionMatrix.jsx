import React from 'react';

/**
 * ConfusionMatrix Component
 * Visualizes a 2x2 evaluation matrix (TP, FP, TN, FN) with derived metric badges.
 */
export default function ConfusionMatrix({
  tp = 0,
  fp = 0,
  tn = 0,
  fn = 0,
  title = 'Classification Performance Matrix'
}) {
  const total = tp + fp + tn + fn || 1;
  const precision = (tp + fp) > 0 ? (tp / (tp + fp)) : 0;
  const recall = (tp + fn) > 0 ? (tp / (tp + fn)) : 0;
  const f1 = (precision + recall) > 0 ? (2 * precision * recall) / (precision + recall) : 0;
  const accuracy = (tp + tn) / total;
  const fpr = (fp + tn) > 0 ? (fp / (fp + tn)) : 0;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-slate-200 tracking-wide uppercase flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          {title}
        </h4>
        <span className="text-xs text-slate-400 font-mono">N = {total.toLocaleString()}</span>
      </div>

      {/* 2x2 Matrix */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        {/* True Positive */}
        <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-lg p-3 text-center transition-transform hover:scale-[1.02]">
          <div className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider mb-1">
            True Positive (TP)
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-300">{tp.toLocaleString()}</div>
          <div className="text-[10px] text-slate-400 mt-1">{((tp / total) * 100).toFixed(1)}% of total</div>
        </div>

        {/* False Positive */}
        <div className="bg-rose-950/30 border border-rose-500/30 rounded-lg p-3 text-center transition-transform hover:scale-[1.02]">
          <div className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider mb-1">
            False Positive (FP)
          </div>
          <div className="text-2xl font-bold font-mono text-rose-300">{fp.toLocaleString()}</div>
          <div className="text-[10px] text-slate-400 mt-1">{((fp / total) * 100).toFixed(1)}% of total</div>
        </div>

        {/* False Negative */}
        <div className="bg-amber-950/30 border border-amber-500/30 rounded-lg p-3 text-center transition-transform hover:scale-[1.02]">
          <div className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider mb-1">
            False Negative (FN)
          </div>
          <div className="text-2xl font-bold font-mono text-amber-300">{fn.toLocaleString()}</div>
          <div className="text-[10px] text-slate-400 mt-1">{((fn / total) * 100).toFixed(1)}% of total</div>
        </div>

        {/* True Negative */}
        <div className="bg-blue-950/30 border border-blue-500/30 rounded-lg p-3 text-center transition-transform hover:scale-[1.02]">
          <div className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider mb-1">
            True Negative (TN)
          </div>
          <div className="text-2xl font-bold font-mono text-blue-300">{tn.toLocaleString()}</div>
          <div className="text-[10px] text-slate-400 mt-1">{((tn / total) * 100).toFixed(1)}% of total</div>
        </div>
      </div>

      {/* Derived Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-3 border-t border-slate-800 text-center">
        <div className="bg-slate-800/40 rounded p-2">
          <div className="text-[10px] text-slate-400 uppercase">Precision</div>
          <div className="text-sm font-bold text-cyan-300 font-mono">{(precision * 100).toFixed(1)}%</div>
        </div>
        <div className="bg-slate-800/40 rounded p-2">
          <div className="text-[10px] text-slate-400 uppercase">Recall</div>
          <div className="text-sm font-bold text-cyan-300 font-mono">{(recall * 100).toFixed(1)}%</div>
        </div>
        <div className="bg-slate-800/40 rounded p-2">
          <div className="text-[10px] text-slate-400 uppercase">F1-Score</div>
          <div className="text-sm font-bold text-violet-300 font-mono">{(f1 * 100).toFixed(1)}%</div>
        </div>
        <div className="bg-slate-800/40 rounded p-2">
          <div className="text-[10px] text-slate-400 uppercase">FPR</div>
          <div className="text-sm font-bold text-rose-300 font-mono">{(fpr * 100).toFixed(2)}%</div>
        </div>
      </div>
    </div>
  );
}
