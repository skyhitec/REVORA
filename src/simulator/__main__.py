"""
CLI Entrypoint for running REVORA Real-Time Transaction Simulator (`python -m src.simulator`).
"""

import sys
import json
import argparse
from pathlib import Path

from src.simulator.event_generator import TransactionEventGenerator
from src.simulator.stream_processor import TransactionStreamSimulator


def main():
    parser = argparse.ArgumentParser(
        description="REVORA Phase 4.2 Real-Time Payment Failure Stream Simulator"
    )
    parser.add_argument(
        "--num-events", "-n", type=int, default=20, help="Total transaction events to simulate (default: 20)"
    )
    parser.add_argument(
        "--rate", "-r", type=float, default=10.0, help="Event stream rate per second (default: 10.0)"
    )
    parser.add_argument(
        "--seed", "-s", type=int, default=42, help="Random seed for reproducible streaming (default: 42)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Optional output JSONL file path to save event results"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress console streaming output"
    )

    args = parser.parse_args()

    generator = TransactionEventGenerator(seed=args.seed)
    simulator = TransactionStreamSimulator(generator=generator)

    print(f"Starting REVORA Transaction Simulator (Events: {args.num_events}, Rate: {args.rate}/s, Seed: {args.seed})...\n")

    out_file = None
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_file = open(out_path, "w", encoding="utf-8")

    interventions_count = 0
    gross_erv_sum = 0.0

    try:
        for res in simulator.stream_events(
            total_events=args.num_events,
            rate_per_sec=args.rate,
            seed=args.seed,
        ):
            res_dict = res.to_dict()
            if out_file:
                out_file.write(json.dumps(res_dict) + "\n")
                out_file.flush()

            gross_erv_sum += res.expected_recovery_value
            if res.decision in ["RETRY", "DELAY_AND_RETRY", "RETRY_WITH_CAUTION", "CUSTOMER_ACTION_REQUIRED", "ESCALATE"]:
                interventions_count += 1

            if not args.quiet:
                badge = f"[{res.decision}]"
                print(
                    f"#{res.event_index:03d} | {res.transaction_id} | {res.failure_code:28s} | "
                    f"P_rec: {res.recovery_probability:.4f} | Risk: {res.risk_level:8s} | "
                    f"Action: {badge:22s} | Net ERV: INR {res.net_expected_recovery_value:,.2f}"
                )
    finally:
        if out_file:
            out_file.close()
            print(f"\nSaved simulation log to '{args.output}'.")

    print("\n" + "=" * 80)
    print(f"Simulation Complete: {args.num_events} Events Processed.")
    print(f"Total Interventions: {interventions_count} / {args.num_events} ({interventions_count / args.num_events * 100:.1f}%)")
    print(f"Total Expected Recovery Value (ERV): INR {gross_erv_sum:,.2f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
