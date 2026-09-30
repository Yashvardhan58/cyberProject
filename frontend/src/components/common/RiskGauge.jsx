import React from 'react';
import { getScoreColor } from '../../utils/formatters';

const RiskGauge = ({ score = 0, size = 'lg', severity = null, title = null, subtitle = null }) => {
  const cleanScore = Math.min(Math.max(parseFloat(score) || 0, 0), 100);
  const color = getScoreColor(cleanScore);

  // Compute severity automatically if not provided
  const computedSeverity = severity || (
    cleanScore >= 80 ? 'CRITICAL' : cleanScore >= 60 ? 'HIGH' : cleanScore >= 30 ? 'MEDIUM' : 'LOW'
  );

  // Semicircle dimensions: support numeric size or standard presets
  const numericSize = typeof size === 'number' ? size : size === 'lg' ? 180 : size === 'sm' ? 110 : 140;
  const radius = Math.round(numericSize * 0.38);
  const strokeWidth = Math.round(numericSize * 0.08);
  const center = radius + strokeWidth;
  const svgWidth = center * 2;
  const svgHeight = center + 12;

  // Arc calculations (180 degrees semicircle)
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (cleanScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-3">
      {title && (
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
          {title}
        </span>
      )}
      {subtitle && (
        <span className="text-[10px] text-slate-400 font-mono mb-2">
          {subtitle}
        </span>
      )}

      <div className="relative flex items-center justify-center">
        <svg width={svgWidth} height={svgHeight} className="overflow-visible">
          {/* Background Arc (dark mode slate track) */}
          <path
            d={`M ${strokeWidth},${center} A ${radius},${radius} 0 0,1 ${svgWidth - strokeWidth},${center}`}
            fill="none"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          {/* Dynamic Progress Arc */}
          <path
            d={`M ${strokeWidth},${center} A ${radius},${radius} 0 0,1 ${svgWidth - strokeWidth},${center}`}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center Score Readout */}
        <div className="absolute bottom-1 flex flex-col items-center">
          <span
            className="font-mono font-bold leading-none text-3xl"
            style={{ color }}
          >
            {Math.round(cleanScore)}
          </span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mt-0.5">
            / 100
          </span>
        </div>
      </div>

      <div
        className="mt-2 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider border shadow-xs"
        style={{
          backgroundColor: `${color}15`,
          color: color,
          borderColor: `${color}40`,
        }}
      >
        {computedSeverity} Risk
      </div>
    </div>
  );
};

export default RiskGauge;
