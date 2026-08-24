# REVORA Phase 4.3 — Interactive Web Dashboard Guide

## 📌 Executive Overview

Phase 4.3 delivers a **production-quality React + Vite Web Application** for REVORA. It provides an intuitive, high-impact user interface for demonstrating, monitoring, and inspecting autonomous payment recovery predictions, policy decisions, ERV calculations, and cryptographic SHA-256 audit logs in real time.

---

## 🎨 Design System & Visual Aesthetics

- **Theme**: Premium Fintech Dark Mode (`#080c14` base background).
- **Typography**: Google Fonts Inter (sans UI) & Outfit (display numbers/headings).
- **Glassmorphic Components**: High-blur backdrop panels (`backdrop-blur-xl`), dark slate borders (`border-slate-800`).
- **Action Badges**:
  - `RETRY`: Emerald (`#10b981`)
  - `DELAY_AND_RETRY`: Cyan (`#06b6d4`)
  - `RETRY_WITH_CAUTION`: Amber (`#f59e0b`)
  - `CUSTOMER_ACTION_REQUIRED`: Orange (`#f97316`)
  - `ESCALATE`: Violet (`#8b5cf6`)
  - `BLOCK`: Rose (`#f43f5e`)
  - `NO_ACTION`: Slate (`#64748b`)

---

## 💻 5 Interactive Dashboard Tabs

### 1. Executive Recovery Overview (`OverviewPage.jsx`)
- **Top 4 KPI Cards**:
  - Total Revenue at Risk (₹)
  - Expected Recoverable Revenue (Probability-weighted ₹)
  - Net Realized Yield (Gross Recovery - Retry Costs ₹)
  - Selective Intervention Rate (%)
- **Revenue Recovery Funnel**: 4-stage visual progress bar tracking revenue from initial failure to net yield.
- **Policy Engine Distribution**: Breakdowns for retry scenarios.

### 2. Real-Time Stream Simulator (`SimulatorPage.jsx`)
- **Live Stream Controls**: Start/Pause stream toggle, rate pacing selector (0.5s, 1.0s, 2.0s), and "Tick Single" trigger.
- **Custom Event Injector**: Form to input custom amounts, failure codes, payment methods, and probabilities.
- **Streaming Feed Table**: Interactive live feed showing transaction ID, failure code, $P_{\text{rec}}$ probability bar, risk level badge, decision badge, and net ERV.

### 3. Transaction Deep-Dive Inspector (`InspectorModal.jsx` & `DeepDivePage.jsx`)
- **Financial ERV Breakdown**: Displays Gross ERV ($P_{\text{rec}} \times \text{Amount}$), intervention cost, and Net ERV.
- **Deterministic Guardrails Trace**: Step-by-step checklist of safety guardrail checks showing passed/failed rules and forced decisions.
- **Human-Readable Rationale**: Natural language policy decision explanation.

### 4. Cryptographic Audit Verifier (`AuditPage.jsx` & `AuditVerifierWidget.jsx`)
- One-click **"Verify SHA-256 Hash Chain Integrity"** button invoking `/api/v1/audit/verify`.
- Displays total verified records, Genesis hash (`SHA256("REVORA_PHASE3_GENESIS")`), log file path, and green tamper-proof badge.

### 5. Buildathon Demo Studio (`DemoStudioPage.jsx` & `BuildathonDemoCards.jsx`)
- 5 pre-configured one-click scenario cards:
  1. *Transient Gateway Failure* $\rightarrow$ Immediate Retry (`RETRY`)
  2. *High-Value Auth Failure* $\rightarrow$ Support Escalation (`ESCALATE`)
  3. *Fraud Risk Flag* $\rightarrow$ Hard Safety Guardrail (`BLOCK`)
  4. *Expired Credit Card* $\rightarrow$ Customer Update Nudge (`CUSTOMER_ACTION_REQUIRED`)
  5. *Low P_rec / High Friction* $\rightarrow$ Cost Suppression (`NO_ACTION`)

---

## 🚀 Running the Demo Application

### Unified Launcher
```bash
python scripts/start_demo.py
```

### Manual Mode
1. **Start Backend**:
   ```bash
   uvicorn src.api.main:app --port 8000
   ```
2. **Start Dashboard**:
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173`.
