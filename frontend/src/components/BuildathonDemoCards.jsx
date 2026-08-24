import React from 'react';
import { Play, CheckCircle, ShieldAlert, CreditCard, UserCheck, ArrowRight, Zap } from 'lucide-react';
import { decideTransaction } from '../services/api';

export default function BuildathonDemoCards({ onRunDemo }) {
  const scenarios = [
    {
      id: 'gateway_retry',
      title: 'Transient Gateway Failure',
      badge: 'High Yield Retry',
      color: 'emerald',
      icon: CheckCircle,
      desc: 'INR 12,500 payment failed due to TEMPORARY_GATEWAY_FAILURE. ML P_rec = 85%.',
      expectedAction: 'RETRY',
      payload: {
        transaction_id: 'demo_gateway_01',
        amount: 12500.0,
        failure_code: 'TEMPORARY_GATEWAY_FAILURE',
        payment_method: 'UPI',
        predicted_recovery_probability: 0.85,
      }
    },
    {
      id: 'high_value_escalate',
      title: 'High-Value Auth Failure',
      badge: 'VIP Escalation',
      color: 'violet',
      icon: UserCheck,
      desc: 'INR 45,000 corporate payment failed due to AUTHENTICATION_FAILURE. Requires VIP escalation.',
      expectedAction: 'ESCALATE',
      payload: {
        transaction_id: 'demo_escalate_01',
        amount: 45000.0,
        failure_code: 'AUTHENTICATION_FAILURE',
        payment_method: 'CREDIT_CARD',
        predicted_recovery_probability: 0.75,
      }
    },
    {
      id: 'fraud_block',
      title: 'Fraud Risk Flag',
      badge: 'Hard Guardrail',
      color: 'rose',
      icon: ShieldAlert,
      desc: 'High ML probability (92%) overridden by mandatory FRAUD_RISK_BLOCK safety guardrail.',
      expectedAction: 'BLOCK',
      payload: {
        transaction_id: 'demo_fraud_01',
        amount: 25000.0,
        failure_code: 'FRAUD_RISK_BLOCK',
        payment_method: 'CREDIT_CARD',
        predicted_recovery_probability: 0.92,
      }
    },
    {
      id: 'expired_card',
      title: 'Expired Card Credential',
      badge: 'Customer Nudge',
      color: 'gold',
      icon: CreditCard,
      desc: 'Non-retryable EXPIRED_CARD failure. Automatically triggers customer update nudge.',
      expectedAction: 'CUSTOMER_ACTION_REQUIRED',
      payload: {
        transaction_id: 'demo_expired_01',
        amount: 3200.0,
        failure_code: 'EXPIRED_CARD',
        payment_method: 'CREDIT_CARD',
        predicted_recovery_probability: 0.40,
      }
    },
    {
      id: 'negative_erv_skip',
      title: 'Negative Net ERV Skip',
      badge: 'Cost Optimizer',
      color: 'blue',
      icon: Zap,
      desc: 'Low P_rec (12%) where retry cost exceeds expected recovery. Engine suppresses retry.',
      expectedAction: 'NO_ACTION',
      payload: {
        transaction_id: 'demo_skip_01',
        amount: 80.0,
        failure_code: 'TEMPORARY_GATEWAY_FAILURE',
        payment_method: 'WALLET',
        predicted_recovery_probability: 0.12,
      }
    }
  ];

  const colorStyles = {
    emerald: 'border-emerald-500/30 hover:border-emerald-500/60 bg-emerald-500/5',
    violet: 'border-violet-500/30 hover:border-violet-500/60 bg-violet-500/5',
    rose: 'border-rose-500/30 hover:border-rose-500/60 bg-rose-500/5',
    gold: 'border-amber-500/30 hover:border-amber-500/60 bg-amber-500/5',
    blue: 'border-blue-500/30 hover:border-blue-500/60 bg-blue-500/5',
  };

  const badgeStyles = {
    emerald: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    violet: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
    rose: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    gold: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  };

  const handleCardClick = async (sc) => {
    try {
      const res = await decideTransaction(sc.payload);
      if (onRunDemo) onRunDemo(res);
    } catch (e) {
      console.error('Demo card error:', e);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-display font-bold text-white">Buildathon Demo Studio</h3>
          <p className="text-xs text-slate-400">One-click interactive demonstration scenarios for REVORA decision engine</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {scenarios.map((sc) => {
          const Icon = sc.icon;
          return (
            <div
              key={sc.id}
              onClick={() => handleCardClick(sc)}
              className={`p-4 rounded-xl border backdrop-blur-md cursor-pointer transition-all duration-200 hover:-translate-y-1 flex flex-col justify-between ${colorStyles[sc.color]}`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded border uppercase tracking-wider ${badgeStyles[sc.color]}`}>
                    {sc.badge}
                  </span>
                  <Icon className="w-4 h-4 text-slate-400" />
                </div>
                <h4 className="text-sm font-bold text-white mb-1">{sc.title}</h4>
                <p className="text-[11px] text-slate-400 leading-relaxed mb-4">{sc.desc}</p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-white group">
                <span>Run Scenario</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
