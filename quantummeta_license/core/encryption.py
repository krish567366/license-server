"""License file encryption and decryption utilities."""

import base64
import hashlib
import secrets
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json


class LicenseEncryption:
    """Handles encryption and decryption of license files."""
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: The password to derive the key from
            salt: Random salt for key derivation
            
        Returns:
            bytes: The derived 32-byte key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    @staticmethod
    def encrypt_license(license_data: Dict[str, Any], password: str = "quantummeta") -> bytes:
        """
        Encrypt license data using AES-256-GCM.
        
        Args:
            license_data: The license data to encrypt
            password: Password for encryption (default: "quantummeta")
            
        Returns:
            bytes: Encrypted license data
        """
        # Serialize license data to JSON
        json_data = json.dumps(license_data, indent=2).encode('utf-8')
        
        # Generate random salt and nonce
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        
        # Derive encryption key
        key = LicenseEncryption.derive_key(password, salt)
        
        # Encrypt using AES-256-GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(json_data) + encryptor.finalize()
        
        # Combine salt, nonce, authentication tag, and ciphertext
        encrypted_data = salt + nonce + encryptor.tag + ciphertext
        
        return encrypted_data
    
    @staticmethod
    def decrypt_license(encrypted_data: bytes, password: str = "quantummeta") -> Dict[str, Any]:
        """
        Decrypt license data using AES-256-GCM.
        
        Args:
            encrypted_data: The encrypted license data
            password: Password for decryption (default: "quantummeta")
            
        Returns:
            dict: Decrypted license data
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            # Extract components
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:28]
            tag = encrypted_data[28:44]
            ciphertext = encrypted_data[44:]
            
            # Derive decryption key
            key = LicenseEncryption.derive_key(password, salt)
            
            # Decrypt using AES-256-GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Parse JSON data
            license_data = json.loads(plaintext.decode('utf-8'))
            
            return license_data
            
        except Exception as e:
            raise ValueError(f"Failed to decrypt license: {e}")
    
    @staticmethod
    def create_license_file(license_data: Dict[str, Any], file_path: str, password: str = "quantummeta") -> None:
        """
        Create an encrypted license file.
        
        Args:
            license_data: The license data to encrypt
            file_path: Path to save the encrypted license file
            password: Password for encryption
        """
        encrypted_data = LicenseEncryption.encrypt_license(license_data, password)
        
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
    
    @staticmethod
    def read_license_file(file_path: str, password: str = "quantummeta") -> Dict[str, Any]:
        """
        Read and decrypt a license file.
        
        Args:
            file_path: Path to the encrypted license file
            password: Password for decryption
            
        Returns:
            dict: Decrypted license data
        """
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        return LicenseEncryption.decrypt_license(encrypted_data, password)


class LicenseSignature:
    """Handles Ed25519 digital signatures for license verification."""
    
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]:
        """
        Generate a new Ed25519 keypair.
        
        Returns:
            tuple: (private_key_bytes, public_key_bytes)
        """
        from cryptography.hazmat.primitives.asymmetric import ed25519
        
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return private_bytes, public_bytes
    
    @staticmethod
    def sign_license(license_data: Dict[str, Any], private_key_bytes: bytes) -> str:
        """
        Sign license data with Ed25519 private key.
        
        Args:
            license_data: License data to sign
            private_key_bytes: Ed25519 private key bytes
            
        Returns:
            str: Base64-encoded signature
        """
        from cryptography.hazmat.primitives.asymmetric import ed25519
        
        # Create a copy without the signature field
        data_to_sign = {k: v for k, v in license_data.items() if k != 'signature'}
        
        # Serialize to canonical JSON
        json_str = json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'))
        
        # Load private key and sign
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        signature = private_key.sign(json_str.encode('utf-8'))
        
        return base64.b64encode(signature).decode('ascii')
    
    @staticmethod
    def verify_signature(license_data: Dict[str, Any], public_key_bytes: bytes) -> bool:
        """
        Verify license signature with Ed25519 public key.
        
        Args:
            license_data: License data with signature
            public_key_bytes: Ed25519 public key bytes
            
        Returns:
            bool: True if signature is valid
        """
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.exceptions import InvalidSignature
        
        try:
            signature_b64 = license_data.get('signature')
            if not signature_b64:
                return False
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Create data to verify (without signature)
            data_to_verify = {k: v for k, v in license_data.items() if k != 'signature'}
            json_str = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
            
            # Load public key and verify
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature, json_str.encode('utf-8'))
            
            return True
            
        except (InvalidSignature, ValueError, KeyError):
            return False
