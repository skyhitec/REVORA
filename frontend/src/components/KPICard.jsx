import React from 'react';

export default function KPICard({ title, value, subtitle, icon: Icon, color = 'emerald', badgeText }) {
  const colorMap = {
    emerald: 'from-emerald-500/10 to-emerald-500/5 text-emerald-400 border-emerald-500/20',
    blue: 'from-blue-500/10 to-blue-500/5 text-blue-400 border-blue-500/20',
    gold: 'from-amber-500/10 to-amber-500/5 text-amber-400 border-amber-500/20',
    violet: 'from-violet-500/10 to-violet-500/5 text-violet-400 border-violet-500/20',
    rose: 'from-rose-500/10 to-rose-500/5 text-rose-400 border-rose-500/20',
  };

  const iconBgMap = {
    emerald: 'bg-emerald-500/20 text-emerald-400',
    blue: 'bg-blue-500/20 text-blue-400',
    gold: 'bg-amber-500/20 text-amber-400',
    violet: 'bg-violet-500/20 text-violet-400',
    rose: 'bg-rose-500/20 text-rose-400',
  };

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-b ${colorMap[color] || colorMap.emerald} border backdrop-blur-xl relative overflow-hidden group hover:border-slate-700/80 transition-all shadow-lg shadow-black/20`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">{title}</p>
          <h3 className="text-2xl font-display font-extrabold text-white tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-slate-400 mt-1 font-medium">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-xl ${iconBgMap[color] || iconBgMap.emerald} flex items-center justify-center`}>
          <Icon className="w-5 h-5 stroke-[2]" />
        </div>
      </div>
      {badgeText && (
        <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-[11px]">
          <span className="text-slate-400">Benchmark Performance</span>
          <span className="font-semibold text-slate-200">{badgeText}</span>
        </div>
      )}
    </div>
  );
}
