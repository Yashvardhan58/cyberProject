import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine
} from 'recharts';

/**
 * Custom Tooltip for Risk Chart
 */
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const score = payload[0].value;
    const isHighRisk = score >= 60;

    return (
      <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs font-mono">
        <p className="text-slate-400 mb-1">{data.timestamp || label}</p>
        <p className={`font-bold text-sm ${isHighRisk ? 'text-rose-400' : 'text-cyan-400'}`}>
          Risk Score: {typeof score === 'number' ? score.toFixed(1) : score}
        </p>
        {data.xgb_prob !== undefined && (
          <p className="text-slate-400 text-[10px] mt-1">
            XGB: {(data.xgb_prob * 100).toFixed(1)}% | IF: {(data.if_score * 100).toFixed(1)}%
          </p>
        )}
        {data.is_anomaly && (
          <span className="inline-block mt-1 px-1.5 py-0.5 bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded text-[9px] font-semibold">
            ANOMALY DETECTED
          </span>
        )}
      </div>
    );
  }
  return null;
};

/**
 * RiskChart Component
 * Displays interactive 30-day (or arbitrary series) risk trajectory with anomaly markers and threshold reference lines.
 */
export default function RiskChart({
  data = [],
  threshold = 60,
  height = 260,
  showReferenceLine = true
}) {
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center bg-slate-900/50 border border-slate-800 rounded-xl text-slate-500 text-xs"
        style={{ height }}
      >
        No trajectory data available
      </div>
    );
  }

  // Format data points
  const formattedData = data.map((item, index) => ({
    ...item,
    formattedDate: item.timestamp 
      ? new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      : `Day ${index + 1}`,
    score: typeof item.risk_score === 'number' ? item.risk_score : (item.score || 0)
  }));

  return (
    <div className="w-full h-full bg-slate-900/60 border border-slate-800 rounded-xl p-4 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.6)]" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Risk Trajectory Timeline
          </span>
        </div>
        <div className="flex items-center space-x-3 text-[11px] text-slate-400">
          <span className="flex items-center space-x-1">
            <span className="w-3 h-0.5 bg-cyan-400 inline-block" />
            <span>Risk Score</span>
          </span>
          {showReferenceLine && (
            <span className="flex items-center space-x-1">
              <span className="w-3 h-0.5 bg-rose-500 inline-block border-dashed" />
              <span>Threshold ({threshold})</span>
            </span>
          )}
        </div>
      </div>

      <div style={{ width: '100%', height: height - 50 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis 
              dataKey="formattedDate" 
              stroke="#64748b" 
              fontSize={10}
              tickLine={false}
            />
            <YAxis 
              stroke="#64748b" 
              fontSize={10} 
              domain={[0, 100]} 
              ticks={[0, 25, 50, 75, 100]}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            {showReferenceLine && (
              <ReferenceLine 
                y={threshold} 
                stroke="#f43f5e" 
                strokeDasharray="4 4" 
                label={{ 
                  value: `Alert Threshold (${threshold})`, 
                  fill: '#f43f5e', 
                  fontSize: 10, 
                  position: 'insideTopRight' 
                }} 
              />
            )}
            <Line
              type="monotone"
              dataKey="score"
              stroke="#22d3ee"
              strokeWidth={2.5}
              dot={(props) => {
                const { cx, cy, payload } = props;
                if (payload.is_anomaly || payload.score >= threshold) {
                  return (
                    <circle
                      key={`dot-${props.index}`}
                      cx={cx}
                      cy={cy}
                      r={4.5}
                      fill="#f43f5e"
                      stroke="#ffe4e6"
                      strokeWidth={1.5}
                      className="animate-pulse"
                    />
                  );
                }
                return (
                  <circle
                    key={`dot-${props.index}`}
                    cx={cx}
                    cy={cy}
                    r={2.5}
                    fill="#22d3ee"
                    stroke="#0f172a"
                    strokeWidth={1}
                  />
                );
              }}
              activeDot={{ r: 6, fill: '#38bdf8', stroke: '#082f49', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
