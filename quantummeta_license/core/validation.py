"""Core validation logic for license and grace period checks."""

import os
from typing import List, Optional
from .license_manager import LicenseManager
from .usage_tracker import UsageTracker


class LicenseError(Exception):
    """Base exception for license-related errors."""
    pass


class LicenseExpiredError(LicenseError):
    """Raised when a license has expired."""
    pass


class LicenseNotFoundError(LicenseError):
    """Raised when no license is found and grace period has expired."""
    pass


class InvalidLicenseError(LicenseError):
    """Raised when a license is invalid or corrupted."""
    pass


class FeatureNotLicensedError(LicenseError):
    """Raised when a required feature is not licensed."""
    pass


def is_development_mode() -> bool:
    """Check if development mode is enabled via environment variable."""
    return os.getenv("QUANTUMMETA_DEV", "").lower() in ("1", "true", "yes", "on")


def validate_or_grace(
    package_name: str,
    required_features: Optional[List[str]] = None,
    grace_days: int = 7,
    public_key_bytes: Optional[bytes] = None
) -> bool:
    """
    Validate license or allow grace period usage.
    
    This is the main entry point for license validation. It will:
    1. Check if development mode is enabled (bypass all checks)
    2. Try to validate an existing license
    3. Fall back to grace period if no license exists
    4. Raise appropriate errors if validation fails
    
    Args:
        package_name: Name of the package to validate
        required_features: List of required features (optional)
        grace_days: Number of grace period days (default: 7)
        public_key_bytes: Public key for signature verification (optional)
        
    Returns:
        bool: True if validation successful
        
    Raises:
        LicenseError: Various license-related errors
    """
    # Development mode bypass
    if is_development_mode():
        return True
    
    package_name = package_name.lower().strip()
    
    license_manager = LicenseManager()
    usage_tracker = UsageTracker()
    
    # Try to validate existing license first
    try:
        if license_manager.validate_license(package_name, required_features, public_key_bytes):
            return True
    except Exception:
        pass  # Continue to grace period check
    
    # Check if we have a license but it's invalid
    license_obj = license_manager.get_license(package_name)
    if license_obj:
        if license_obj.is_expired():
            raise LicenseExpiredError(f"License for '{package_name}' has expired on {license_obj.expires}")
        
        # Check machine compatibility
        from .hardware import verify_machine_id
        if not verify_machine_id(license_obj.machine_id):
            raise InvalidLicenseError(f"License for '{package_name}' is not valid for this machine")
        
        # Check required features
        if required_features:
            missing_features = []
            for feature in required_features:
                if not license_obj.has_feature(feature):
                    missing_features.append(feature)
            
            if missing_features:
                raise FeatureNotLicensedError(
                    f"License for '{package_name}' does not include required features: {missing_features}"
                )
    
    # No valid license found, check grace period
    if usage_tracker.is_grace_period_expired(package_name, grace_days):
        grace_info = usage_tracker.get_grace_period_info(package_name, grace_days)
        raise LicenseNotFoundError(
            f"Grace period for '{package_name}' expired on {grace_info['expiry_date']}. "
            f"Please activate a valid license."
        )
    
    # Grace period is active, record usage and allow access
    grace_info = usage_tracker.get_grace_period_info(package_name, grace_days)
    
    # Print grace period warning
    if grace_info['days_remaining'] <= 1:
        print(f"⚠️  Grace period for '{package_name}' expires in {grace_info['hours_remaining']} hours!")
    else:
        print(f"ℹ️  Grace period for '{package_name}' - {grace_info['days_remaining']} days remaining")
    
    return True


def check_license_status(package_name: str) -> dict:
    """
    Get detailed license status information.
    
    Args:
        package_name: Name of the package
        
    Returns:
        dict: Detailed status information
    """
    package_name = package_name.lower().strip()
    
    if is_development_mode():
        return {
            "status": "development_mode",
            "message": "Development mode is enabled - all checks bypassed",
            "has_license": False,
            "in_grace_period": False
        }
    
    license_manager = LicenseManager()
    usage_tracker = UsageTracker()
    
    # Check for existing license
    license_obj = license_manager.get_license(package_name)
    has_license = license_obj is not None
    
    if has_license:
        is_valid = license_manager.validate_license(package_name)
        
        status_info = {
            "status": "licensed" if is_valid else "invalid_license",
            "has_license": True,
            "in_grace_period": False,
            "license_info": {
                "user": license_obj.user,
                "issued": license_obj.issued,
                "expires": license_obj.expires,
                "features": license_obj.features,
                "is_expired": license_obj.is_expired()
            }
        }
        
        if not is_valid:
            if license_obj.is_expired():
                status_info["message"] = f"License expired on {license_obj.expires}"
            else:
                from .hardware import verify_machine_id
                if not verify_machine_id(license_obj.machine_id):
                    status_info["message"] = "License is not valid for this machine"
                else:
                    status_info["message"] = "License validation failed"
        else:
            status_info["message"] = "Valid license found"
        
        return status_info
    
    # No license, check grace period
    grace_info = usage_tracker.get_grace_period_info(package_name)
    
    return {
        "status": "grace_period" if not grace_info["is_expired"] else "expired",
        "message": f"Grace period {'active' if not grace_info['is_expired'] else 'expired'}",
        "has_license": False,
        "in_grace_period": not grace_info["is_expired"],
        "grace_info": grace_info
    }
