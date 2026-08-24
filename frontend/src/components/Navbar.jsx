import React from 'react';
import { Activity, ShieldCheck, Cpu, Zap, LayoutDashboard, Database, PlayCircle } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, isHealthy }) {
  const tabs = [
    { id: 'overview', label: 'Executive Dashboard', icon: LayoutDashboard },
    { id: 'simulator', label: 'Live Stream Simulator', icon: Zap },
    { id: 'inspector', label: 'Decision Inspector', icon: Cpu },
    { id: 'audit', label: 'Cryptographic Audit UI', icon: ShieldCheck },
    { id: 'demo', label: 'Buildathon Demo Studio', icon: PlayCircle },
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#080c14]/90 backdrop-blur-xl border-b border-slate-800/80 px-6 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Activity className="w-6 h-6 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-display font-extrabold text-xl tracking-tight text-white">REVORA</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                Phase 4.3 Production
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Autonomous Payment Recovery & Policy Engine</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center bg-slate-900/80 p-1.5 rounded-xl border border-slate-800/80 overflow-x-auto custom-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 shadow-md shadow-emerald-500/20 font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-slate-950' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Health Status Indicator */}
        <div className="hidden lg:flex items-center space-x-2.5 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800/80">
          <span className={`w-2.5 h-2.5 rounded-full ${isHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
          <span className="text-xs font-medium text-slate-300">
            {isHealthy ? 'FastAPI API Active (Port 8000)' : 'API Disconnected'}
          </span>
        </div>
      </div>
    </header>
  );
}
