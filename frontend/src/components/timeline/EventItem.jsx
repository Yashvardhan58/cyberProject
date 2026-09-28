import React, { useState } from 'react';
import { 
  LogIn, 
  Usb, 
  Mail, 
  FileText, 
  Globe, 
  AlertTriangle, 
  ChevronDown, 
  ChevronUp, 
  Clock, 
  User 
} from 'lucide-react';
import { formatDate } from '../../utils/formatters';

/**
 * EventItem Component
 * Renders a forensic log node in the chronological audit timeline.
 */
export default function EventItem({ event = {} }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const eventType = (event.channel || event.event_type || 'logon').toLowerCase();
  const isAnomaly = event.is_anomaly || event.risk_score >= 60;

  // Domain-specific styling & icon selection
  const getChannelConfig = (channel) => {
    switch (channel) {
      case 'usb':
      case 'device':
        return {
          icon: Usb,
          color: 'text-amber-400',
          badge: 'bg-amber-950/60 text-amber-300 border-amber-500/30',
          label: 'USB / Removable Media'
        };
      case 'email':
        return {
          icon: Mail,
          color: 'text-sky-400',
          badge: 'bg-sky-950/60 text-sky-300 border-sky-500/30',
          label: 'Email Activity'
        };
      case 'file':
        return {
          icon: FileText,
          color: 'text-emerald-400',
          badge: 'bg-emerald-950/60 text-emerald-300 border-emerald-500/30',
          label: 'File Transfer'
        };
      case 'http':
      case 'web':
        return {
          icon: Globe,
          color: 'text-purple-400',
          badge: 'bg-purple-950/60 text-purple-300 border-purple-500/30',
          label: 'HTTP / Web Access'
        };
      case 'logon':
      default:
        return {
          icon: LogIn,
          color: 'text-cyan-400',
          badge: 'bg-cyan-950/60 text-cyan-300 border-cyan-500/30',
          label: 'Authentication / Logon'
        };
    }
  };

  const config = getChannelConfig(eventType);
  const IconComponent = config.icon;

  return (
    <div className="relative pl-6 pb-6 group">
      {/* Vertical timeline connector */}
      <div className="absolute left-2.5 top-3 bottom-0 w-0.5 bg-slate-800 group-last:hidden" />

      {/* Timeline Node Dot */}
      <div className={`absolute left-0 top-1.5 w-5 h-5 rounded-full flex items-center justify-center border shadow-sm ${
        isAnomaly 
          ? 'bg-rose-950 border-rose-500 text-rose-400 animate-pulse' 
          : 'bg-slate-900 border-slate-700 text-slate-400'
      }`}>
        <div className={`w-2 h-2 rounded-full ${isAnomaly ? 'bg-rose-500' : 'bg-slate-500'}`} />
      </div>

      {/* Event Card */}
      <div className={`p-4 rounded-xl border transition-all ${
        isAnomaly 
          ? 'bg-slate-900/90 border-rose-500/30 shadow-md shadow-rose-950/20' 
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
      }`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded border text-[10px] font-semibold ${config.badge}`}>
              <IconComponent className="w-3 h-3" />
              <span>{config.label}</span>
            </span>
            <span className="text-xs font-mono font-bold text-slate-200">
              {event.user_id || 'UNKNOWN_USER'}
            </span>
            {isAnomaly && (
              <span className="text-[9px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 px-1.5 py-0.2 rounded">
                ANOMALOUS
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono">
            <Clock className="w-3 h-3 text-slate-500" />
            <span>{formatDate(event.timestamp || event.date)}</span>
          </div>
        </div>

        {/* Summary Description */}
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          {event.description || event.activity || 'Standard behavioral audit event captured in time window.'}
        </p>

        {/* Metadata Details Toggle */}
        <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-1 text-[11px] text-slate-400 hover:text-cyan-400 transition-colors"
          >
            <span>{isExpanded ? 'Hide Raw Metadata' : 'View Raw Metadata'}</span>
            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          {event.risk_score !== undefined && (
            <span className="text-[10px] text-slate-400 font-mono">
              Risk Score: <strong className={isAnomaly ? 'text-rose-400' : 'text-slate-300'}>{event.risk_score.toFixed(1)}</strong>
            </span>
          )}
        </div>

        {/* Expanded Metadata JSON */}
        {isExpanded && (
          <div className="mt-3 p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto">
            <pre>{JSON.stringify(event.raw_data || event, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
