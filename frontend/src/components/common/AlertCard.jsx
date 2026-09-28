import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight, ShieldAlert } from 'lucide-react';
import { getSeverityBadgeStyle, formatDateTime } from '../../utils/formatters';

const AlertCard = ({ alert }) => {
  const navigate = useNavigate();

  const getBorderColor = (sev) => {
    switch ((sev || '').toUpperCase()) {
      case 'CRITICAL':
        return 'border-l-red-600';
      case 'HIGH':
        return 'border-l-orange-600';
      case 'MEDIUM':
        return 'border-l-amber-600';
      case 'LOW':
      default:
        return 'border-l-green-600';
    }
  };

  const handleCardClick = () => {
    navigate(`/alerts/${alert.id}/chat`);
  };

  return (
    <div
      onClick={handleCardClick}
      className={`bg-white rounded-lg border border-slate-200 border-l-4 ${getBorderColor(
        alert.severity
      )} p-4 hover:shadow-md transition-all cursor-pointer group`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${getSeverityBadgeStyle(
              alert.severity
            )}`}
          >
            {alert.severity}
          </span>
          <span className="font-mono text-xs font-semibold text-slate-800">
            Score: {alert.risk_score_val || alert.final_risk || 0}
          </span>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          {formatDateTime(alert.created_at)}
        </span>
      </div>

      <h4 className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1">
        {alert.title}
      </h4>

      <p className="text-xs text-slate-600 mt-1 line-clamp-2">
        {alert.description || alert.top_feature_summary || 'Anomalous deviation detected across multi-source logs.'}
      </p>

      <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-100 text-xs text-slate-500">
        <span className="font-medium text-slate-700">
          {alert.user_name || alert.employee_id}
        </span>
        <div className="flex items-center gap-1 text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          <span>Inspect</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
