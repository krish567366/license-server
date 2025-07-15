"""Tests for core validation functionality."""

import pytest
import os
from unittest.mock import patch
from quantummeta_license.core.validation import (
    validate_or_grace,
    check_license_status,
    is_development_mode,
    LicenseError,
    LicenseExpiredError,
    LicenseNotFoundError,
    InvalidLicenseError,
    FeatureNotLicensedError
)


class TestDevelopmentMode:
    """Test development mode functionality."""
    
    def test_development_mode_enabled(self):
        """Test development mode detection when enabled."""
        with patch.dict(os.environ, {"QUANTUMMETA_DEV": "1"}):
            assert is_development_mode() is True
        
        with patch.dict(os.environ, {"QUANTUMMETA_DEV": "true"}):
            assert is_development_mode() is True
        
        with patch.dict(os.environ, {"QUANTUMMETA_DEV": "YES"}):
            assert is_development_mode() is True
    
    def test_development_mode_disabled(self):
        """Test development mode detection when disabled."""
        with patch.dict(os.environ, {"QUANTUMMETA_DEV": "0"}, clear=True):
            assert is_development_mode() is False
        
        with patch.dict(os.environ, {}, clear=True):
            assert is_development_mode() is False


class TestValidateOrGrace:
    """Test main validation function."""
    
    def test_development_mode_bypass(self, license_manager, usage_tracker):
        """Test that development mode bypasses all checks."""
        with patch.dict(os.environ, {"QUANTUMMETA_DEV": "1"}):
            # Should always return True in dev mode
            assert validate_or_grace("any-package") is True
    
    def test_valid_license_validation(self, license_manager, usage_tracker):
        """Test validation with a valid license."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Create and store a valid license
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            machine_id=get_machine_id(),
            features=["core", "pro"]
        )
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(license_data, str(license_file))
        
        # Should validate successfully
        assert validate_or_grace("test-package") is True
        assert validate_or_grace("test-package", ["core"]) is True
        assert validate_or_grace("test-package", ["core", "pro"]) is True
    
    def test_expired_license_error(self, license_manager, usage_tracker, expired_license_data):
        """Test validation with expired license."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Modify expired license to have correct machine ID
        expired_license_data["machine_id"] = get_machine_id()
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(expired_license_data, str(license_file))
        
        with pytest.raises(LicenseExpiredError, match="License for 'test-package' has expired"):
            validate_or_grace("test-package")
    
    def test_wrong_machine_id_error(self, license_manager, usage_tracker, sample_license_data):
        """Test validation with wrong machine ID."""
        # Use the sample license data which has a fake machine ID
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(sample_license_data, str(license_file))
        
        with pytest.raises(InvalidLicenseError, match="License for 'test-package' is not valid for this machine"):
            validate_or_grace("test-package")
    
    def test_missing_features_error(self, license_manager, usage_tracker):
        """Test validation with missing required features."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Create license with limited features
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            machine_id=get_machine_id(),
            features=["core"]
        )
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(license_data, str(license_file))
        
        with pytest.raises(FeatureNotLicensedError, match="does not include required features"):
            validate_or_grace("test-package", ["enterprise"])
    
    def test_grace_period_new_package(self, license_manager, usage_tracker):
        """Test grace period for new package."""
        # No license exists, should start grace period
        assert validate_or_grace("new-package") is True
        
        # Should have recorded first use
        first_use = usage_tracker.get_first_use_date("new-package")
        assert first_use is not None
    
    def test_grace_period_expired_error(self, license_manager, usage_tracker):
        """Test error when grace period is expired."""
        from datetime import datetime, timedelta
        
        # Manually set expired grace period
        old_date = datetime.now() - timedelta(days=10)
        log_data = {
            "expired-package": {
                "first_use": old_date.isoformat(),
                "last_check": old_date.isoformat()
            }
        }
        usage_tracker._save_usage_log(log_data)
        
        with pytest.raises(LicenseNotFoundError, match="Grace period for 'expired-package' expired"):
            validate_or_grace("expired-package", grace_days=7)


class TestCheckLicenseStatus:
    """Test license status checking function."""
    
    def test_status_development_mode(self, license_manager, usage_tracker):
        """Test status in development mode."""
        with patch.dict(os.environ, {"QUANTUMMETA_DEV": "1"}):
            status = check_license_status("any-package")
            
            assert status["status"] == "development_mode"
            assert status["has_license"] is False
            assert status["in_grace_period"] is False
            assert "Development mode is enabled" in status["message"]
    
    def test_status_valid_license(self, license_manager, usage_tracker):
        """Test status with valid license."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Create and store valid license
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            machine_id=get_machine_id(),
            features=["core", "pro"]
        )
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(license_data, str(license_file))
        
        status = check_license_status("test-package")
        
        assert status["status"] == "licensed"
        assert status["has_license"] is True
        assert status["in_grace_period"] is False
        assert "Valid license found" in status["message"]
        assert status["license_info"]["user"] == "test@example.com"
        assert status["license_info"]["features"] == ["core", "pro"]
    
    def test_status_expired_license(self, license_manager, usage_tracker, expired_license_data):
        """Test status with expired license."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Modify expired license to have correct machine ID
        expired_license_data["machine_id"] = get_machine_id()
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(expired_license_data, str(license_file))
        
        status = check_license_status("test-package")
        
        assert status["status"] == "invalid_license"
        assert status["has_license"] is True
        assert status["in_grace_period"] is False
        assert "License expired" in status["message"]
    
    def test_status_wrong_machine(self, license_manager, usage_tracker, sample_license_data):
        """Test status with wrong machine ID."""
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(sample_license_data, str(license_file))
        
        status = check_license_status("test-package")
        
        assert status["status"] == "invalid_license"
        assert status["has_license"] is True
        assert status["in_grace_period"] is False
        assert "not valid for this machine" in status["message"]
    
    def test_status_grace_period_active(self, license_manager, usage_tracker):
        """Test status during active grace period."""
        # Record first use for new package
        usage_tracker.record_first_use("grace-package")
        
        status = check_license_status("grace-package")
        
        assert status["status"] == "grace_period"
        assert status["has_license"] is False
        assert status["in_grace_period"] is True
        assert "Grace period active" in status["message"]
        assert "grace_info" in status
        assert status["grace_info"]["is_expired"] is False
    
    def test_status_grace_period_expired(self, license_manager, usage_tracker):
        """Test status when grace period is expired."""
        from datetime import datetime, timedelta
        
        # Set expired grace period
        old_date = datetime.now() - timedelta(days=10)
        log_data = {
            "expired-grace-package": {
                "first_use": old_date.isoformat(),
                "last_check": old_date.isoformat()
            }
        }
        usage_tracker._save_usage_log(log_data)
        
        status = check_license_status("expired-grace-package")
        
        assert status["status"] == "expired"
        assert status["has_license"] is False
        assert status["in_grace_period"] is False
        assert "Grace period expired" in status["message"]
        assert status["grace_info"]["is_expired"] is True
