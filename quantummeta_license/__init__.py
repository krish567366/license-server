"""
QuantumMeta License Manager

A universal, secure licensing system for the QuantumMeta ecosystem.
"""

from .core.validation import (
    validate_or_grace, 
    LicenseError, 
    LicenseExpiredError,
    LicenseNotFoundError,
    InvalidLicenseError,
    FeatureNotLicensedError
)
from .core.license_manager import LicenseManager
from .core.hardware import get_machine_id

__version__ = "1.0.0"
__author__ = "QuantumMeta Team"
__email__ = "info@quantummeta.com"

__all__ = [
    "validate_or_grace",
    "LicenseError", 
    "LicenseExpiredError",
    "LicenseNotFoundError",
    "InvalidLicenseError", 
    "FeatureNotLicensedError",
    "LicenseManager",
    "get_machine_id",
]
