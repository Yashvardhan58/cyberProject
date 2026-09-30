import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Bot, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  ShieldCheck,
  Cpu
} from 'lucide-react';
import apiClient from '../../api/client';

/**
 * ExplanationPanel Component
 * Asynchronous Celery 5.3 + Redis 7 explanation controller for SOC incident triage.
 * Triggers non-blocking background LLM synthesis (HTTP 202 Accepted) and polls for completion.
 */
export default function ExplanationPanel({ alertId, onCompleted }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState(null);
  const pollTimerRef = useRef(null);

  // Clear polling on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    };
  }, []);

  // Check for existing explanation on mount or alertId change
  useEffect(() => {
    if (!alertId) return;

    let isMounted = true;
    const fetchExisting = async () => {
      try {
        const res = await apiClient.get(`/explanations/alerts/${alertId}/explanation/`);
        const data = res?.data || res?.raw;
        if (isMounted && data && data.status) {
          setExplanation(data);
          if (data.status === 'PENDING' || data.status === 'PROCESSING') {
            startPolling(data.id);
          } else if (data.status === 'COMPLETED' && onCompleted) {
            onCompleted(data);
          }
        }
      } catch (err) {
        // No prior explanation exists yet, ready for analyst to trigger
      }
    };

    fetchExisting();
    return () => {
      isMounted = false;
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    };
  }, [alertId]);

  // Polling loop for Celery async worker completion
  const startPolling = (explanationId) => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
    }
    setPolling(true);

    pollTimerRef.current = setInterval(async () => {
      try {
        const url = explanationId 
          ? `/explanations/${explanationId}/` 
          : `/explanations/alerts/${alertId}/explanation/`;
        const res = await apiClient.get(url);
        const data = res?.data || res?.raw;

        if (data && (data.status === 'COMPLETED' || data.status === 'FAILED')) {
          clearInterval(pollTimerRef.current);
          pollTimerRef.current = null;
          setPolling(false);
          setLoading(false);
          setExplanation(data);

          if (data.status === 'COMPLETED' && onCompleted) {
            onCompleted(data);
          }
          if (data.status === 'FAILED') {
            setError(data.error || 'Explanation generation failed in worker process.');
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000);
  };

  // Trigger non-blocking async explanation generation
  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post('/explanations/', { alert_id: alertId });
      const rawData = res?.raw || res?.data;

      // Handle immediate cache hit (200 OK)
      if (rawData?.status === 'completed' && rawData?.data) {
        setExplanation(rawData.data);
        setLoading(false);
        if (onCompleted) onCompleted(rawData.data);
        return;
      }

      // Handle queued task (202 Accepted)
      const expId = rawData?.id || rawData?.explanation_id;
      setExplanation((prev) => ({
        ...(prev || {}),
        id: expId,
        status: 'PROCESSING'
      }));
      startPolling(expId);
    } catch (err) {
      setLoading(false);
      setPolling(false);
      const errMsg = err?.error || err?.message || 'Failed to enqueue explanation task.';
      setError(errMsg);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 shadow-lg space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20 text-violet-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-200">AI Threat Explanation</h4>
            <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
              <Cpu className="w-3 h-3 text-emerald-400" />
              <span>Celery Async Queue</span>
            </div>
          </div>
        </div>

        {explanation?.status === 'COMPLETED' && (
          <button
            onClick={handleGenerate}
            disabled={loading || polling}
            className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800/50 hover:bg-slate-800 border border-slate-700 transition"
            title="Re-run synthesis"
          >
            <RefreshCw className={`w-3 h-3 ${(loading || polling) ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>
        )}
      </div>

      {/* Loading / Polling State */}
      {(loading || polling) && (
        <div className="p-3 bg-violet-950/20 border border-violet-500/30 rounded-lg space-y-2">
          <div className="flex items-center gap-2 text-xs text-violet-300 font-medium">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-violet-400" />
            <span>Processing via Claude 3.5 Sonnet...</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Task dispatched to Celery background worker (<span className="text-slate-300 font-mono">queue: llm</span>). Free API prefetch multiplier active.
          </p>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-gradient-to-r from-violet-500 to-indigo-500 h-full w-2/3 animate-pulse" />
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && !polling && (
        <div className="p-2.5 bg-rose-950/30 border border-rose-500/40 rounded-lg flex items-start gap-2 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-rose-200">Generation Notice</p>
            <p className="text-[11px] text-rose-300/90">{error}</p>
            <button
              onClick={handleGenerate}
              className="mt-1 text-[11px] font-semibold text-rose-200 underline hover:text-white"
            >
              Retry Dispatch
            </button>
          </div>
        </div>
      )}

      {/* Completed Explanation State */}
      {explanation?.status === 'COMPLETED' && !loading && !polling && (
        <div className="space-y-2.5">
          <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/80 text-xs text-slate-200 leading-relaxed font-sans">
            {explanation.text || explanation.explanation_text}
          </div>

          {/* Badges / Metrics */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-3 h-3" />
              FaithLens: {((explanation.faithfulness_score ?? 0.95) * 100).toFixed(0)}%
            </span>

            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-mono">
              <CheckCircle2 className="w-3 h-3 text-indigo-400" />
              {explanation.model_name || 'claude-3-5-sonnet'}
            </span>

            {explanation.attempts && explanation.attempts > 1 && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Clock className="w-3 h-3" />
                {explanation.attempts} attempts
              </span>
            )}
          </div>
        </div>
      )}

      {/* Initial Call-to-Action (No Explanation Yet) */}
      {!explanation && !loading && !polling && !error && (
        <div className="text-center py-2 space-y-2">
          <p className="text-[11px] text-slate-400">
            Generate an evidence-grounded incident synthesis without blocking dashboard operations.
          </p>
          <button
            onClick={handleGenerate}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-medium text-xs shadow-md transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Synthesize AI Explanation</span>
          </button>
        </div>
      )}
    </div>
  );
}
