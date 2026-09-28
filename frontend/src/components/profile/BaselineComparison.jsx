import React from 'react';
import { Users, TrendingUp, ShieldAlert, CheckCircle2 } from 'lucide-react';

/**
 * BaselineComparison Component
 * Visualizes user's behavioral deviation vs peer group baseline, 7-day drift trend, and quarantine status.
 */
export default function BaselineComparison({ baselineData = {}, peerGroupName = 'Engineering / Dev' }) {
  const userMean = baselineData.user_mean ?? 28.4;
  const peerMean = baselineData.peer_mean ?? 24.1;
  const driftScore = baselineData.drift_score ?? 0.12;
  const isQuarantined = baselineData.is_quarantined || driftScore >= 0.60;
  const trendDays = baselineData.trend_days ?? 7;
  const monotonicTrend = baselineData.monotonic_upward_days ?? 0;

  const deviationPct = peerMean > 0 ? (((userMean - peerMean) / peerMean) * 100) : 0;

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Users className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Baseline & Peer Comparison
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono bg-slate-800 px-2 py-0.5 rounded">
          Peer: {peerGroupName}
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        {/* User 30-Day Mean */}
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3">
          <div className="text-[11px] text-slate-400 uppercase font-medium">User 30-Day Mean</div>
          <div className="text-xl font-bold font-mono text-cyan-300 mt-0.5">
            {userMean.toFixed(1)}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Rolling feature baseline</div>
        </div>

        {/* Peer Mean & Deviation */}
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3">
          <div className="text-[11px] text-slate-400 uppercase font-medium">Peer Centroid Mean</div>
          <div className="text-xl font-bold font-mono text-slate-200 mt-0.5">
            {peerMean.toFixed(1)}
          </div>
          <div className={`text-[10px] mt-0.5 font-semibold ${deviationPct > 20 ? 'text-amber-400' : 'text-emerald-400'}`}>
            {deviationPct >= 0 ? `+${deviationPct.toFixed(1)}%` : `${deviationPct.toFixed(1)}%`} vs peer group
          </div>
        </div>

        {/* Drift Suspicion Score */}
        <div className={`border rounded-lg p-3 ${
          isQuarantined 
            ? 'bg-rose-950/30 border-rose-500/40 text-rose-300' 
            : 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
        }`}>
          <div className="text-[11px] uppercase font-medium">Drift Suspicion (D_drift)</div>
          <div className="text-xl font-bold font-mono mt-0.5">
            {driftScore.toFixed(3)}
          </div>
          <div className="text-[10px] mt-0.5">
            Threshold: 0.600 ({isQuarantined ? 'Quarantine Active' : 'Normal Update'})
          </div>
        </div>
      </div>

      {/* Governance Banner */}
      <div className={`p-3 rounded-lg border flex items-center justify-between text-xs ${
        isQuarantined 
          ? 'bg-rose-900/20 border-rose-600/40 text-rose-200' 
          : 'bg-slate-800/30 border-slate-700 text-slate-300'
      }`}>
        <div className="flex items-center space-x-2">
          {isQuarantined ? (
            <ShieldAlert className="w-4 h-4 text-rose-400 flex-shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          )}
          <span>
            {isQuarantined 
              ? `Baseline updates halted: ${monotonicTrend}-day monotonic escalation detected. Defending against baseline poisoning.`
              : `Baseline active: 7-day drift trend is within legitimate operational role tolerance.`}
          </span>
        </div>
      </div>
    </div>
  );
}
