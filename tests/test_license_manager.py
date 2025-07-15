"""Tests for license manager functionality."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from quantummeta_license.core.license_manager import LicenseManager, LicenseData


class TestLicenseData:
    """Test LicenseData model validation."""
    
    def test_valid_license_data(self, sample_license_data):
        """Test valid license data creation."""
        license_obj = LicenseData(**sample_license_data)
        
        assert license_obj.package == sample_license_data["package"]
        assert license_obj.user == sample_license_data["user"]
        assert license_obj.machine_id == sample_license_data["machine_id"]
        assert license_obj.features == sample_license_data["features"]
    
    def test_invalid_date_format(self, sample_license_data):
        """Test invalid date format validation."""
        invalid_data = sample_license_data.copy()
        invalid_data["issued"] = "invalid-date"
        
        with pytest.raises(ValueError, match="Date must be in ISO format"):
            LicenseData(**invalid_data)
    
    def test_empty_package_name(self, sample_license_data):
        """Test empty package name validation."""
        invalid_data = sample_license_data.copy()
        invalid_data["package"] = ""
        
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            LicenseData(**invalid_data)
    
    def test_is_expired_false(self, sample_license_data):
        """Test license expiration check for valid license."""
        license_obj = LicenseData(**sample_license_data)
        assert not license_obj.is_expired()
    
    def test_is_expired_true(self, expired_license_data):
        """Test license expiration check for expired license."""
        license_obj = LicenseData(**expired_license_data)
        assert license_obj.is_expired()
    
    def test_has_feature(self, sample_license_data):
        """Test feature checking."""
        license_obj = LicenseData(**sample_license_data)
        
        assert license_obj.has_feature("core")
        assert license_obj.has_feature("pro")
        assert license_obj.has_feature("CORE")  # Case insensitive
        assert not license_obj.has_feature("enterprise")


class TestLicenseManager:
    """Test LicenseManager functionality."""
    
    def test_create_license_basic(self, license_manager):
        """Test basic license creation."""
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com"
        )
        
        assert license_data["package"] == "test-package"
        assert license_data["user"] == "test@example.com"
        assert "machine_id" in license_data
        assert "issued" in license_data
        assert "expires" in license_data
        assert license_data["features"] == ["core"]
    
    def test_create_license_with_features(self, license_manager):
        """Test license creation with custom features."""
        features = ["core", "pro", "enterprise"]
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            features=features
        )
        
        assert license_data["features"] == features
    
    def test_create_license_with_validity(self, license_manager):
        """Test license creation with custom validity period."""
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            validity_days=180
        )
        
        issued_date = datetime.fromisoformat(license_data["issued"])
        expires_date = datetime.fromisoformat(license_data["expires"])
        
        expected_expires = issued_date + timedelta(days=180)
        assert abs((expires_date - expected_expires).total_seconds()) < 1
    
    def test_create_license_with_signature(self, license_manager, signing_keys):
        """Test license creation with signature."""
        private_key, _ = signing_keys
        
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            private_key_bytes=private_key
        )
        
        assert "signature" in license_data
        assert isinstance(license_data["signature"], str)
    
    def test_save_and_activate_license(self, license_manager, sample_license_data, temp_config_dir):
        """Test saving and activating a license."""
        # Save license to file
        license_file = temp_config_dir / "test.qkey"
        license_manager.save_license_file(sample_license_data, str(license_file))
        
        assert license_file.exists()
        
        # Activate license
        with pytest.raises(ValueError, match="License is not valid for this machine"):
            # Should fail because machine_id doesn't match
            license_manager.activate_license(str(license_file))
    
    def test_activate_license_with_correct_machine_id(self, license_manager, temp_config_dir):
        """Test activating license with correct machine ID."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Create license with current machine ID
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            machine_id=get_machine_id()
        )
        
        # Save to file
        license_file = temp_config_dir / "test.qkey"
        license_manager.save_license_file(license_data, str(license_file))
        
        # Activate should succeed
        assert license_manager.activate_license(str(license_file))
        
        # License should now be available
        stored_license = license_manager.get_license("test-package")
        assert stored_license is not None
        assert stored_license.package == "test-package"
    
    def test_activate_expired_license(self, license_manager, expired_license_data, temp_config_dir):
        """Test activating an expired license."""
        license_file = temp_config_dir / "expired.qkey"
        license_manager.save_license_file(expired_license_data, str(license_file))
        
        with pytest.raises(ValueError, match="License has expired"):
            license_manager.activate_license(str(license_file))
    
    def test_get_nonexistent_license(self, license_manager):
        """Test getting a license that doesn't exist."""
        license_obj = license_manager.get_license("nonexistent-package")
        assert license_obj is None
    
    def test_validate_license_success(self, license_manager):
        """Test successful license validation."""
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
        
        # Validation should succeed
        assert license_manager.validate_license("test-package")
        assert license_manager.validate_license("test-package", ["core"])
        assert license_manager.validate_license("test-package", ["core", "pro"])
    
    def test_validate_license_missing_features(self, license_manager):
        """Test license validation with missing features."""
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
        
        # Should fail when requiring missing feature
        assert not license_manager.validate_license("test-package", ["enterprise"])
    
    def test_list_licenses(self, license_manager):
        """Test listing installed licenses."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Initially no licenses
        licenses = license_manager.list_licenses()
        assert len(licenses) == 0
        
        # Add a license
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            machine_id=get_machine_id()
        )
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(license_data, str(license_file))
        
        # Should now show one license
        licenses = license_manager.list_licenses()
        assert len(licenses) == 1
        assert licenses[0]["package"] == "test-package"
        assert licenses[0]["user"] == "test@example.com"
    
    def test_remove_license(self, license_manager):
        """Test removing a license."""
        from quantummeta_license.core.hardware import get_machine_id
        
        # Add a license
        license_data = license_manager.create_license(
            package="test-package",
            user="test@example.com",
            machine_id=get_machine_id()
        )
        
        license_file = license_manager._get_license_path("test-package")
        license_manager.save_license_file(license_data, str(license_file))
        
        # Verify it exists
        assert license_manager.get_license("test-package") is not None
        
        # Remove it
        assert license_manager.remove_license("test-package")
        
        # Should no longer exist
        assert license_manager.get_license("test-package") is None
    
    def test_remove_nonexistent_license(self, license_manager):
        """Test removing a license that doesn't exist."""
        # Should return False but not error
        assert not license_manager.remove_license("nonexistent-package")
