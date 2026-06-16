"""Main test runner script"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run all tests and report results"""
    
    print("\n" + "="*80)
    print("GROGUI TEST SUITE - RUNNING ALL TESTS")
    print("="*80 + "\n")
    
    # Run pytest with verbose output
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes",
            "-ra"
        ],
        cwd=Path(__file__).parent.parent
    )
    
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
