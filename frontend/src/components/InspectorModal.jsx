import React from 'react';
import { X, CheckCircle2, XCircle, Shield, Calculator, AlertTriangle, Cpu, DollarSign, FileText } from 'lucide-react';
import { DecisionBadge, RiskBadge } from './DecisionBadge';

export default function InspectorModal({ transaction, onClose }) {
  if (!transaction) return null;

  const dObj = transaction.decision_object || transaction;
  const checks = dObj.policy_checks || [];
  const prob = dObj.recovery_probability ?? transaction.recovery_probability ?? 0.0;
  const netErv = dObj.net_expected_recovery_value ?? transaction.net_expected_recovery_value ?? 0.0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto custom-scrollbar">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto glass-panel border border-slate-700/80 p-6 shadow-2xl custom-scrollbar animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-4 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Cpu className="w-6 h-6 stroke-[2]" />
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-display font-bold text-white">Transaction Inspector</h2>
                <span className="font-mono text-xs text-slate-400 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                  {dObj.transaction_id || transaction.transaction_id}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Deep-Dive Policy & Financial Yield Diagnostic Trace</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Top Diagnostic Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Decision</p>
            <DecisionBadge decision={dObj.decision || transaction.decision} />
          </div>
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Risk Classification</p>
            <RiskBadge riskLevel={dObj.risk_level || transaction.risk_level} />
          </div>
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">ML Probability (P_rec)</p>
            <p className="text-xl font-bold text-emerald-400 font-display">{(prob * 100).toFixed(1)}%</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Net Recovery Yield</p>
            <p className={`text-xl font-bold font-display ${netErv > 0 ? 'text-emerald-400' : 'text-slate-400'}`}>
              INR {netErv.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        {/* Main 2-Column Inspector */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          
          {/* Column 1: Financial ERV & Risk Synthesis */}
          <div className="space-y-6">
            
            {/* Financial ERV Breakdown Widget */}
            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="flex items-center space-x-2 mb-4">
                <Calculator className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-white">Financial ERV Breakdown</h3>
              </div>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                  <span className="text-slate-400">Transaction Amount</span>
                  <span className="font-semibold text-white">INR {(dObj.amount || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                  <span className="text-slate-400">Recovery Probability (P_rec)</span>
                  <span className="font-semibold text-emerald-400">{(prob * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                  <span className="text-slate-400">Gross Expected Recovery Value</span>
                  <span className="font-semibold text-white">INR {(dObj.expected_recovery_value || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-800/60">
                  <span className="text-slate-400">Operational Retry Cost</span>
                  <span className="font-semibold text-rose-400">- INR {(dObj.intervention_cost || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 text-sm font-bold bg-slate-800/40 px-3 rounded-lg border border-slate-700/50">
                  <span className="text-emerald-400">Net Expected Recovery Value</span>
                  <span className="text-emerald-400">INR {netErv.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
              </div>
            </div>

            {/* Explanation Rationale */}
            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800">
              <div className="flex items-center space-x-2 mb-3">
                <FileText className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-semibold text-white">Explainable Decision Reason</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3.5 rounded-lg border border-slate-800/80 font-mono">
                {dObj.reason || transaction.reason || 'No explanation trace.'}
              </p>
            </div>

          </div>

          {/* Column 2: Guardrails & Policy Execution Trace */}
          <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Shield className="w-4 h-4 text-violet-400" />
                <h3 className="text-sm font-semibold text-white">Deterministic Guardrails Trace</h3>
              </div>
              
              <div className="space-y-2.5">
                {checks.length > 0 ? (
                  checks.map((chk, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg border text-xs flex items-start justify-between space-x-3 ${
                        chk.passed
                          ? 'bg-slate-950/60 border-slate-800 text-slate-300'
                          : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                      }`}
                    >
                      <div className="flex items-start space-x-2.5">
                        {chk.passed ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                        )}
                        <div>
                          <p className="font-semibold text-white">{chk.rule_name || chk.rule_id}</p>
                          <p className="text-[11px] text-slate-400 mt-0.5">{chk.reason}</p>
                        </div>
                      </div>
                      {chk.forced_decision && (
                        <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 text-[10px] font-bold border border-rose-500/30 whitespace-nowrap">
                          FORCED {chk.forced_decision}
                        </span>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 italic">No policy guardrail checks recorded.</p>
                )}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800 text-right">
              <span className="text-[11px] text-slate-500 font-mono">Policy Version: {dObj.policy_version || 'v3.0.0-frozen'}</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
