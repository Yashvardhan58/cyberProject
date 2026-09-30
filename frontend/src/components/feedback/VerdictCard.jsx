import React, { useState } from 'react';
import { CheckCircle2, XCircle, AlertOctagon, Send, ShieldCheck, ShieldAlert } from 'lucide-react';
import { verdictsApi } from '../../api/verdicts';

/**
 * VerdictCard Component
 * Interactive form allowing SOC analysts to adjudicate alerts as True Positive or False Positive.
 */
export default function VerdictCard({ 
  alert = null, 
  onVerdictSubmitted = () => {} 
}) {
  const [verdict, setVerdict] = useState('TP'); // 'TP' or 'FP'
  const [analystNotes, setAnalystNotes] = useState('');
  const [quarantineBaseline, setQuarantineBaseline] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  if (!alert) {
    return (
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-8 text-center text-slate-500 text-xs">
        Select an alert from the queue to adjudicate and submit analyst verdict.
      </div>
    );
  }

  const alertId = alert.id || alert.alert_id;
  const userName = alert.user_name || alert.user?.name;
  const userEmpId = alert.employee_id || alert.user_id || alert.user?.employee_id || 'USR0001';
  const userDisplay = userName ? `${userName} (${userEmpId})` : userEmpId;
  const score = alert.final_risk_score ?? alert.risk_score_val ?? (typeof alert.risk_score === 'number' ? alert.risk_score : alert.risk_score?.final_risk) ?? 85.0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await verdictsApi.submitVerdict(alertId, {
        verdict: verdict === 'TP' ? 'TP' : 'FP',
        analyst_note: analystNotes || (verdict === 'TP' ? 'Confirmed malicious behavioral spike' : 'Authorized operational role drift'),
        analyst_name: 'SOC Analyst L2',
        quarantine_baseline: verdict === 'TP' ? quarantineBaseline : false,
        // Legacy keys kept for backwards compatibility:
        notes: analystNotes || (verdict === 'TP' ? 'Confirmed malicious behavioral spike' : 'Authorized operational role drift'),
        analyst_id: 'ANALYST_SOC_L2'
      });

      setSubmitSuccess(true);
      setTimeout(() => {
        setSubmitSuccess(false);
        onVerdictSubmitted();
      }, 1500);
    } catch (err) {
      console.error('Failed to submit verdict:', err);
      alert('Error submitting verdict. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            Adjudicate Alert: #{alertId}
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Subject Account: <strong className="text-cyan-400">{userDisplay}</strong> | Risk Score: <strong className="text-rose-400">{score}</strong>
          </p>
        </div>
        <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-1 rounded">
          SOC L2 Review
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* TP / FP Toggle Buttons */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            Analyst Classification
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => {
                setVerdict('TP');
                setQuarantineBaseline(true);
              }}
              className={`p-3 rounded-xl border flex items-center justify-center space-x-2 text-xs font-bold transition-all ${
                verdict === 'TP'
                  ? 'bg-rose-950/80 border-rose-500 text-rose-300 shadow-md shadow-rose-950/40 ring-1 ring-rose-500'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <AlertOctagon className="w-4 h-4 text-rose-400" />
              <span>True Positive (Malicious)</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setVerdict('FP');
                setQuarantineBaseline(false);
              }}
              className={`p-3 rounded-xl border flex items-center justify-center space-x-2 text-xs font-bold transition-all ${
                verdict === 'FP'
                  ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300 shadow-md shadow-emerald-950/40 ring-1 ring-emerald-500'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>False Positive (Benign Drift)</span>
            </button>
          </div>
        </div>

        {/* Baseline Quarantine Option for TP */}
        {verdict === 'TP' && (
          <div className="p-3 bg-rose-950/30 border border-rose-500/30 rounded-lg flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <div>
                <div className="font-semibold text-rose-300">Quarantine User Baseline</div>
                <div className="text-[10px] text-slate-400">Prevent malicious telemetry from poisoning normal behavioral profile</div>
              </div>
            </div>
            <input
              type="checkbox"
              checked={quarantineBaseline}
              onChange={(e) => setQuarantineBaseline(e.target.checked)}
              className="w-4 h-4 rounded text-rose-600 bg-slate-900 border-slate-700 focus:ring-rose-500"
            />
          </div>
        )}

        {/* Notes Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
            Forensic Findings & Notes
          </label>
          <textarea
            rows={3}
            value={analystNotes}
            onChange={(e) => setAnalystNotes(e.target.value)}
            placeholder={
              verdict === 'TP'
                ? 'E.g., Confirmed mass exfiltration via USB device following off-hours logon.'
                : 'E.g., User confirmed approved cross-departmental project migration.'
            }
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting || submitSuccess}
          className={`w-full py-2.5 rounded-lg text-xs font-bold uppercase tracking-wider flex items-center justify-center space-x-2 transition-all ${
            submitSuccess
              ? 'bg-emerald-600 text-white'
              : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 disabled:opacity-50'
          }`}
        >
          {submitSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4" />
              <span>Verdict Registered & Baseline Synced</span>
            </>
          ) : isSubmitting ? (
            <span>Recording Verdict...</span>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Commit Adjudication Verdict</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
