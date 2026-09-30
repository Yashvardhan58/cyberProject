import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import VerdictCard from '../components/feedback/VerdictCard';
import GovernanceOverride from '../components/feedback/GovernanceOverride';
import { alertsApi } from '../api/alerts';
import { usersApi } from '../api/users';
import { verdictsApi } from '../api/verdicts';
import { CheckCircle2, AlertOctagon, ShieldCheck, Clock, FileCheck, Filter } from 'lucide-react';
import { getRiskBadgeClass, formatDate } from '../utils/formatters';

import { useApp } from '../context/AppContext';

/**
 * FeedbackView Component
 * SOC Analyst adjudication dashboard for submitting TP/FP verdicts, quarantining baselines, and inspecting verdict logs.
 */
export default function FeedbackView() {
  const { refreshTrigger } = useApp() || {};
  const [searchParams] = useSearchParams();
  const queryAlertId = searchParams.get('alert_id');

  const [alerts, setAlerts] = useState([]);
  const [users, setUsers] = useState([]);
  const [pastVerdicts, setPastVerdicts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // [OPTIMIZATION]: Allow selective refresh (refreshUsers = false on verdict submission)
  // to avoid redundant user fleet fetch when only alert verdict state changed.
  const fetchFeedbackData = async (refreshUsers = true) => {
    setIsLoading(true);
    try {
      const promises = [
        alertsApi.getAllAlerts().catch(() => ({ data: [] })),
        verdictsApi.getVerdicts().catch(() => ({ data: [] }))
      ];

      if (refreshUsers || users.length === 0) {
        promises.push(usersApi.getAllUsers().catch(() => ({ data: [] })));
      }

      const results = await Promise.all(promises);
      const alertsRes = results[0];
      const verdictsRes = results[1];
      const usersRes = results[2];

      const fetchedAlerts = Array.isArray(alertsRes.data) ? alertsRes.data : (alertsRes.results || []);
      const fetchedVerdicts = Array.isArray(verdictsRes.data) ? verdictsRes.data : (verdictsRes.results || []);

      setAlerts(fetchedAlerts);
      setPastVerdicts(fetchedVerdicts);

      if (usersRes) {
        const fetchedUsers = Array.isArray(usersRes.data) ? usersRes.data : (usersRes.results || []);
        setUsers(fetchedUsers);
      }

      if (queryAlertId) {
        const found = fetchedAlerts.find(a => String(a.id || a.alert_id) === String(queryAlertId));
        if (found) setSelectedAlert(found);
        else if (fetchedAlerts.length > 0 && !selectedAlert) setSelectedAlert(fetchedAlerts[0]);
      } else if (fetchedAlerts.length > 0 && !selectedAlert) {
        setSelectedAlert(fetchedAlerts[0]);
      }
    } catch (err) {
      console.error('Failed to load feedback data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedbackData(true);
  }, [queryAlertId, refreshTrigger]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl md:text-2xl font-bold text-slate-100 tracking-tight">
              Analyst Adjudication & Baseline Governance
            </h1>
            <span className="bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 text-[10px] font-mono px-2 py-0.5 rounded-full flex items-center gap-1">
              <ShieldCheck className="w-2.5 h-2.5" />
              Human-in-the-Loop Feedback
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Validate true positives, discard false positives, and govern dynamic baseline update pipelines.
          </p>
        </div>
      </div>

      {/* Main Grid: Alert Selection + Adjudication Card + Governance Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Alert Queue (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 shadow-lg">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3 flex items-center justify-between">
              <span>Unresolved Alert Queue</span>
              <span className="bg-slate-800 text-slate-400 font-mono px-2 py-0.5 rounded text-[10px]">
                {alerts.length} Pending
              </span>
            </h3>

            <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
              {alerts.length === 0 ? (
                <p className="text-slate-500 text-xs text-center py-6">No alerts pending review.</p>
              ) : (
                alerts.map((a) => {
                  const aId = a.id || a.alert_id;
                  const isSelected = selectedAlert && (selectedAlert.id || selectedAlert.alert_id) === aId;
                  const uName = a.user_name || a.user?.name;
                  const uEmpId = a.employee_id || a.user_id || 'USR0001';
                  const userDisplay = uName ? `${uName} (${uEmpId})` : uEmpId;
                  const score = typeof a.risk_score === 'number' ? a.risk_score : (a.risk_score_val || 75.0);

                  return (
                    <div
                      key={aId}
                      onClick={() => setSelectedAlert(a)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-cyan-950/40 border-cyan-500/80 shadow-md ring-1 ring-cyan-500/40'
                          : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-xs text-slate-200">
                          {userDisplay}
                        </span>
                        <span className={`px-1.5 py-0.2 rounded font-mono text-[10px] font-bold ${getRiskBadgeClass(score)}`}>
                          Risk {score}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 line-clamp-1">
                        {a.title || a.summary || 'Behavioral anomaly detected'}
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Verdict Submission Card & Governance Overrides (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          <VerdictCard
            alert={selectedAlert}
            onVerdictSubmitted={fetchFeedbackData}
          />

          <GovernanceOverride
            users={users}
            onUpdated={fetchFeedbackData}
          />
        </div>
      </div>

      {/* Historical Verdicts Audit Log */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center space-x-2 mb-4">
          <FileCheck className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Recent Adjudication Verdict History
          </h3>
        </div>

        {pastVerdicts.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">
            No historical verdicts registered yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[520px]">
              <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Alert ID</th>
                  <th className="py-2.5 px-3">Verdict</th>
                  <th className="py-2.5 px-3">Analyst Notes</th>
                  <th className="py-2.5 px-3">Quarantined</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {pastVerdicts.map((v, i) => (
                  <tr key={i} className="hover:bg-slate-800/20">
                    <td className="py-2.5 px-3 font-mono font-bold text-slate-300">
                      #{v.alert_id || v.alert}
                    </td>
                    <td className="py-2.5 px-3">
                      {v.verdict === 'TRUE_POSITIVE' || v.verdict === 'TP' ? (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-500/30 text-[10px] font-semibold">
                          <AlertOctagon className="w-3 h-3" />
                          <span>True Positive</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 text-[10px] font-semibold">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>False Positive</span>
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-slate-300 max-w-md truncate">
                      {v.notes || 'Standard validation'}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px]">
                      {v.quarantine_baseline ? (
                        <span className="text-rose-400 font-bold">YES</span>
                      ) : (
                        <span className="text-slate-500">NO</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[10px]">
                      {formatDate(v.timestamp || v.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
