#!/usr/bin/env python
"""Comprehensive test execution and reporting script"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def print_header():
    """Print header"""
    print("\n" + "="*80)
    print("🧪 GROGUI COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def run_tests():
    """Run all tests"""
    print_header()
    
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes",
            "-ra",
            "--co"  # Collect only to show what would run
        ],
        cwd=Path(__file__).parent
    )
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    
    print("\n" + "="*80)
    print("✅ TEST SUITE EXECUTION COMPLETE")
    print("="*80 + "\n")
    
    sys.exit(exit_code)
