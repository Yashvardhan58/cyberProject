import React from 'react';

/**
 * FeatureBar Component
 * Renders a horizontal bar representing feature contribution / SHAP impact.
 * Supports positive (red/orange: increased risk) and negative (blue/green: reduced risk) contributions.
 */
export default function FeatureBar({ 
  featureName, 
  shapValue = 0, 
  rawFeatureValue = null, 
  maxMagnitude = 1.0,
  unit = '' 
}) {
  const isPositive = shapValue >= 0;
  const absMagnitude = Math.abs(shapValue);
  const normalizedWidth = Math.min(100, Math.max(4, (absMagnitude / (maxMagnitude || 1.0)) * 100));

  // Friendly name formatting (e.g. logon_offhours_count -> Off-Hours Logons)
  const formatFeatureName = (name) => {
    if (!name) return 'Unknown Feature';
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div className="py-2 px-3 hover:bg-slate-800/40 rounded-lg transition-colors group">
      <div className="flex items-center justify-between text-xs mb-1">
        <div className="flex items-center space-x-2 truncate pr-2">
          <span className="font-medium text-slate-300 group-hover:text-cyan-400 transition-colors truncate">
            {formatFeatureName(featureName)}
          </span>
          {rawFeatureValue !== null && (
            <span className="text-slate-500 text-[10px] font-mono bg-slate-800 px-1.5 py-0.5 rounded">
              val: {typeof rawFeatureValue === 'number' ? rawFeatureValue.toFixed(2) : rawFeatureValue}{unit}
            </span>
          )}
        </div>
        <span className={`font-mono text-xs font-semibold ${isPositive ? 'text-rose-400' : 'text-emerald-400'}`}>
          {isPositive ? '+' : ''}{shapValue.toFixed(3)}
        </span>
      </div>

      <div className="relative h-2 bg-slate-900 rounded-full overflow-hidden flex items-center">
        {/* Center baseline indicator */}
        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-slate-700 z-10" />

        {isPositive ? (
          // Positive SHAP (pushes risk up -> spans right from center)
          <div className="w-1/2 flex justify-start ml-[50%]">
            <div 
              className="h-full bg-gradient-to-r from-rose-500 to-red-600 rounded-r-full transition-all duration-500 ease-out shadow-[0_0_8px_rgba(244,63,94,0.4)]"
              style={{ width: `${normalizedWidth}%` }}
              title={`+${shapValue.toFixed(4)} Risk Impact`}
            />
          </div>
        ) : (
          // Negative SHAP (pulls risk down -> spans left from center)
          <div className="w-1/2 flex justify-end mr-[50%]">
            <div 
              className="h-full bg-gradient-to-l from-emerald-500 to-teal-600 rounded-l-full transition-all duration-500 ease-out shadow-[0_0_8px_rgba(16,185,129,0.4)]"
              style={{ width: `${normalizedWidth}%` }}
              title={`${shapValue.toFixed(4)} Risk Impact`}
            />
          </div>
        )}
      </div>
    </div>
  );
}
