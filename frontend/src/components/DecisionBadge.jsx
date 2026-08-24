import React from 'react';

export function DecisionBadge({ decision }) {
  const badgeStyles = {
    RETRY: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    DELAY_AND_RETRY: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
    RETRY_WITH_CAUTION: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    CUSTOMER_ACTION_REQUIRED: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
    ESCALATE: 'bg-violet-500/15 text-violet-400 border-violet-500/30',
    BLOCK: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    NO_ACTION: 'bg-slate-700/30 text-slate-400 border-slate-700/50',
  };

  const decStr = decision ? decision.toUpperCase() : 'NO_ACTION';
  const style = badgeStyles[decStr] || badgeStyles.NO_ACTION;

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-bold border tracking-wide uppercase ${style}`}>
      {decStr}
    </span>
  );
}

export function RiskBadge({ riskLevel }) {
  const riskStyles = {
    LOW: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    MEDIUM: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    HIGH: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    CRITICAL: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
  };

  const riskStr = riskLevel ? riskLevel.toUpperCase() : 'LOW';
  const style = riskStyles[riskStr] || riskStyles.LOW;

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-extrabold border uppercase tracking-wider ${style}`}>
      {riskStr}
    </span>
  );
}
