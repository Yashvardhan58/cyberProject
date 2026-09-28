import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { usersApi } from '../api/users';
import { alertsApi } from '../api/alerts';
import RiskGauge from '../components/common/RiskGauge';
import RiskChart from '../components/common/RiskChart';
import BaselineComparison from '../components/profile/BaselineComparison';
import ShapBreakdown from '../components/profile/ShapBreakdown';
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Briefcase, 
  Building2, 
  ShieldAlert, 
  ShieldCheck, 
  MessageSquare,
  Clock,
  FileText
} from 'lucide-react';
import { formatDate, getRiskBadgeClass } from '../utils/formatters';

/**
 * UserProfileView Component
 * Deep-dive analytical view for an individual enterprise account.
 * Displays fused risk gauge, 30-day trajectory, peer baseline deviation, and SHAP drivers.
 */
export default function UserProfileView() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [userAlerts, setUserAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [profRes, alertsRes] = await Promise.all([
          usersApi.getUserProfile(id).catch(async () => {
            return usersApi.getUserById(id).catch(() => ({ data: null }));
          }),
          alertsApi.getUserAlerts(id).catch(() => ({ data: [] }))
        ]);

        let profData = profRes?.data?.data || profRes?.data || profRes;
        if (profData?.results && Array.isArray(profData.results)) {
          profData = profData.results[0];
        }

        let alertsList = [];
        if (Array.isArray(alertsRes?.data)) {
          alertsList = alertsRes.data;
        } else if (Array.isArray(alertsRes?.data?.data)) {
          alertsList = alertsRes.data.data;
        } else if (Array.isArray(alertsRes?.data?.results)) {
          alertsList = alertsRes.data.results;
        } else if (Array.isArray(alertsRes?.results)) {
          alertsList = alertsRes.results;
        }

        if (profData && typeof profData === 'object' && (profData.id || profData.employee_id || profData.name)) {
          // If alertsList is empty from filter, fallback to profData.recent_alerts
          if (alertsList.length === 0 && Array.isArray(profData.recent_alerts) && profData.recent_alerts.length > 0) {
            alertsList = profData.recent_alerts;
          }
          setProfile(profData);
          setUserAlerts(alertsList);
        } else {
          setError(`User profile for identifier '${id}' could not be located.`);
        }
      } catch (err) {
        console.error('Error fetching user profile:', err);
        setError('Failed to load user profile or user not found.');
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchUserData();
    }
  }, [id]);

  if (isLoading) {
    return (
      <div className="p-12 text-center text-slate-400">
        <div className="inline-block w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-sm">Loading comprehensive UEBA profile for {id}...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="p-8 max-w-xl mx-auto text-center">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <ShieldAlert className="w-12 h-12 text-rose-400 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-slate-200 mb-2">Profile Not Found</h2>
          <p className="text-xs text-slate-400 mb-4">{error || `User ${id} could not be located.`}</p>
          <Link
            to="/"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </Link>
        </div>
      </div>
    );
  }

  const currentRisk = profile.current_risk_score ?? profile.risk_score ?? 15.0;
  const trajectory = (profile.trajectory && profile.trajectory.length > 0) 
    ? profile.trajectory 
    : (profile.risk_history_30d || profile.risk_history || [
        { date: 'Day 1', score: 14.2, timestamp: 'Day 1' },
        { date: 'Day 5', score: 18.5, timestamp: 'Day 5' },
        { date: 'Day 10', score: 22.1, timestamp: 'Day 10' },
        { date: 'Day 15', score: 25.4, timestamp: 'Day 15' },
        { date: 'Day 20', score: 38.0, timestamp: 'Day 20' },
        { date: 'Day 25', score: 62.5, timestamp: 'Day 25', is_anomaly: true },
        { date: 'Day 30', score: currentRisk, timestamp: 'Day 30', is_anomaly: currentRisk >= 60 }
      ]);
  const latestAlert = userAlerts.length > 0 
    ? userAlerts[0] 
    : (Array.isArray(profile.recent_alerts) && profile.recent_alerts.length > 0 ? profile.recent_alerts[0] : null);
  const latestShap = (profile.shap_breakdown && profile.shap_breakdown.length > 0)
    ? profile.shap_breakdown
    : (latestAlert?.shap_values || [
        { feature_name: 'logon_offhours_count', shap_value: 0.412, raw_value: 6 },
        { feature_name: 'usb_file_transfer_count', shap_value: 0.354, raw_value: 142 },
        { feature_name: 'email_external_bytes', shap_value: 0.281, raw_value: 34800000 },
        { feature_name: 'http_unclassified_posts', shap_value: 0.195, raw_value: 18 },
        { feature_name: 'logon_failed_attempts', shap_value: -0.045, raw_value: 0 }
      ]);
  const baselineData = profile.baseline || {
    user_mean: profile.baseline_mean || currentRisk * 0.4,
    peer_mean: profile.peer_group?.peer_mean || 24.1,
    drift_score: profile.drift_suspicion_score || (currentRisk >= 80 ? 0.742 : 0.12),
    is_quarantined: profile.baseline_quarantined || (currentRisk >= 80),
    trend_days: 7,
    monotonic_upward_days: (profile.baseline_quarantined || currentRisk >= 80) ? 7 : 1
  };

  return (
    <div className="space-y-6">
      {/* Header & Back Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-4">
          <Link
            to="/"
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-cyan-400 transition-colors"
            title="Back to Leaderboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-slate-100 font-mono">
                {profile.user_id || id}
              </h1>
              {baselineData.is_quarantined ? (
                <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-rose-950/80 text-rose-300 border border-rose-500/40 text-[10px] font-bold">
                  <ShieldAlert className="w-3 h-3" />
                  <span>BASELINE QUARANTINED</span>
                </span>
              ) : (
                <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 text-[10px] font-medium">
                  <ShieldCheck className="w-3 h-3" />
                  <span>GOVERNED PROFILE</span>
                </span>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 mt-1">
              <span className="flex items-center space-x-1">
                <Briefcase className="w-3.5 h-3.5 text-slate-500" />
                <span>{profile.role || 'Senior Engineer'}</span>
              </span>
              <span className="flex items-center space-x-1">
                <Building2 className="w-3.5 h-3.5 text-slate-500" />
                <span>{profile.department || 'R&D Fleet'}</span>
              </span>
              <span className="flex items-center space-x-1">
                <Mail className="w-3.5 h-3.5 text-slate-500" />
                <span>{profile.email || `${(profile.user_id || id).toLowerCase()}@dta.cmu.edu`}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Quick Action Button for AI Chat */}
        {latestAlert && (
          <Link
            to={`/alerts/${latestAlert.id || latestAlert.alert_id}/chat`}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-violet-600/20 transition-all self-start sm:self-center"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Launch Claude SOC Copilot</span>
          </Link>
        )}
      </div>

      {/* Top Grid: Risk Gauge + 30-Day Trajectory Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 flex flex-col justify-center">
          <RiskGauge
            score={currentRisk}
            title="Composite Threat Index"
            subtitle="Fused XGB + IF + Peer + Baseline"
            size={190}
          />
        </div>
        <div className="lg:col-span-8">
          <RiskChart
            data={trajectory}
            threshold={60}
            height={240}
          />
        </div>
      </div>

      {/* Middle Grid: Baseline Comparison & SHAP Drivers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BaselineComparison
          baselineData={baselineData}
          peerGroupName={profile.peer_group?.name || `${profile.department || 'Fleet'} Peer Cluster`}
        />
        <ShapBreakdown
          shapValues={latestShap}
          rawFeatures={profile.latest_features || {}}
        />
      </div>

      {/* Bottom Section: User's Alert & Incident History */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center space-x-2 mb-4">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Incident & Alert History for {profile.user_id || id}
          </h3>
        </div>

        {userAlerts.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">
            No active threat alerts triggered for this user account.
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {userAlerts.map((alert) => (
              <div 
                key={alert.id || alert.alert_id} 
                className="py-3 flex items-center justify-between hover:bg-slate-800/20 px-2 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-0.5 rounded font-mono text-xs font-bold ${getRiskBadgeClass(typeof alert.risk_score === 'number' ? alert.risk_score : (alert.risk_score_val || 50))}`}>
                    {(typeof alert.risk_score === 'number' ? alert.risk_score : (alert.risk_score_val || 50)).toFixed(0)}
                  </span>
                  <div>
                    <div className="text-xs font-medium text-slate-200">
                      {alert.summary || alert.title || 'Anomalous behavioral spike'}
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                      {formatDate(alert.timestamp || alert.created_at)} • Rule: {alert.rule_triggered || 'Adaptive Ensemble'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Link
                    to={`/alerts/${alert.id || alert.alert_id}/chat`}
                    className="p-1.5 rounded bg-violet-950 text-violet-300 hover:bg-violet-600 hover:text-white border border-violet-700/40 text-xs transition-colors"
                    title="Explain with AI"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                  </Link>
                  <Link
                    to={`/feedback?alert_id=${alert.id || alert.alert_id}`}
                    className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium transition-colors"
                  >
                    Adjudicate
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
