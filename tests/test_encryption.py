"""Tests for encryption and signature functionality."""

import pytest
import tempfile
from pathlib import Path
from quantummeta_license.core.encryption import LicenseEncryption, LicenseSignature


class TestLicenseEncryption:
    """Test license encryption functionality."""
    
    def test_encrypt_decrypt_roundtrip(self, sample_license_data):
        """Test encryption and decryption roundtrip."""
        password = "test-password"
        
        # Encrypt
        encrypted_data = LicenseEncryption.encrypt_license(sample_license_data, password)
        assert isinstance(encrypted_data, bytes)
        assert len(encrypted_data) > 0
        
        # Decrypt
        decrypted_data = LicenseEncryption.decrypt_license(encrypted_data, password)
        assert decrypted_data == sample_license_data
    
    def test_encrypt_decrypt_default_password(self, sample_license_data):
        """Test encryption with default password."""
        # Encrypt with default password
        encrypted_data = LicenseEncryption.encrypt_license(sample_license_data)
        
        # Decrypt with default password
        decrypted_data = LicenseEncryption.decrypt_license(encrypted_data)
        assert decrypted_data == sample_license_data
    
    def test_decrypt_wrong_password(self, sample_license_data):
        """Test decryption with wrong password fails."""
        # Encrypt with one password
        encrypted_data = LicenseEncryption.encrypt_license(sample_license_data, "password1")
        
        # Try to decrypt with different password
        with pytest.raises(ValueError, match="Failed to decrypt license"):
            LicenseEncryption.decrypt_license(encrypted_data, "password2")
    
    def test_create_read_license_file(self, sample_license_data, temp_config_dir):
        """Test creating and reading license files."""
        license_file = temp_config_dir / "test.qkey"
        password = "test-password"
        
        # Create license file
        LicenseEncryption.create_license_file(sample_license_data, str(license_file), password)
        assert license_file.exists()
        
        # Read license file
        read_data = LicenseEncryption.read_license_file(str(license_file), password)
        assert read_data == sample_license_data
    
    def test_encrypt_decrypt_different_data_types(self):
        """Test encryption with different data types in license."""
        license_data = {
            "string": "test",
            "number": 123,
            "boolean": True,
            "list": ["a", "b", "c"],
            "dict": {"nested": "value"}
        }
        
        encrypted_data = LicenseEncryption.encrypt_license(license_data)
        decrypted_data = LicenseEncryption.decrypt_license(encrypted_data)
        
        assert decrypted_data == license_data


class TestLicenseSignature:
    """Test license signature functionality."""
    
    def test_generate_keypair(self):
        """Test Ed25519 keypair generation."""
        private_key, public_key = LicenseSignature.generate_keypair()
        
        assert isinstance(private_key, bytes)
        assert isinstance(public_key, bytes)
        assert len(private_key) == 32  # Ed25519 private key is 32 bytes
        assert len(public_key) == 32   # Ed25519 public key is 32 bytes
    
    def test_sign_verify_roundtrip(self, sample_license_data, signing_keys):
        """Test signing and verification roundtrip."""
        private_key, public_key = signing_keys
        
        # Sign license
        signature = LicenseSignature.sign_license(sample_license_data, private_key)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Add signature to license data
        signed_data = sample_license_data.copy()
        signed_data["signature"] = signature
        
        # Verify signature
        is_valid = LicenseSignature.verify_signature(signed_data, public_key)
        assert is_valid is True
    
    def test_verify_invalid_signature(self, sample_license_data, signing_keys):
        """Test verification with invalid signature."""
        _, public_key = signing_keys
        
        # Create data with fake signature
        signed_data = sample_license_data.copy()
        signed_data["signature"] = "fake-signature-not-valid"
        
        # Verification should fail
        is_valid = LicenseSignature.verify_signature(signed_data, public_key)
        assert is_valid is False
    
    def test_verify_wrong_public_key(self, signed_license_data):
        """Test verification with wrong public key."""
        # Generate different keypair
        _, wrong_public_key = LicenseSignature.generate_keypair()
        
        # Verification should fail
        is_valid = LicenseSignature.verify_signature(signed_license_data, wrong_public_key)
        assert is_valid is False
    
    def test_verify_modified_data(self, sample_license_data, signing_keys):
        """Test verification fails when data is modified."""
        private_key, public_key = signing_keys
        
        # Sign original data
        signature = LicenseSignature.sign_license(sample_license_data, private_key)
        
        # Modify the data after signing
        modified_data = sample_license_data.copy()
        modified_data["user"] = "modified@example.com"
        modified_data["signature"] = signature
        
        # Verification should fail
        is_valid = LicenseSignature.verify_signature(modified_data, public_key)
        assert is_valid is False
    
    def test_verify_no_signature(self, sample_license_data, signing_keys):
        """Test verification when no signature is present."""
        _, public_key = signing_keys
        
        # Verification should fail when no signature
        is_valid = LicenseSignature.verify_signature(sample_license_data, public_key)
        assert is_valid is False
    
    def test_sign_excludes_signature_field(self, signing_keys):
        """Test that signing excludes the signature field from the data."""
        private_key, public_key = signing_keys
        
        # Data with existing signature
        data_with_signature = {
            "package": "test",
            "user": "test@example.com",
            "signature": "old-signature"
        }
        
        # Sign the data (should ignore existing signature)
        new_signature = LicenseSignature.sign_license(data_with_signature, private_key)
        
        # Create properly signed data
        properly_signed = data_with_signature.copy()
        properly_signed["signature"] = new_signature
        
        # Verification should pass
        is_valid = LicenseSignature.verify_signature(properly_signed, public_key)
        assert is_valid is True
