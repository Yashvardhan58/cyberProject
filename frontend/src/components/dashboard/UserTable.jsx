import React from 'react';
import { Link } from 'react-router-dom';
import { User, ChevronRight, ShieldAlert, ShieldCheck } from 'lucide-react';
import { getRiskBadgeClass, getRiskLevel } from '../../utils/formatters';

/**
 * UserTable Component
 * User leaderboard sorted by risk score with quick profile routing.
 */
export default function UserTable({ users = [], isLoading = false }) {
  if (isLoading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-sm">
        <div className="inline-block w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-2" />
        <p>Loading enterprise user leaderboard...</p>
      </div>
    );
  }

  if (!users || users.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-sm">
        No monitored user profiles found.
      </div>
    );
  }

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-lg backdrop-blur-sm">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <User className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            User Risk Leaderboard
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {users.length} Active Accounts
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs min-w-[560px]">
          <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider border-b border-slate-800/80">
            <tr>
              <th className="py-3 px-4">User ID & Name</th>
              <th className="py-3 px-4">Role & Department</th>
              <th className="py-3 px-4">Current Risk</th>
              <th className="py-3 px-4">Baseline Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {users.map((user) => {
              const riskScore = user.current_risk_score ?? user.risk_score ?? 0;
              const isHighRisk = riskScore >= 60;
              const isQuarantined = user.baseline_quarantined || user.is_quarantined;
              const displayName = user.name || user.employee_id || user.user_id || `User #${user.id}`;
              const empId = user.employee_id || user.user_id || `ID-${user.id}`;
              const userIdentifier = user.id || user.employee_id || user.user_id;

              return (
                <tr 
                  key={user.id || user.employee_id || user.user_id} 
                  className="hover:bg-slate-800/30 transition-colors group"
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center font-mono font-bold text-slate-300 border border-slate-700 text-xs">
                        {displayName.charAt(0)}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors">
                          {displayName}
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono">
                          {empId} • {user.email || `${empId.toLowerCase()}@dti.com`}
                        </div>
                      </div>
                    </div>
                  </td>

                  <td className="py-3 px-4">
                    <div className="text-slate-200 font-medium">{user.role || 'Employee'}</div>
                    <div className="text-[11px] text-slate-400">{user.department || user.peer_group_name || 'General Fleet'}</div>
                  </td>

                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-mono font-bold ${getRiskBadgeClass(riskScore)}`}>
                        {typeof riskScore === 'number' ? riskScore.toFixed(1) : riskScore}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        ({getRiskLevel(riskScore)})
                      </span>
                    </div>
                  </td>

                  <td className="py-3 px-4">
                    {isQuarantined ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 border border-rose-500/40 text-[10px] font-semibold">
                        <ShieldAlert className="w-3 h-3" />
                        <span>QUARANTINED</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-950/50 text-emerald-300 border border-emerald-500/30 text-[10px]">
                        <ShieldCheck className="w-3 h-3" />
                        <span>Governed</span>
                      </span>
                    )}
                  </td>

                  <td className="py-3 px-4 text-right">
                    <Link
                      to={`/users/${userIdentifier}`}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-cyan-500 hover:text-slate-950 text-slate-300 transition-all font-medium text-[11px]"
                    >
                      <span>Analyze</span>
                      <ChevronRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
