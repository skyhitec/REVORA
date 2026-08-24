import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RefreshCw, Send, Sliders, Eye, Zap, Shield, Sparkles } from 'lucide-react';
import { simulateTransaction } from '../services/api';
import { DecisionBadge, RiskBadge } from '../components/DecisionBadge';

export default function SimulatorPage({ onSelectTransaction }) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamEvents, setStreamEvents] = useState([]);
  const [speed, setSpeed] = useState(1.5); // seconds per tick
  const [customForm, setCustomForm] = useState({
    amount: 2500,
    failure_code: 'TEMPORARY_GATEWAY_FAILURE',
    payment_method: 'UPI',
    recovery_probability: 0.85,
  });
  const timerRef = useRef(null);

  const failureCodes = [
    'TEMPORARY_GATEWAY_FAILURE',
    'GATEWAY_TIMEOUT',
    'INSUFFICIENT_FUNDS',
    'EXPIRED_CARD',
    'INVALID_CREDENTIALS',
    'AUTHENTICATION_FAILURE',
    'BANK_DECLINED',
    'FRAUD_RISK_BLOCK',
  ];

  const paymentMethods = ['UPI', 'CREDIT_CARD', 'DEBIT_CARD', 'NET_BANKING', 'WALLET'];

  // Single simulation trigger
  const triggerSimulation = async (customPayload = null) => {
    try {
      const payload = customPayload || {
        amount: Number(customForm.amount),
        failure_code: customForm.failure_code,
        payment_method: customForm.payment_method,
        recovery_probability: Number(customForm.recovery_probability),
      };

      const res = await simulateTransaction(payload);
      const newEvent = {
        event_index: streamEvents.length + 1,
        ...res,
      };
      setStreamEvents((prev) => [newEvent, ...prev.slice(0, 49)]); // Keep last 50
    } catch (err) {
      console.error('Simulation error:', err);
    }
  };

  // Streaming interval
  useEffect(() => {
    if (isStreaming) {
      timerRef.current = setInterval(() => {
        // Generate random simulation event
        const randomCode = failureCodes[Math.floor(Math.random() * failureCodes.length)];
        const randomMethod = paymentMethods[Math.floor(Math.random() * paymentMethods.length)];
        const randomAmount = Math.floor(Math.random() * 20000) + 200;
        const randomProb = Number((Math.random() * 0.7 + 0.2).toFixed(2));

        triggerSimulation({
          amount: randomAmount,
          failure_code: randomCode,
          payment_method: randomMethod,
          recovery_probability: randomProb,
        });
      }, speed * 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isStreaming, speed, streamEvents.length]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* Stream Controls & Custom Simulator Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Controls Card */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-display font-bold text-white flex items-center space-x-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              <span>Stream Controls</span>
            </h3>
            <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider border ${
              isStreaming
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 animate-pulse'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}>
              {isStreaming ? 'STREAMING LIVE' : 'PAUSED'}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsStreaming(!isStreaming)}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-xl font-bold text-xs shadow-lg transition-all ${
                isStreaming
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30 hover:bg-rose-500/30'
                  : 'bg-emerald-500 text-slate-950 hover:bg-emerald-400 shadow-emerald-500/20'
              }`}
            >
              {isStreaming ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-slate-950" />}
              <span>{isStreaming ? 'Pause Stream' : 'Start Live Stream'}</span>
            </button>

            <button
              onClick={() => triggerSimulation()}
              className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs border border-slate-700 flex items-center space-x-1.5 transition-all"
            >
              <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
              <span>Tick Single</span>
            </button>
          </div>

          <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Stream Speed:</span>
            <div className="flex items-center space-x-2">
              {[0.5, 1.0, 2.0].map((s) => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={`px-2.5 py-1 rounded text-[11px] font-bold border transition-colors ${
                    speed === s
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
                  }`}
                >
                  {s}s
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Custom Event Form */}
        <div className="lg:col-span-2 p-6 rounded-2xl glass-panel border border-slate-800">
          <h3 className="text-base font-display font-bold text-white mb-3 flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <span>Custom Failure Event Injector</span>
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div>
              <label className="text-slate-400 block mb-1 font-medium">Amount (INR)</label>
              <input
                type="number"
                value={customForm.amount}
                onChange={(e) => setCustomForm({ ...customForm, amount: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="text-slate-400 block mb-1 font-medium">Failure Code</label>
              <select
                value={customForm.failure_code}
                onChange={(e) => setCustomForm({ ...customForm, failure_code: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-white text-[11px] focus:outline-none focus:border-emerald-500"
              >
                {failureCodes.map((fc) => (
                  <option key={fc} value={fc}>{fc}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-slate-400 block mb-1 font-medium">Payment Method</label>
              <select
                value={customForm.payment_method}
                onChange={(e) => setCustomForm({ ...customForm, payment_method: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-white text-[11px] focus:outline-none focus:border-emerald-500"
              >
                {paymentMethods.map((pm) => (
                  <option key={pm} value={pm}>{pm}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-slate-400 block mb-1 font-medium">P_rec Probability</label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={customForm.recovery_probability}
                onChange={(e) => setCustomForm({ ...customForm, recovery_probability: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-emerald-400 font-mono font-bold focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={() => triggerSimulation()}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white font-bold text-xs flex items-center space-x-2 shadow-lg shadow-cyan-600/20 transition-all"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Simulate Custom Event</span>
            </button>
          </div>
        </div>

      </div>

      {/* Real-time Stream Table */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-display font-bold text-white">Live Payment Failure Feed</h3>
            <p className="text-xs text-slate-400">Showing real-time evaluated transactions (Click row for deep-dive inspection)</p>
          </div>
          <span className="text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">
            {streamEvents.length} Events Captured
          </span>
        </div>

        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider bg-slate-950/40">
                <th className="py-3 px-4">#</th>
                <th className="py-3 px-4">Transaction ID</th>
                <th className="py-3 px-4">Failure Scenario</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">P_rec</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Decision Action</th>
                <th className="py-3 px-4">Net ERV</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {streamEvents.length > 0 ? (
                streamEvents.map((ev, idx) => (
                  <tr
                    key={ev.transaction_id + idx}
                    onClick={() => onSelectTransaction && onSelectTransaction(ev)}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                  >
                    <td className="py-3 px-4 font-mono text-slate-500">#{ev.event_index}</td>
                    <td className="py-3 px-4 font-mono text-white font-medium">{ev.transaction_id}</td>
                    <td className="py-3 px-4 text-slate-300 font-medium">{ev.failure_code}</td>
                    <td className="py-3 px-4 font-mono font-semibold text-white">INR {(ev.amount || 0).toLocaleString()}</td>
                    <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                      {((ev.recovery_probability || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4">
                      <RiskBadge riskLevel={ev.risk_level} />
                    </td>
                    <td className="py-3 px-4">
                      <DecisionBadge decision={ev.decision} />
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                      INR {(ev.net_expected_recovery_value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button className="p-1.5 rounded-lg bg-slate-800 text-slate-400 group-hover:text-emerald-400 group-hover:bg-slate-700 transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="9" className="py-12 text-center text-slate-500 italic">
                    No simulated transactions yet. Click <span className="text-emerald-400 font-semibold">'Start Live Stream'</span> or <span className="text-cyan-400 font-semibold">'Tick Single'</span> to generate events.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
