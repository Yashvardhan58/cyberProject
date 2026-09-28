import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Sliders, RefreshCw, Lock, Unlock } from 'lucide-react';
import { baselinesApi } from '../../api/baselines';

/**
 * GovernanceOverride Component
 * Controls for manually overriding baseline quarantine states and fine-tuning drift sensitivity.
 */
export default function GovernanceOverride({ users = [], onUpdated = () => {} }) {
  const [selectedUser, setSelectedUser] = useState('');
  const [threshold, setThreshold] = useState(0.60);
  const [isSaving, setIsSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  const currentUser = users.find(u => (u.user_id || u.id) === selectedUser);
  const isQuarantined = currentUser?.baseline_quarantined || false;

  const handleToggleQuarantine = async () => {
    if (!selectedUser) return;
    setIsSaving(true);
    setStatusMsg('');
    try {
      await baselinesApi.overrideQuarantine(selectedUser, {
        quarantined: !isQuarantined,
        reason: isQuarantined ? 'Manual SOC unquarantine override' : 'Manual SOC containment'
      });
      setStatusMsg(`Baseline state updated for ${selectedUser}.`);
      onUpdated();
    } catch (err) {
      console.error('Failed to override baseline:', err);
      setStatusMsg('Error updating baseline status.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Sliders className="w-4 h-4 text-violet-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Baseline Governance Controls
          </h3>
        </div>
        <span className="text-[10px] font-mono text-violet-300 bg-violet-950/60 border border-violet-500/30 px-2 py-0.5 rounded">
          Admin Override
        </span>
      </div>

      {/* Target User Selector */}
      <div>
        <label className="block text-xs text-slate-300 mb-1 font-medium">
          Select Monitored User Account
        </label>
        <select
          value={selectedUser}
          onChange={(e) => setSelectedUser(e.target.value)}
          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-violet-500"
        >
          <option value="">Choose User...</option>
          {users.map((u) => {
            const val = u.employee_id || u.user_id || String(u.id);
            const label = u.name ? `${u.name} (${u.employee_id || u.user_id})` : (u.employee_id || u.user_id || `User #${u.id}`);
            return (
              <option key={val} value={val}>
                {label} - {u.role || 'User'} ({u.baseline_quarantined ? 'QUARANTINED' : 'Active'})
              </option>
            );
          })}
        </select>
      </div>

      {/* Status & Toggle */}
      {currentUser && (
        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Current Baseline Status:</span>
            {isQuarantined ? (
              <span className="text-rose-400 font-bold flex items-center gap-1 font-mono">
                <Lock className="w-3.5 h-3.5" /> QUARANTINED (Updates Halted)
              </span>
            ) : (
              <span className="text-emerald-400 font-bold flex items-center gap-1 font-mono">
                <Unlock className="w-3.5 h-3.5" /> NORMAL (Adaptive Updating)
              </span>
            )}
          </div>

          <button
            onClick={handleToggleQuarantine}
            disabled={isSaving}
            className={`w-full py-2 rounded-lg text-xs font-semibold flex items-center justify-center space-x-2 border transition-all ${
              isQuarantined
                ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300 hover:bg-emerald-900/60'
                : 'bg-rose-950/60 border-rose-500/40 text-rose-300 hover:bg-rose-900/60'
            }`}
          >
            {isQuarantined ? (
              <>
                <Unlock className="w-3.5 h-3.5" />
                <span>Unfreeze & Resume Baseline Adaptation</span>
              </>
            ) : (
              <>
                <Lock className="w-3.5 h-3.5" />
                <span>Lock & Quarantine Baseline Immediately</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Sensitivity Threshold Slider */}
      <div>
        <div className="flex items-center justify-between text-xs text-slate-300 mb-1">
          <span>Drift Suspicion Sensitivity (&tau;<sub>drift</sub>):</span>
          <span className="font-mono font-bold text-violet-400">{threshold.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min="0.30"
          max="0.90"
          step="0.05"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="w-full accent-violet-500 cursor-pointer"
        />
        <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
          <span>0.30 (Aggressive)</span>
          <span>0.60 (Optimal Default)</span>
          <span>0.90 (Permissive)</span>
        </div>
      </div>

      {statusMsg && (
        <p className="text-[11px] text-cyan-400 font-mono text-center">{statusMsg}</p>
      )}
    </div>
  );
}
