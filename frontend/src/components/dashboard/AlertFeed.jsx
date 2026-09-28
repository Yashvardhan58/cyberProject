import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Filter, ArrowRight, MessageSquare, CheckCircle } from 'lucide-react';
import { getRiskBadgeClass, formatDate } from '../../utils/formatters';

/**
 * AlertFeed Component
 * Filterable live alert feed displaying security anomaly incidents.
 */
export default function AlertFeed({ alerts = [], isLoading = false }) {
  const [filter, setFilter] = useState('ALL');

  const filteredAlerts = alerts.filter((alert) => {
    const score = typeof alert.risk_score === 'number' ? alert.risk_score : (alert.risk_score_val || 0);
    const sev = (alert.severity || '').toUpperCase();
    if (filter === 'ALL') return true;
    if (filter === 'CRITICAL') return sev === 'CRITICAL' || score >= 80;
    if (filter === 'HIGH') return sev === 'HIGH' || (score >= 60 && score < 80);
    if (filter === 'MEDIUM') return sev === 'MEDIUM' || (score >= 30 && score < 60);
    if (filter === 'LOW') return sev === 'LOW' || score < 30;
    return true;
  });

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-lg backdrop-blur-sm">
      {/* Header & Filter Controls */}
      <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-rose-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Live Threat Stream
          </h3>
          <span className="text-xs bg-rose-950/60 text-rose-300 border border-rose-500/30 px-2 py-0.5 rounded-full font-mono">
            {filteredAlerts.length}
          </span>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilter(lvl)}
              className={`text-[10px] font-semibold px-2 py-1 rounded-md transition-all ${
                filter === lvl
                  ? 'bg-cyan-500 text-slate-950 shadow-md font-bold'
                  : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Feed Content */}
      <div className="divide-y divide-slate-800/60 max-h-[480px] overflow-y-auto">
        {isLoading ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            <div className="inline-block w-5 h-5 border-2 border-rose-400 border-t-transparent rounded-full animate-spin mb-2" />
            <p>Loading threat stream...</p>
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No threat incidents match the selected filter.
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const score = typeof alert.risk_score === 'number' ? alert.risk_score : (alert.risk_score_val || 0);
            const topFeature = alert.top_contributing_feature || alert.top_feature_summary || alert.primary_indicator || 'Anomalous behavioral spike';
            const alertId = alert.id || alert.alert_id;
            const userDisplay = alert.user_name || alert.employee_id || alert.user_id || 'Security Account';
            const userEmpId = alert.employee_id || alert.user_id || `ID-${alert.user_id}`;
            const userIdentifier = alert.employee_id || alert.user_id || alert.user?.id || alertId;

            return (
              <div 
                key={alertId} 
                className="p-4 hover:bg-slate-800/30 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
              >
                {/* Left info */}
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">
                    <span className={`inline-flex items-center justify-center w-9 h-9 rounded-lg font-mono font-bold text-xs border ${getRiskBadgeClass(score)}`}>
                      {typeof score === 'number' ? score.toFixed(0) : score}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <Link 
                        to={`/users/${userIdentifier}`} 
                        className="font-bold text-slate-200 hover:text-cyan-400 transition-colors text-xs font-mono"
                      >
                        {userDisplay} ({userEmpId})
                      </Link>
                      <span className="text-slate-500 text-[10px]">•</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {formatDate(alert.timestamp || alert.created_at)}
                      </span>
                      {alert.is_quarantined && (
                        <span className="text-[9px] bg-violet-950/80 text-violet-300 border border-violet-500/40 px-1.5 py-0.2 rounded font-semibold">
                          QUARANTINED
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 mt-0.5 font-medium line-clamp-1">
                      {alert.title || alert.summary || topFeature}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5 font-mono">
                      Rule: {alert.rule_triggered || 'Adaptive Ensemble Fusion'}
                    </p>
                  </div>
                </div>

                {/* Right Action buttons */}
                <div className="flex items-center space-x-2 self-end sm:self-center">
                  <Link
                    to={`/alerts/${alertId}/chat`}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-violet-900/40 hover:bg-violet-600 text-violet-200 border border-violet-700/50 hover:border-violet-400 text-[11px] font-medium transition-colors shadow-sm"
                    title="Ask Claude 3.5 Sonnet to explain this alert"
                  >
                    <MessageSquare className="w-3 h-3" />
                    <span>AI Copilot</span>
                  </Link>

                  <Link
                    to={`/feedback?alert_id=${alertId}`}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-600 hover:text-white text-slate-300 border border-slate-700 text-[11px] font-medium transition-colors"
                    title="Adjudicate alert as True Positive / False Positive"
                  >
                    <CheckCircle className="w-3 h-3" />
                    <span>Verdict</span>
                  </Link>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
