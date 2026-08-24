import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, RefreshCw, Lock } from 'lucide-react';
import { verifyAuditTrail } from '../services/api';

export default function AuditVerifierWidget() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleVerify = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await verifyAuditTrail();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-2xl glass-panel border border-slate-800 relative overflow-hidden">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20">
            <Lock className="w-6 h-6 stroke-[2]" />
          </div>
          <div>
            <h3 className="text-lg font-display font-bold text-white">Cryptographic Audit Chain Verifier</h3>
            <p className="text-xs text-slate-400">SHA-256 Immutable Append-Only Ledger Integrity Verification</p>
          </div>
        </div>

        <button
          onClick={handleVerify}
          disabled={loading}
          className="flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-violet-600/20 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Verifying SHA-256 Chain...' : 'Verify Hash Chain Integrity'}</span>
        </button>
      </div>

      {/* Audit Status Display */}
      {result && (
        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {result.is_valid ? (
                <ShieldCheck className="w-8 h-8 text-emerald-400" />
              ) : (
                <ShieldAlert className="w-8 h-8 text-rose-500" />
              )}
              <div>
                <h4 className="text-sm font-bold text-white">
                  {result.is_valid ? 'Audit Log 100% Cryptographically Valid' : 'Tamper Alert Detected'}
                </h4>
                <p className="text-xs text-slate-400">
                  {result.is_valid
                    ? `Verified ${result.total_records} audit records sequentially without broken hashes.`
                    : `${result.errors.length} integrity violations detected.`}
                </p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wide border ${
              result.is_valid
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
            }`}>
              {result.is_valid ? 'TAMPER-PROOF' : 'TAMPERED'}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs pt-2 border-t border-slate-800">
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Total Verified Records</span>
              <span className="font-bold text-white font-mono">{result.total_records} Records</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800">
              <span className="text-slate-500 block text-[10px]">Genesis Hash</span>
              <span className="font-mono text-emerald-400 text-[10px] truncate block">SHA256(REVORA_PHASE3)</span>
            </div>
            <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 col-span-2 md:col-span-1">
              <span className="text-slate-500 block text-[10px]">Log File Path</span>
              <span className="font-mono text-slate-300 text-[10px] truncate block">{result.log_filepath}</span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
          <span>Error verifying audit log: {error}</span>
        </div>
      )}
    </div>
  );
}
