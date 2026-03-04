#!/usr/bin/env python3
"""
CLI Module - Command-line interface for auto flow
Extracted from auto_run_full_flow.py for better modularity
"""
import sys
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

from .runner import AutoTestRunner


def setup_logging() -> Path:
    """Setup logging configuration"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f"auto_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_file


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Upstox API Auto Run Full Flow')
    parser.add_argument('--delay', type=int, default=0, 
                        help='Wait N seconds before starting')
    parser.add_argument('--allure', action='store_true', 
                        help='Enable Allure reporting')
    parser.add_argument('--allure-dir', type=str, default='reports/allure-results',
                        help='Allure results directory')
    return parser.parse_args()


def print_header(allure_enabled: bool, allure_dir: str):
    """Print execution header"""
    print("\n🚀 Upstox API Auto Run - Full 5-Stage Flow")
    print("=" * 70)
    if allure_enabled:
        print("📊 Allure Reporting: ENABLED")
        print(f"📁 Results Dir: {allure_dir}")
        print("=" * 70)


def main() -> int:
    """Main entry point"""
    log_file = setup_logging()
    args = parse_arguments()

    if args.delay > 0:
        print(f"\n⏳ Waiting {args.delay} seconds before starting...")
        time.sleep(args.delay)

    print_header(args.allure, args.allure_dir)

    runner = AutoTestRunner(
        allure_enabled=args.allure, 
        allure_results_dir=args.allure_dir
    )

    # Run all stages
    success = runner.run_all_stages()

    if success:
        runner.print_final_summary()
        print(f"\n📁 Reports saved in: reports/")
        print(f"📝 Log file: {log_file}")

        if args.allure:
            print(f"\n📊 To view Allure report, run:")
            print(f"   allure serve {args.allure_dir}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
