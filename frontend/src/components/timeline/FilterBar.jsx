import React from 'react';
import { Search, Filter, ShieldAlert, CheckCircle2, RefreshCw } from 'lucide-react';

/**
 * FilterBar Component
 * Filtering controls for the Incident Timeline View.
 */
export default function FilterBar({
  channelFilter = 'ALL',
  onChannelChange = () => {},
  onlyAnomalies = false,
  onToggleAnomalies = () => {},
  searchQuery = '',
  onSearchChange = () => {},
  selectedUser = '',
  onUserChange = () => {},
  users = [],
  onRefresh = () => {},
  isLoading = false
}) {
  const channels = [
    { id: 'ALL', label: 'All Channels' },
    { id: 'logon', label: 'Logons' },
    { id: 'usb', label: 'Device / USB' },
    { id: 'email', label: 'Email' },
    { id: 'file', label: 'File Transfers' },
    { id: 'http', label: 'Web / HTTP' }
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 mb-6 shadow-md backdrop-blur-sm space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search forensic activity, filename, domain, or IP..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* User Select Dropdown */}
        <div className="w-full md:w-56">
          <select
            value={selectedUser}
            onChange={(e) => onUserChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
          >
            <option value="">All Monitored Users</option>
            {users.map((u) => {
              const val = u.employee_id || u.user_id || String(u.id);
              const label = u.name ? `${u.name} (${u.employee_id || u.user_id || u.role})` : `${u.employee_id || u.user_id || 'User'} (${u.role || 'Fleet'})`;
              return (
                <option key={val} value={val}>
                  {label}
                </option>
              );
            })}
          </select>
        </div>

        {/* Anomaly Toggle + Refresh Button */}
        <div className="flex items-center space-x-3 self-end md:self-auto">
          <button
            onClick={() => onToggleAnomalies(!onlyAnomalies)}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold border transition-all ${
              onlyAnomalies
                ? 'bg-rose-950/80 border-rose-500/50 text-rose-300 shadow-sm'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span>Anomalies Only</span>
          </button>

          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-400 hover:text-cyan-400 hover:border-slate-700 transition-colors disabled:opacity-50"
            title="Refresh Timeline Stream"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Channel Pills */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pt-2 border-t border-slate-800/80">
        {channels.map((ch) => (
          <button
            key={ch.id}
            onClick={() => onChannelChange(ch.id)}
            className={`text-[11px] font-medium px-3 py-1 rounded-md transition-all whitespace-nowrap ${
              channelFilter === ch.id
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {ch.label}
          </button>
        ))}
      </div>
    </div>
  );
}
