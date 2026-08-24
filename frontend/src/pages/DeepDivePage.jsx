import React, { useState } from 'react';
import { Cpu, Send, Shield, Calculator, CheckCircle2, XCircle, FileText } from 'lucide-react';
import { decideTransaction } from '../services/api';
import { DecisionBadge, RiskBadge } from '../components/DecisionBadge';

export default function DeepDivePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [form, setForm] = useState({
    transaction_id: 'tx_deepdive_101',
    amount: 15000,
    failure_code: 'TEMPORARY_GATEWAY_FAILURE',
    payment_method: 'UPI',
    predicted_recovery_probability: 0.85,
  });

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await decideTransaction({
        ...form,
        amount: Number(form.amount),
        predicted_recovery_probability: Number(form.predicted_recovery_probability),
      });
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* Top Input Form */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Cpu className="w-5 h-5 stroke-[2]" />
            </div>
            <div>
              <h3 className="text-base font-display font-bold text-white">Interactive Policy Engine Inspector</h3>
              <p className="text-xs text-slate-400">Evaluate custom failure payloads through frozen Phase 3 decision rules</p>
            </div>
          </div>

          <button
            onClick={handleEvaluate}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            <Send className="w-4 h-4 fill-slate-950" />
            <span>{loading ? 'Evaluating...' : 'Run Decision Engine'}</span>
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs pt-2">
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Transaction ID</label>
            <input
              type="text"
              value={form.transaction_id}
              onChange={(e) => setForm({ ...form, transaction_id: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Amount (INR)</label>
            <input
              type="number"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono focus:border-emerald-500"
            />
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Failure Scenario</label>
            <select
              value={form.failure_code}
              onChange={(e) => setForm({ ...form, failure_code: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-white text-[11px] focus:border-emerald-500"
            >
              <option value="TEMPORARY_GATEWAY_FAILURE">TEMPORARY_GATEWAY_FAILURE</option>
              <option value="GATEWAY_TIMEOUT">GATEWAY_TIMEOUT</option>
              <option value="INSUFFICIENT_FUNDS">INSUFFICIENT_FUNDS</option>
              <option value="EXPIRED_CARD">EXPIRED_CARD</option>
              <option value="INVALID_CREDENTIALS">INVALID_CREDENTIALS</option>
              <option value="AUTHENTICATION_FAILURE">AUTHENTICATION_FAILURE</option>
              <option value="BANK_DECLINED">BANK_DECLINED</option>
              <option value="FRAUD_RISK_BLOCK">FRAUD_RISK_BLOCK</option>
            </select>
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">Payment Method</label>
            <select
              value={form.payment_method}
              onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-white text-[11px] focus:border-emerald-500"
            >
              <option value="UPI">UPI</option>
              <option value="CREDIT_CARD">CREDIT_CARD</option>
              <option value="DEBIT_CARD">DEBIT_CARD</option>
              <option value="NET_BANKING">NET_BANKING</option>
            </select>
          </div>
          <div>
            <label className="text-slate-400 block mb-1 font-medium">P_rec Probability</label>
            <input
              type="number"
              step="0.05"
              min="0"
              max="1"
              value={form.predicted_recovery_probability}
              onChange={(e) => setForm({ ...form, predicted_recovery_probability: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-emerald-400 font-mono font-bold focus:border-emerald-500"
            />
          </div>
        </div>
      </div>

      {/* Result Diagnostic Output */}
      {result ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-300">
          
          {/* Diagnostic Metrics */}
          <div className="space-y-6">
            <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">Diagnostic Decision Result</h4>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">Intervention Action</span>
                  <DecisionBadge decision={result.decision} />
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">Risk Level</span>
                  <RiskBadge riskLevel={result.risk_level} />
                </div>
              </div>

              {/* Financial Math */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Gross Recovery Value (ERV):</span>
                  <span className="font-bold text-white font-mono">INR {result.expected_recovery_value.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Intervention Cost:</span>
                  <span className="font-bold text-rose-400 font-mono">- INR {result.intervention_cost}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-slate-800 text-sm font-bold">
                  <span className="text-emerald-400">Net Expected Recovery Value:</span>
                  <span className="text-emerald-400 font-mono">INR {result.net_expected_recovery_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                </div>
              </div>

              {/* Explanation */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-xs font-semibold text-cyan-400 block mb-1">Explanation Rationale:</span>
                <p className="text-xs text-slate-300 font-mono leading-relaxed">{result.reason}</p>
              </div>
            </div>
          </div>

          {/* Guardrail Checklist */}
          <div className="p-6 rounded-2xl glass-panel border border-slate-800">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400 mb-4 flex items-center space-x-2">
              <Shield className="w-4 h-4 text-violet-400" />
              <span>Policy Guardrails Trace</span>
            </h4>

            <div className="space-y-3">
              {result.policy_checks && result.policy_checks.map((chk, idx) => (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border text-xs flex items-start justify-between ${
                    chk.passed
                      ? 'bg-slate-950/80 border-slate-800 text-slate-300'
                      : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    {chk.passed ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className="font-bold text-white">{chk.rule_name || chk.rule_id}</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">{chk.reason}</p>
                    </div>
                  </div>
                  {chk.forced_decision && (
                    <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 text-[10px] font-bold border border-rose-500/30">
                      FORCED {chk.forced_decision}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

        </div>
      ) : (
        <div className="p-12 text-center text-slate-500 glass-panel border border-slate-800 rounded-2xl italic text-xs">
          Click <span className="text-emerald-400 font-semibold">'Run Decision Engine'</span> above to evaluate custom payload.
        </div>
      )}

    </div>
  );
}
