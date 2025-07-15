"""License management and operations."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import platformdirs
from pydantic import BaseModel, Field, field_validator

from .encryption import LicenseEncryption, LicenseSignature
from .hardware import get_machine_id, verify_machine_id


class LicenseData(BaseModel):
    """Pydantic model for license data validation."""
    
    package: str = Field(..., description="Package name")
    user: str = Field(..., description="User email or ID")
    machine_id: str = Field(..., description="Machine hardware fingerprint")
    issued: str = Field(..., description="Issue date (ISO format)")
    expires: str = Field(..., description="Expiration date (ISO format)")
    features: List[str] = Field(default_factory=list, description="Enabled features")
    signature: Optional[str] = Field(None, description="Ed25519 signature")
    
    @field_validator('issued', 'expires')
    @classmethod
    def validate_dates(cls, v):
        """Validate ISO date format."""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    
    @field_validator('package')
    @classmethod
    def validate_package_name(cls, v):
        """Validate package name."""
        if not v or not v.strip():
            raise ValueError("Package name cannot be empty")
        return v.strip().lower()
    
    def is_expired(self) -> bool:
        """Check if the license is expired."""
        expiry_date = datetime.fromisoformat(self.expires)
        return datetime.now() > expiry_date
    
    def has_feature(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return feature.lower() in [f.lower() for f in self.features]


class LicenseManager:
    """Manages license operations including storage, validation, and activation."""
    
    def __init__(self):
        self.config_dir = Path(platformdirs.user_config_dir("quantummeta"))
        self.licenses_dir = self.config_dir / "licenses"
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.licenses_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_license_path(self, package_name: str) -> Path:
        """Get the path for a package's license file."""
        return self.licenses_dir / f"{package_name.lower()}.qkey"
    
    def create_license(
        self,
        package: str,
        user: str,
        machine_id: Optional[str] = None,
        features: Optional[List[str]] = None,
        validity_days: int = 365,
        private_key_bytes: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Create a new license.
        
        Args:
            package: Package name
            user: User email or ID
            machine_id: Target machine ID (if None, uses current machine)
            features: List of enabled features
            validity_days: License validity in days
            private_key_bytes: Private key for signing (optional)
            
        Returns:
            dict: License data
        """
        if machine_id is None:
            machine_id = get_machine_id()
        
        if features is None:
            features = ["core"]
        
        now = datetime.now()
        expires = now + timedelta(days=validity_days)
        
        license_data = {
            "package": package.lower().strip(),
            "user": user.strip(),
            "machine_id": machine_id,
            "issued": now.isoformat(),
            "expires": expires.isoformat(),
            "features": features
        }
        
        # Add signature if private key is provided
        if private_key_bytes:
            signature = LicenseSignature.sign_license(license_data, private_key_bytes)
            license_data["signature"] = signature
        
        # Validate the license data
        LicenseData(**license_data)
        
        return license_data
    
    def save_license_file(self, license_data: Dict[str, Any], file_path: str) -> None:
        """
        Save a license to an encrypted file.
        
        Args:
            license_data: License data to save
            file_path: Path to save the license file
        """
        LicenseEncryption.create_license_file(license_data, file_path)
    
    def activate_license(self, license_file_path: str) -> bool:
        """
        Activate a license by copying it to the licenses directory.
        
        Args:
            license_file_path: Path to the license file to activate
            
        Returns:
            bool: True if activation successful
            
        Raises:
            ValueError: If license is invalid or incompatible
        """
        try:
            # Read and validate the license
            license_data = LicenseEncryption.read_license_file(license_file_path)
            license_obj = LicenseData(**license_data)
            
            # Check if license is expired
            if license_obj.is_expired():
                raise ValueError("License has expired")
            
            # Check machine compatibility
            if not verify_machine_id(license_obj.machine_id):
                raise ValueError("License is not valid for this machine")
            
            # Copy to licenses directory
            target_path = self._get_license_path(license_obj.package)
            LicenseEncryption.create_license_file(license_data, str(target_path))
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to activate license: {e}")
    
    def get_license(self, package_name: str) -> Optional[LicenseData]:
        """
        Get the license for a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            LicenseData or None: License data if found and valid
        """
        license_path = self._get_license_path(package_name)
        
        if not license_path.exists():
            return None
        
        try:
            license_data = LicenseEncryption.read_license_file(str(license_path))
            return LicenseData(**license_data)
        except Exception:
            return None
    
    def validate_license(
        self,
        package_name: str,
        required_features: Optional[List[str]] = None,
        public_key_bytes: Optional[bytes] = None
    ) -> bool:
        """
        Validate a license for a package.
        
        Args:
            package_name: Name of the package
            required_features: List of required features
            public_key_bytes: Public key for signature verification
            
        Returns:
            bool: True if license is valid
        """
        license_obj = self.get_license(package_name)
        
        if license_obj is None:
            return False
        
        # Check expiration
        if license_obj.is_expired():
            return False
        
        # Check machine compatibility
        if not verify_machine_id(license_obj.machine_id):
            return False
        
        # Check required features
        if required_features:
            for feature in required_features:
                if not license_obj.has_feature(feature):
                    return False
        
        # Verify signature if public key provided
        if public_key_bytes and license_obj.signature:
            license_dict = license_obj.dict()
            if not LicenseSignature.verify_signature(license_dict, public_key_bytes):
                return False
        
        return True
    
    def list_licenses(self) -> List[Dict[str, Any]]:
        """
        List all installed licenses.
        
        Returns:
            list: List of license information
        """
        licenses = []
        
        for license_file in self.licenses_dir.glob("*.qkey"):
            try:
                package_name = license_file.stem
                license_obj = self.get_license(package_name)
                
                if license_obj:
                    licenses.append({
                        "package": license_obj.package,
                        "user": license_obj.user,
                        "issued": license_obj.issued,
                        "expires": license_obj.expires,
                        "features": license_obj.features,
                        "is_expired": license_obj.is_expired(),
                        "is_valid": self.validate_license(package_name)
                    })
            except Exception:
                continue
        
        return licenses
    
    def remove_license(self, package_name: str) -> bool:
        """
        Remove a license for a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            bool: True if license was removed
        """
        license_path = self._get_license_path(package_name)
        
        if license_path.exists():
            try:
                license_path.unlink()
                return True
            except Exception:
                return False
        
        return False
