"""Pytest configuration and fixtures"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data_dir():
    """Get test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset imported modules between tests"""
    yield
