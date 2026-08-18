"""Convenience CLI to launch the interactive TokenTelemetry local web dashboard."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
try:
    from .token_tracker import collect_telemetry, serve_dashboard, DEFAULT_INR_RATE
except ImportError:
    from token_tracker import collect_telemetry, serve_dashboard, DEFAULT_INR_RATE

def main():
    parser = argparse.ArgumentParser(description="Launch TokenTelemetry Interactive Web Dashboard")
    parser.add_argument("--global", dest="is_global", action="store_true", help="Scan global host agents across ~/.claude, ~/.gemini, ~/.cursor, ~/.hermes")
    parser.add_argument("--dir", default=None, help="Target project directory (default: current directory)")
    parser.add_argument("--port", type=int, default=3000, help="Port to bind dashboard server (default: 3000)")
    parser.add_argument("--inr-rate", type=float, default=DEFAULT_INR_RATE, help="USD to INR exchange rate")
    args = parser.parse_args()

    target_path = Path(args.dir) if args.dir else Path.cwd()
    report = collect_telemetry(
        target_path=target_path,
        is_global=args.is_global,
        inr_rate=args.inr_rate,
    )
    serve_dashboard(report, port=args.port)

if __name__ == "__main__":
    main()
