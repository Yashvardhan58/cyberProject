/**
 * Utility formatters for dates, severity colors, and risk metrics.
 */

export const getRiskLevel = (score) => {
  const s = parseFloat(score) || 0;
  if (s >= 80) return 'CRITICAL';
  if (s >= 60) return 'HIGH';
  if (s >= 40) return 'MEDIUM';
  return 'LOW';
};

export const getRiskBadgeClass = (score) => {
  const s = parseFloat(score) || 0;
  if (s >= 80) return 'bg-rose-950/80 text-rose-300 border-rose-500/50 shadow-[0_0_10px_rgba(244,63,94,0.3)]';
  if (s >= 60) return 'bg-orange-950/80 text-orange-300 border-orange-500/50 shadow-[0_0_10px_rgba(249,115,22,0.3)]';
  if (s >= 40) return 'bg-amber-950/80 text-amber-300 border-amber-500/50';
  return 'bg-emerald-950/80 text-emerald-300 border-emerald-500/50';
};

export const getSeverityBadgeStyle = (severity) => {
  const sev = (severity || '').toUpperCase();
  switch (sev) {
    case 'CRITICAL':
      return 'bg-rose-600 text-white border-rose-700';
    case 'HIGH':
      return 'bg-orange-600 text-white border-orange-700';
    case 'MEDIUM':
      return 'bg-amber-600 text-white border-amber-700';
    case 'LOW':
    default:
      return 'bg-emerald-600 text-white border-emerald-700';
  }
};

export const getSeveritySoftBadgeStyle = (severity) => {
  const sev = (severity || '').toUpperCase();
  switch (sev) {
    case 'CRITICAL':
      return 'bg-rose-950/60 text-rose-400 border-rose-500/30';
    case 'HIGH':
      return 'bg-orange-950/60 text-orange-400 border-orange-500/30';
    case 'MEDIUM':
      return 'bg-amber-950/60 text-amber-400 border-amber-500/30';
    case 'LOW':
    default:
      return 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30';
  }
};

export const getScoreColor = (score) => {
  const s = parseFloat(score) || 0;
  if (s >= 80) return '#f43f5e'; // Rose
  if (s >= 60) return '#f97316'; // Orange
  if (s >= 40) return '#f59e0b'; // Amber
  return '#10b981'; // Emerald
};

export const formatDate = (dateString) => {
  if (!dateString) return 'Recent';
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? dateString : date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

export const formatDateTime = (dateString) => {
  if (!dateString) return 'Recent';
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? dateString : date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export default {
  getRiskLevel,
  getRiskBadgeClass,
  getSeverityBadgeStyle,
  getSeveritySoftBadgeStyle,
  getScoreColor,
  formatDate,
  formatDateTime
};
