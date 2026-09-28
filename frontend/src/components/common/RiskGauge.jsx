import React from 'react';
import { getScoreColor } from '../../utils/formatters';

const RiskGauge = ({ score = 0, size = 'md', severity = 'LOW' }) => {
  const cleanScore = Math.min(Math.max(parseFloat(score) || 0, 0), 100);
  const color = getScoreColor(cleanScore);

  // Semicircle dimensions
  const strokeWidth = size === 'lg' ? 14 : size === 'sm' ? 8 : 10;
  const radius = size === 'lg' ? 70 : size === 'sm' ? 40 : 55;
  const center = radius + strokeWidth;
  const svgWidth = center * 2;
  const svgHeight = center + 10;

  // Arc calculations (180 degrees semicircle)
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (cleanScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative flex items-center justify-center">
        <svg width={svgWidth} height={svgHeight} className="overflow-visible">
          {/* Background Arc */}
          <path
            d={`M ${strokeWidth},${center} A ${radius},${radius} 0 0,1 ${svgWidth - strokeWidth},${center}`}
            fill="none"
            stroke="#E2E8F0"
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
            className={`font-mono font-bold leading-none ${
              size === 'lg' ? 'text-3xl' : size === 'sm' ? 'text-lg' : 'text-2xl'
            }`}
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
        className="mt-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider border shadow-xs"
        style={{
          backgroundColor: `${color}15`,
          color: color,
          borderColor: `${color}40`,
        }}
      >
        {severity} Risk
      </div>
    </div>
  );
};

export default RiskGauge;
