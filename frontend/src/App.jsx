import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import InspectorModal from './components/InspectorModal';
import OverviewPage from './pages/OverviewPage';
import SimulatorPage from './pages/SimulatorPage';
import DeepDivePage from './pages/DeepDivePage';
import AuditPage from './pages/AuditPage';
import DemoStudioPage from './pages/DemoStudioPage';
import { fetchHealth, fetchMetrics } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isHealthy, setIsHealthy] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [selectedTx, setSelectedTx] = useState(null);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const health = await fetchHealth();
        if (health && health.status === 'ok') {
          setIsHealthy(true);
        }
        const mData = await fetchMetrics();
        setMetrics(mData);
      } catch (err) {
        console.warn('Backend API connection offline:', err.message);
        setIsHealthy(false);
      }
    }
    loadInitialData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14] text-slate-100 font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} isHealthy={isHealthy} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {activeTab === 'overview' && <OverviewPage metrics={metrics} />}
        {activeTab === 'simulator' && <SimulatorPage onSelectTransaction={(tx) => setSelectedTx(tx)} />}
        {activeTab === 'inspector' && <DeepDivePage />}
        {activeTab === 'audit' && <AuditPage />}
        {activeTab === 'demo' && <DemoStudioPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>REVORA Autonomous Payment Recovery Engine — Phase 4.3</span>
          <span>Buildathon Demo Edition &bull; SHA-256 Tamper-Proof Audit</span>
        </div>
      </footer>

      {/* Global Inspector Modal */}
      {selectedTx && (
        <InspectorModal
          transaction={selectedTx}
          onClose={() => setSelectedTx(null)}
        />
      )}
    </div>
  );
}
