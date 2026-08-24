import React from 'react';
import { DollarSign, TrendingUp, Zap, Shield, AlertTriangle, Layers, Percent } from 'lucide-react';
import KPICard from '../components/KPICard';

export default function OverviewPage({ metrics }) {
  const m = metrics || {
    total_failed_count: 3000,
    optimal_threshold: 0.1600,
    revenue_at_risk: 5528784.0,
    expected_recoverable_revenue: 2145620.0,
    gross_revenue_recovered: 1854200.0,
    retry_cost: 11590.0,
    net_revenue_recovered: 1842610.0,
    intervention_rate: 38.63,
    intervention_recovery_rate: 58.20,
    overall_recovery_yield: 33.33,
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Top 4 Executive KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Total Revenue at Risk"
          value={`INR ${m.revenue_at_risk.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          subtitle={`${m.total_failed_count.toLocaleString()} Failed Payments Scored`}
          icon={DollarSign}
          color="rose"
          badgeText="100% Failed Payments Scored"
        />
        <KPICard
          title="Expected Recoverable Revenue"
          value={`INR ${m.expected_recoverable_revenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          subtitle="Model Probability-Weighted Revenue"
          icon={TrendingUp}
          color="blue"
          badgeText={`Threshold Tau* = ${m.optimal_threshold}`}
        />
        <KPICard
          title="Net Revenue Recovered"
          value={`INR ${m.net_revenue_recovered.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          subtitle={`Minus INR ${m.retry_cost.toLocaleString()} Operational Cost`}
          icon={Zap}
          color="emerald"
          badgeText={`Yield = ${m.overall_recovery_yield}% Total Risk`}
        />
        <KPICard
          title="Intervention Selection Rate"
          value={`${m.intervention_rate}%`}
          subtitle={`${m.intervention_recovery_rate}% Success on Intervened`}
          icon={Percent}
          color="violet"
          badgeText="Optimal Selective Retries"
        />
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Revenue Funnel Visualizer */}
        <div className="lg:col-span-2 p-6 rounded-2xl glass-panel border border-slate-800 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-display font-bold text-white">Revenue Recovery Funnel</h3>
              <p className="text-xs text-slate-400">Step-by-step financial yield progression from failure to recovery</p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
              Optimal Tau* = 0.1600
            </span>
          </div>

          <div className="space-y-4">
            {/* Step 1 */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>1. Total Revenue at Risk (Failed Payments)</span>
                <span className="font-bold text-rose-400">INR {m.revenue_at_risk.toLocaleString('en-IN')} (100%)</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden">
                <div className="bg-rose-500 h-full rounded-full" style={{ width: '100%' }}></div>
              </div>
            </div>

            {/* Step 2 */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>2. Intervened Subset (P_rec &ge; 0.1600)</span>
                <span className="font-bold text-amber-400">INR {m.expected_recoverable_revenue.toLocaleString('en-IN')} ({m.intervention_rate}%)</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden">
                <div className="bg-amber-500 h-full rounded-full" style={{ width: `${m.intervention_rate}%` }}></div>
              </div>
            </div>

            {/* Step 3 */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>3. Gross Recovered Revenue</span>
                <span className="font-bold text-blue-400">INR {m.gross_revenue_recovered.toLocaleString('en-IN')} ({m.overall_recovery_yield}%)</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden">
                <div className="bg-blue-500 h-full rounded-full" style={{ width: `${m.overall_recovery_yield}%` }}></div>
              </div>
            </div>

            {/* Step 4 */}
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-300 mb-1.5">
                <span>4. Net Realized Yield (After Intervention Cost)</span>
                <span className="font-bold text-emerald-400">INR {m.net_revenue_recovered.toLocaleString('en-IN')}</span>
              </div>
              <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden">
                <div className="bg-gradient-to-r from-teal-500 to-emerald-400 h-full rounded-full" style={{ width: `${(m.net_revenue_recovered / m.revenue_at_risk * 100).toFixed(1)}%` }}></div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 grid grid-cols-3 gap-4 text-center text-xs">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Validation Set</span>
              <span className="font-bold text-white font-display text-base">3,000 Transactions</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Intervention Rate Cap</span>
              <span className="font-bold text-emerald-400 font-display text-base">&le; 40.0% Max</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase font-semibold">Safety Violations</span>
              <span className="font-bold text-emerald-400 font-display text-base">0 Violations</span>
            </div>
          </div>
        </div>

        {/* Failure Scenarios & Policy Rules Overview */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <h3 className="text-lg font-display font-bold text-white mb-2">Policy Engine Distribution</h3>

          <div className="space-y-3">
            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span className="text-slate-200 font-semibold">Immediate Retry (RETRY)</span>
              </div>
              <span className="font-bold text-emerald-400">35% Scenarios</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <span className="text-slate-200 font-semibold">Paced Retry (DELAY_AND_RETRY)</span>
              </div>
              <span className="font-bold text-cyan-400">40% Scenarios</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span className="text-slate-200 font-semibold">Customer Nudge (CUSTOMER_ACTION)</span>
              </div>
              <span className="font-bold text-amber-400">13% Scenarios</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-violet-400"></span>
                <span className="text-slate-200 font-semibold">Support Escalation (ESCALATE)</span>
              </div>
              <span className="font-bold text-violet-400">5% Scenarios</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
                <span className="text-slate-200 font-semibold">Hard Fraud Block (BLOCK)</span>
              </div>
              <span className="font-bold text-rose-400">7% Scenarios</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
