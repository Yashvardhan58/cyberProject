import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import DashboardView from './views/DashboardView';
import UserProfileView from './views/UserProfileView';
import TimelineView from './views/TimelineView';
import FeedbackView from './views/FeedbackView';
import ChatView from './views/ChatView';
import AdminMetricsView from './views/AdminMetricsView';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-slate-950/40 p-3 sm:p-4 md:p-6 transition-all duration-300">
          <Routes>
            <Route path="/" element={<DashboardView />} />
            <Route path="/users/:id" element={<UserProfileView />} />
            <Route path="/timeline" element={<TimelineView />} />
            <Route path="/feedback" element={<FeedbackView />} />
            <Route path="/chat" element={<ChatView />} />
            <Route path="/alerts/:id/chat" element={<ChatView />} />
            <Route path="/admin/metrics" element={<AdminMetricsView />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
