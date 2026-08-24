import React, { useState } from 'react';
import BuildathonDemoCards from '../components/BuildathonDemoCards';
import InspectorModal from '../components/InspectorModal';

export default function DemoStudioPage() {
  const [selectedDemoResult, setSelectedDemoResult] = useState(null);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* 5 One-Click Buildathon Scenario Cards */}
      <BuildathonDemoCards onRunDemo={(res) => setSelectedDemoResult(res)} />

      {/* Active Demo Execution Result Banner */}
      {selectedDemoResult && (
        <div className="p-6 rounded-2xl glass-panel border border-emerald-500/30 bg-emerald-500/5 space-y-4 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white uppercase tracking-wider text-emerald-400">
              Active Scenario Execution Output
            </h4>
            <span className="font-mono text-xs text-slate-400">ID: {selectedDemoResult.transaction_id}</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-500 text-[10px] block">Decision</span>
              <span className="font-bold text-emerald-400 text-sm">{selectedDemoResult.decision}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-500 text-[10px] block">Risk Level</span>
              <span className="font-bold text-white text-sm">{selectedDemoResult.risk_level}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-500 text-[10px] block">ML Probability</span>
              <span className="font-bold text-cyan-400 text-sm">{((selectedDemoResult.recovery_probability || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <span className="text-slate-500 text-[10px] block">Net Expected Recovery</span>
              <span className="font-bold text-emerald-400 text-sm">INR {(selectedDemoResult.net_expected_recovery_value || 0).toLocaleString()}</span>
            </div>
          </div>

          <p className="text-xs text-slate-300 font-mono bg-slate-950 p-3 rounded-lg border border-slate-800">
            {selectedDemoResult.reason}
          </p>
        </div>
      )}

      {/* Inspector Modal if opened */}
      {selectedDemoResult && (
        <InspectorModal
          transaction={selectedDemoResult}
          onClose={() => setSelectedDemoResult(null)}
        />
      )}

    </div>
  );
}
