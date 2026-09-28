import React from 'react';
import { AlertTriangle, Users, ShieldCheck, ShieldAlert } from 'lucide-react';

/**
 * StatCards Component
 * Fleet-wide metric summary cards for the Risk Dashboard.
 */
export default function StatCards({ 
  totalAlerts = 0, 
  criticalAlerts = 0, 
  monitoredUsers = 0, 
  quarantinedBaselines = 0,
  avgFleetRisk = 0
}) {
  const cards = [
    {
      title: 'Active High Threats',
      value: criticalAlerts,
      subtitle: `${totalAlerts} total unresolved alerts`,
      icon: ShieldAlert,
      color: 'rose',
      border: 'border-rose-500/30',
      bg: 'bg-rose-950/20',
      text: 'text-rose-400'
    },
    {
      title: 'Monitored Users',
      value: monitoredUsers,
      subtitle: 'Active accounts across fleet',
      icon: Users,
      color: 'cyan',
      border: 'border-cyan-500/30',
      bg: 'bg-cyan-950/20',
      text: 'text-cyan-400'
    },
    {
      title: 'Fleet Avg Risk Score',
      value: typeof avgFleetRisk === 'number' ? avgFleetRisk.toFixed(1) : avgFleetRisk,
      subtitle: 'Baseline normal: < 30.0',
      icon: AlertTriangle,
      color: avgFleetRisk >= 50 ? 'amber' : 'emerald',
      border: avgFleetRisk >= 50 ? 'border-amber-500/30' : 'border-emerald-500/30',
      bg: avgFleetRisk >= 50 ? 'bg-amber-950/20' : 'bg-emerald-950/20',
      text: avgFleetRisk >= 50 ? 'text-amber-400' : 'text-emerald-400'
    },
    {
      title: 'Quarantined Baselines',
      value: quarantinedBaselines,
      subtitle: 'Poisoning defense active',
      icon: ShieldCheck,
      color: 'violet',
      border: 'border-violet-500/30',
      bg: 'bg-violet-950/20',
      text: 'text-violet-400'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, idx) => {
        const IconComponent = card.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl border ${card.border} ${card.bg} backdrop-blur-sm shadow-md flex items-center justify-between transition-transform hover:-translate-y-0.5`}
          >
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                {card.title}
              </p>
              <h3 className={`text-2xl font-bold font-mono ${card.text}`}>
                {card.value}
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">
                {card.subtitle}
              </p>
            </div>
            <div className={`p-3 rounded-xl bg-slate-900/60 border ${card.border} ${card.text}`}>
              <IconComponent className="w-5 h-5" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
