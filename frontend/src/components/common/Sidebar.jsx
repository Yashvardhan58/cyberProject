import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Clock, 
  CheckSquare, 
  BarChart3, 
  Settings, 
  MessageSquare,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

const Sidebar = () => {
  const { 
    isSidebarOpen, 
    closeSidebar, 
    isSidebarCollapsed, 
    toggleSidebarCollapse 
  } = useApp();

  // Local hover state: expands slightly on hover when collapsed
  const [isHovered, setIsHovered] = useState(false);

  const navItems = [
    { name: 'Risk Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Incident Timeline', path: '/timeline', icon: Clock },
    { name: 'Analyst Feedback', path: '/feedback', icon: CheckSquare },
    { name: 'AI Threat Chat', path: '/chat', icon: MessageSquare },
    { name: 'Admin Metrics', path: '/admin/metrics', icon: BarChart3 },
  ];

  // Determine whether to display expanded contents (labels, header)
  // On desktop: if not collapsed, OR if collapsed and hovered ("on over it should open slightly")
  const isExpanded = !isSidebarCollapsed || isHovered;

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isSidebarOpen && (
        <div
          onClick={closeSidebar}
          className="fixed inset-0 bg-slate-950/70 backdrop-blur-xs z-40 md:hidden transition-opacity duration-300"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Aside */}
      <aside
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`
          bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between py-4 shadow-sm shrink-0 z-50
          transition-all duration-300 ease-in-out
          fixed inset-y-0 left-0 md:static md:inset-auto
          ${isSidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full md:translate-x-0'}
          ${isExpanded ? 'w-60' : 'w-16'}
        `}
      >
        <div className="flex flex-col flex-1">
          {/* Mobile Header / Desktop Collapse Header */}
          <div className="px-3 pb-3 mb-1 border-b border-slate-100 flex items-center justify-between">
            <div className={`text-[11px] font-bold uppercase tracking-wider text-slate-400 transition-opacity duration-200 ${isExpanded ? 'opacity-100' : 'opacity-0 md:hidden'}`}>
              Navigation
            </div>

            {/* Mobile Close Button */}
            <button
              onClick={closeSidebar}
              className="p-1 text-slate-400 hover:text-slate-700 rounded-lg md:hidden"
              title="Close Menu"
              aria-label="Close Menu"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Desktop Collapse Toggle Icon */}
            <button
              onClick={toggleSidebarCollapse}
              className={`hidden md:flex p-1 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-slate-100 transition-colors ${!isExpanded ? 'mx-auto' : ''}`}
              title={isSidebarCollapsed ? 'Pin Sidebar Open' : 'Collapse Sidebar'}
              aria-label={isSidebarCollapsed ? 'Pin Sidebar Open' : 'Collapse Sidebar'}
            >
              {isSidebarCollapsed ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1 px-2 flex-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  onClick={() => {
                    // Clicking menu item navigates and smoothly closes mobile drawer
                    closeSidebar();
                  }}
                  title={!isExpanded ? item.name : undefined}
                  className={({ isActive }) =>
                    `flex items-center rounded-lg text-sm transition-all duration-200 group relative ${
                      isExpanded ? 'gap-3 px-3 py-2.5' : 'justify-center p-2.5'
                    } ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600 shadow-sm'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 font-medium'
                    }`
                  }
                >
                  <Icon className="w-5 h-5 shrink-0 transition-transform duration-200 group-hover:scale-110" />
                  
                  {isExpanded && (
                    <span className="whitespace-nowrap transition-opacity duration-200">
                      {item.name}
                    </span>
                  )}

                  {/* Compact tooltip on collapsed desktop when not hovered */}
                  {!isExpanded && !isHovered && (
                    <div className="hidden md:group-hover:block absolute left-full ml-2 px-2.5 py-1 bg-slate-900 text-white text-xs font-medium rounded-md shadow-lg whitespace-nowrap z-50 pointer-events-none">
                      {item.name}
                    </div>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Footer / System Status */}
        <div className="px-3 py-3 border-t border-slate-200 mt-auto">
          <div className={`flex items-center text-xs text-slate-500 ${isExpanded ? 'gap-2' : 'justify-center'}`}>
            <Settings className="w-4 h-4 shrink-0" />
            {isExpanded && (
              <span className="truncate whitespace-nowrap">UEBA v1.0.0 (CERT r5.2)</span>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
