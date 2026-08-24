/**
 * API Client Service for REVORA Phase 4.3 Web Dashboard.
 * Interacts with frozen Phase 4.1 FastAPI endpoints.
 */

const API_BASE_URL = '/api/v1';

export async function fetchHealth() {
  const res = await fetch('/health');
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE_URL}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch system metrics');
  return res.json();
}

export async function predictTransaction(payload) {
  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function decideTransaction(payload) {
  const res = await fetch(`${API_BASE_URL}/decide`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Decision evaluation failed');
  }
  return res.json();
}

export async function simulateTransaction(payload = {}) {
  const res = await fetch(`${API_BASE_URL}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Simulation failed');
  }
  return res.json();
}

export async function verifyAuditTrail(filepath = 'data/audit/val_audit.jsonl') {
  const url = `${API_BASE_URL}/audit/verify?filepath=${encodeURIComponent(filepath)}`;
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Audit verification failed');
  }
  return res.json();
}
