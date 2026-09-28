import React, { useEffect, useState } from 'react';
import StatCards from '../components/dashboard/StatCards';
import UserTable from '../components/dashboard/UserTable';
import AlertFeed from '../components/dashboard/AlertFeed';
import { usersApi } from '../api/users';
import { alertsApi } from '../api/alerts';
import { metricsApi } from '../api/metrics';
import { RefreshCw, ShieldAlert, Sparkles } from 'lucide-react';

/**
 * DashboardView Component
 * Main enterprise SOC landing page for real-time insider threat and account compromise detection.
 */
export default function DashboardView() {
  const [users, setUsers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [summaryMetrics, setSummaryMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [usersRes, alertsRes, metricsRes] = await Promise.all([
        usersApi.getAllUsers().catch(() => ({ data: [] })),
        alertsApi.getAllAlerts().catch(() => ({ data: [] })),
        metricsApi.getSummaryMetrics().catch(() => ({ data: {} }))
      ]);

      const usersList = Array.isArray(usersRes.data) ? usersRes.data : (usersRes.results || []);
      const alertsList = Array.isArray(alertsRes.data) ? alertsRes.data : (alertsRes.results || []);

      setUsers(usersList);
      setAlerts(alertsList);
      setSummaryMetrics(metricsRes.data || {});
      setLastRefreshed(new Date());
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Compute live KPIs
  const criticalCount = alerts.filter(a => (a.risk_score >= 80 || a.severity === 'CRITICAL')).length;
  const quarantinedCount = users.filter(u => u.baseline_quarantined || u.is_quarantined).length;
  const avgRisk = users.length > 0 
    ? users.reduce((acc, u) => acc + (u.current_risk_score || u.risk_score || 0), 0) / users.length 
    : 0;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl md:text-2xl font-bold text-slate-100 tracking-tight">
              Adaptive UEBA SOC Command Center
            </h1>
            <span className="bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 text-[10px] font-mono px-2 py-0.5 rounded-full flex items-center gap-1">
              <Sparkles className="w-2.5 h-2.5" />
              CERT r5.2
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Contamination-Resistant Baseline Governance & Multi-Model Threat Ensemble
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-[11px] text-slate-500 font-mono">
            Synced {lastRefreshed.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-400 text-xs font-medium border border-slate-700 transition-colors disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Fleet KPI Stat Cards */}
      <StatCards
        totalAlerts={alerts.length}
        criticalAlerts={criticalCount}
        monitoredUsers={users.length}
        quarantinedBaselines={quarantinedCount}
        avgFleetRisk={avgRisk}
      />

      {/* Main Grid: User Leaderboard + Live Threat Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <UserTable users={users} isLoading={isLoading} />
        </div>
        <div className="lg:col-span-5">
          <AlertFeed alerts={alerts} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
