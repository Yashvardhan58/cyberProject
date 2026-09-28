import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Clock, CheckSquare, BarChart3, Settings, MessageSquare } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Risk Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Incident Timeline', path: '/timeline', icon: Clock },
    { name: 'Analyst Feedback', path: '/feedback', icon: CheckSquare },
    { name: 'AI Threat Chat', path: '/chat', icon: MessageSquare },
    { name: 'Admin Metrics', path: '/admin/metrics', icon: BarChart3 },
  ];

  return (
    <aside className="w-60 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between py-4 shadow-sm shrink-0">
      <nav className="space-y-1 px-3">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-medium'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer / System Status */}
      <div className="px-4 py-3 border-t border-slate-200 mt-auto">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Settings className="w-3.5 h-3.5" />
          <span>UEBA v1.0.0 (CERT r5.2)</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
