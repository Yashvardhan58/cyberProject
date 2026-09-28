import React, { useState, useEffect } from 'react';
import FilterBar from '../components/timeline/FilterBar';
import EventItem from '../components/timeline/EventItem';
import { usersApi } from '../api/users';
import { alertsApi } from '../api/alerts';
import { Clock, ShieldAlert, Sparkles, Activity } from 'lucide-react';

/**
 * TimelineView Component
 * Chronological multi-channel forensic timeline view for security incident investigations.
 */
export default function TimelineView() {
  const [users, setUsers] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [channelFilter, setChannelFilter] = useState('ALL');
  const [onlyAnomalies, setOnlyAnomalies] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchTimelineData = async () => {
    setIsLoading(true);
    try {
      const [usersRes, alertsRes] = await Promise.all([
        usersApi.getAllUsers().catch(() => ({ data: [] })),
        alertsApi.getAllAlerts().catch(() => ({ data: [] }))
      ]);

      const rawUsers = Array.isArray(usersRes.data) ? usersRes.data : (usersRes.results || []);
      const rawAlerts = Array.isArray(alertsRes.data) ? alertsRes.data : (alertsRes.results || []);

      setUsers(rawUsers);

      // Build simulated forensic timeline nodes from alerts and user activities
      const generatedEvents = rawAlerts.flatMap((alert, idx) => {
        const baseDate = new Date(alert.timestamp || alert.created_at || Date.now());
        const uId = alert.employee_id || alert.user_id || alert.user_name || 'USR0001';
        const uName = alert.user_name || alert.employee_id || uId;
        const score = typeof alert.risk_score === 'number' ? alert.risk_score : (alert.risk_score_val || 75);

        return [
          {
            id: `evt-${idx}-1`,
            user_id: uId,
            user_name: uName,
            channel: 'logon',
            timestamp: new Date(baseDate.getTime() - 3600000 * 3).toISOString(),
            description: `Off-hours authentication from internal workstation (IP: 192.168.1.${10 + idx}).`,
            is_anomaly: score >= 60,
            risk_score: score * 0.7,
            raw_data: { auth_method: 'Kerberos', workstation: `WS-${100 + idx}`, off_hours: true }
          },
          {
            id: `evt-${idx}-2`,
            user_id: uId,
            user_name: uName,
            channel: 'usb',
            timestamp: new Date(baseDate.getTime() - 3600000 * 1.5).toISOString(),
            description: `Mass file transfer to unregistered removable storage drive (${idx % 2 === 0 ? 'SanDisk 64GB' : 'Kingston 128GB'}).`,
            is_anomaly: true,
            risk_score: score,
            raw_data: { device_serial: `USB-SN-${8800 + idx}`, bytes_transferred: 458000000, file_count: 142 }
          },
          {
            id: `evt-${idx}-3`,
            user_id: uId,
            user_name: uName,
            channel: 'email',
            timestamp: baseDate.toISOString(),
            description: `Outbound email dispatched to external personal webmail with encrypted archive attachment.`,
            is_anomaly: score >= 70,
            risk_score: score * 0.9,
            raw_data: { recipient: 'exfil_drop@external-mail.com', attachment_size: '34.8 MB', is_encrypted: true }
          },
          {
            id: `evt-${idx}-4`,
            user_id: uId,
            user_name: uName,
            channel: 'http',
            timestamp: new Date(baseDate.getTime() + 1800000).toISOString(),
            description: `HTTP POST request to unclassified external file-sharing host.`,
            is_anomaly: score >= 60,
            risk_score: score * 0.85,
            raw_data: { destination_domain: 'mega-upload-cloud.net', bytes_sent: 125000000, response_code: 200 }
          }
        ];
      });

      // Sort newest first
      generatedEvents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setEvents(generatedEvents);
    } catch (err) {
      console.error('Failed to load forensic events:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTimelineData();
  }, []);

  // Filter events safely without throwing TypeErrors
  const filteredEvents = events.filter((evt) => {
    const evtUser = String(evt.user_id || '').toLowerCase();
    const evtName = String(evt.user_name || '').toLowerCase();
    const selUser = String(selectedUser || '').toLowerCase();

    if (selectedUser && evtUser !== selUser && !evtName.includes(selUser) && !evtUser.includes(selUser)) return false;
    if (channelFilter !== 'ALL' && evt.channel !== channelFilter) return false;
    if (onlyAnomalies && !evt.is_anomaly) return false;
    if (searchQuery) {
      const q = String(searchQuery).toLowerCase();
      const matchDesc = String(evt.description || '').toLowerCase().includes(q);
      const matchUser = evtUser.includes(q) || evtName.includes(q);
      const matchChan = String(evt.channel || '').toLowerCase().includes(q);
      if (!matchDesc && !matchUser && !matchChan) return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl md:text-2xl font-bold text-slate-100 tracking-tight">
              Forensic Incident Timeline
            </h1>
            <span className="bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 text-[10px] font-mono px-2 py-0.5 rounded-full flex items-center gap-1">
              <Activity className="w-2.5 h-2.5" />
              Multi-Channel Audit
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Chronological audit stream across Authentication, Device/USB, Email, File, and Web telemetry.
          </p>
        </div>

        <div className="text-xs text-slate-400 font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg self-start sm:self-auto">
          Showing <strong className="text-cyan-400">{filteredEvents.length}</strong> events
        </div>
      </div>

      {/* Filter Controls */}
      <FilterBar
        channelFilter={channelFilter}
        onChannelChange={setChannelFilter}
        onlyAnomalies={onlyAnomalies}
        onToggleAnomalies={setOnlyAnomalies}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedUser={selectedUser}
        onUserChange={setSelectedUser}
        users={users}
        onRefresh={fetchTimelineData}
        isLoading={isLoading}
      />

      {/* Timeline Stream */}
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm shadow-xl">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            <div className="inline-block w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mb-2" />
            <p>Correlating forensic event streams...</p>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs">
            No forensic events match your current filter parameters.
          </div>
        ) : (
          <div className="pt-2">
            {filteredEvents.map((evt) => (
              <EventItem key={evt.id} event={evt} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
