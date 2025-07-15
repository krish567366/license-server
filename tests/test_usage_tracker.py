"""Tests for usage tracking and grace period functionality."""

import pytest
from datetime import datetime, timedelta
from quantummeta_license.core.usage_tracker import UsageTracker


class TestUsageTracker:
    """Test usage tracking functionality."""
    
    def test_first_use_tracking(self, usage_tracker):
        """Test first use date tracking."""
        package = "test-package"
        
        # Initially no first use date
        assert usage_tracker.get_first_use_date(package) is None
        
        # Record first use
        first_use = usage_tracker.record_first_use(package)
        assert isinstance(first_use, datetime)
        
        # Should return the same date on subsequent calls
        first_use2 = usage_tracker.record_first_use(package)
        assert first_use == first_use2
        
        # Should be able to retrieve it
        retrieved = usage_tracker.get_first_use_date(package)
        assert retrieved == first_use
    
    def test_grace_period_not_expired(self, usage_tracker):
        """Test grace period when not expired."""
        package = "test-package"
        
        # Just recorded, should not be expired
        usage_tracker.record_first_use(package)
        assert not usage_tracker.is_grace_period_expired(package, grace_days=7)
    
    def test_grace_period_expired(self, usage_tracker):
        """Test grace period when expired."""
        package = "test-package"
        
        # Manually set an old first use date
        old_date = datetime.now() - timedelta(days=10)
        log_data = {
            package: {
                "first_use": old_date.isoformat(),
                "last_check": old_date.isoformat()
            }
        }
        usage_tracker._save_usage_log(log_data)
        
        # Should be expired with 7-day grace period
        assert usage_tracker.is_grace_period_expired(package, grace_days=7)
    
    def test_grace_period_info(self, usage_tracker):
        """Test grace period information retrieval."""
        package = "test-package"
        
        # Record first use
        usage_tracker.record_first_use(package)
        
        # Get grace period info
        info = usage_tracker.get_grace_period_info(package, grace_days=7)
        
        assert info["package_name"] == package
        assert "first_use" in info
        assert "expiry_date" in info
        assert info["is_expired"] is False
        assert info["days_remaining"] >= 6  # Should be close to 7
        assert info["grace_days"] == 7
    
    def test_grace_period_info_expired(self, usage_tracker):
        """Test grace period info for expired period."""
        package = "test-package"
        
        # Set expired first use
        old_date = datetime.now() - timedelta(days=10)
        log_data = {
            package: {
                "first_use": old_date.isoformat(),
                "last_check": old_date.isoformat()
            }
        }
        usage_tracker._save_usage_log(log_data)
        
        info = usage_tracker.get_grace_period_info(package, grace_days=7)
        
        assert info["is_expired"] is True
        assert info["days_remaining"] == 0
        assert info["hours_remaining"] == 0
    
    def test_clear_usage_data_specific_package(self, usage_tracker):
        """Test clearing usage data for specific package."""
        package1 = "test-package-1"
        package2 = "test-package-2"
        
        # Record usage for both packages
        usage_tracker.record_first_use(package1)
        usage_tracker.record_first_use(package2)
        
        # Verify both exist
        assert usage_tracker.get_first_use_date(package1) is not None
        assert usage_tracker.get_first_use_date(package2) is not None
        
        # Clear only package1
        usage_tracker.clear_usage_data(package1)
        
        # package1 should be cleared, package2 should remain
        assert usage_tracker.get_first_use_date(package1) is None
        assert usage_tracker.get_first_use_date(package2) is not None
    
    def test_clear_usage_data_all(self, usage_tracker):
        """Test clearing all usage data."""
        package1 = "test-package-1"
        package2 = "test-package-2"
        
        # Record usage for both packages
        usage_tracker.record_first_use(package1)
        usage_tracker.record_first_use(package2)
        
        # Clear all data
        usage_tracker.clear_usage_data()
        
        # Both should be cleared
        assert usage_tracker.get_first_use_date(package1) is None
        assert usage_tracker.get_first_use_date(package2) is None
    
    def test_get_all_usage_data(self, usage_tracker):
        """Test retrieving all usage data."""
        package1 = "test-package-1"
        package2 = "test-package-2"
        
        # Record usage for both packages
        usage_tracker.record_first_use(package1)
        usage_tracker.record_first_use(package2)
        
        # Get all data
        all_data = usage_tracker.get_all_usage_data()
        
        assert package1 in all_data
        assert package2 in all_data
        assert "first_use" in all_data[package1]
        assert "last_check" in all_data[package1]
    
    def test_file_persistence(self, usage_tracker):
        """Test that usage data persists across instances."""
        package = "test-package"
        
        # Record first use
        first_use = usage_tracker.record_first_use(package)
        
        # Create new tracker instance (should read from same file)
        new_tracker = UsageTracker()
        new_tracker.config_dir = usage_tracker.config_dir
        new_tracker.usage_log_file = usage_tracker.usage_log_file
        
        # Should retrieve the same first use date
        retrieved = new_tracker.get_first_use_date(package)
        assert retrieved == first_use
