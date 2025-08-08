"""
PyTest configuration and fixtures for Zebra Print Control System tests.
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def temp_db():
    """Provide temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def sample_label_data():
    """Provide sample label data for testing."""
    return {
        "title": "W-CPN/OUT/TEST",
        "date": "08/08/25",
        "qr_code": "TEST123456"
    }