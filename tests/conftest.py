"""Test configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from quantummeta_license.core.license_manager import LicenseManager
from quantummeta_license.core.usage_tracker import UsageTracker
from quantummeta_license.core.encryption import LicenseSignature


@pytest.fixture
def temp_config_dir():
    """Create a temporary configuration directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def license_manager(temp_config_dir, monkeypatch):
    """Create a LicenseManager with a temporary config directory."""
    monkeypatch.setattr("platformdirs.user_config_dir", lambda x: str(temp_config_dir))
    return LicenseManager()


@pytest.fixture
def usage_tracker(temp_config_dir, monkeypatch):
    """Create a UsageTracker with a temporary config directory."""
    monkeypatch.setattr("platformdirs.user_config_dir", lambda x: str(temp_config_dir))
    return UsageTracker()


@pytest.fixture
def sample_license_data() -> Dict[str, Any]:
    """Create sample license data for testing."""
    now = datetime.now()
    return {
        "package": "test-package",
        "user": "test@example.com",
        "machine_id": "test-machine-id-12345",
        "issued": now.isoformat(),
        "expires": (now + timedelta(days=365)).isoformat(),
        "features": ["core", "pro"]
    }


@pytest.fixture
def expired_license_data() -> Dict[str, Any]:
    """Create expired license data for testing."""
    now = datetime.now()
    return {
        "package": "test-package",
        "user": "test@example.com",
        "machine_id": "test-machine-id-12345",
        "issued": (now - timedelta(days=400)).isoformat(),
        "expires": (now - timedelta(days=30)).isoformat(),
        "features": ["core"]
    }


@pytest.fixture
def signing_keys():
    """Generate Ed25519 keypair for testing."""
    return LicenseSignature.generate_keypair()


@pytest.fixture
def signed_license_data(sample_license_data, signing_keys) -> Dict[str, Any]:
    """Create signed license data for testing."""
    private_key, _ = signing_keys
    license_data = sample_license_data.copy()
    license_data["signature"] = LicenseSignature.sign_license(license_data, private_key)
    return license_data
