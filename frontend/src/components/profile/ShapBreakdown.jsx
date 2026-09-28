import React from 'react';
import FeatureBar from '../common/FeatureBar';
import { Sparkles, Info } from 'lucide-react';

/**
 * ShapBreakdown Component
 * Displays the top-5 feature attributions computed by TreeSHAP for explainable AI triage.
 */
export default function ShapBreakdown({ shapValues = [], rawFeatures = {} }) {
  if (!shapValues || shapValues.length === 0) {
    return (
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center space-x-2 mb-3">
          <Sparkles className="w-4 h-4 text-violet-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            SHAP Behavioral Attributions
          </h3>
        </div>
        <p className="text-xs text-slate-500 py-4 text-center">
          No feature attribution data recorded for this user window.
        </p>
      </div>
    );
  }

  // Find max magnitude for normalization
  const maxMagnitude = Math.max(...shapValues.map(s => Math.abs(s.shap_value || s.value || 0)), 0.1);

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-violet-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Top-5 SHAP Risk Drivers (TreeSHAP)
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
          <span className="text-rose-400 font-bold">+ Increases Risk</span>
          <span>|</span>
          <span className="text-emerald-400 font-bold">- Decreases Risk</span>
        </div>
      </div>

      <div className="space-y-1">
        {shapValues.map((item, idx) => {
          const featureName = item.feature_name || item.feature || `Feature ${idx + 1}`;
          const value = item.shap_value ?? item.value ?? 0;
          const rawVal = rawFeatures[featureName] ?? item.raw_value ?? null;

          return (
            <FeatureBar
              key={idx}
              featureName={featureName}
              shapValue={value}
              rawFeatureValue={rawVal}
              maxMagnitude={maxMagnitude}
            />
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800 flex items-start space-x-2 text-[11px] text-slate-400">
        <Info className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
        <span>
          Attributions computed via post-hoc TreeSHAP explainer against XGBoost and Isolation Forest anomaly ensembles.
        </span>
      </div>
    </div>
  );
}
