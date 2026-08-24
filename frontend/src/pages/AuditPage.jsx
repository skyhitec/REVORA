import React from 'react';
import { Lock, ShieldCheck, FileCode, CheckCircle2, Key } from 'lucide-react';
import AuditVerifierWidget from '../components/AuditVerifierWidget';

export default function AuditPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* Audit Verifier Widget */}
      <AuditVerifierWidget />

      {/* Cryptographic Architecture Card */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Key className="w-5 h-5 stroke-[2]" />
          </div>
          <div>
            <h3 className="text-base font-display font-bold text-white">SHA-256 Hash Chain Specification</h3>
            <p className="text-xs text-slate-400">Mathematical immutability formulas enforcing audit log integrity</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-slate-400 font-sans font-semibold block text-xs">Genesis Hash (H_0)</span>
            <p className="text-emerald-400 font-bold bg-slate-900 p-2.5 rounded border border-slate-800 text-[11px] break-all">
              SHA256("REVORA_PHASE3_GENESIS")
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <span className="text-slate-400 font-sans font-semibold block text-xs">Sequential Chain Link (H_i)</span>
            <p className="text-cyan-400 font-bold bg-slate-900 p-2.5 rounded border border-slate-800 text-[11px] break-all">
              H_i = SHA256(H_i-1 || CanonicalJSON(R_i))
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 space-y-2">
          <p className="font-semibold text-white">Tamper Detection Invariants:</p>
          <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
            <li>Modifying a single character in any past record invalidates all subsequent hashes.</li>
            <li>Reordering or deleting lines breaks cryptographic continuity immediately.</li>
            <li>Fully validated by AuditVerifier in O(N) linear time during compliance audits.</li>
          </ul>
        </div>
      </div>

    </div>
  );
}
