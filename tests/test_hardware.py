"""Tests for hardware fingerprinting functionality."""

import pytest
from unittest.mock import patch, mock_open
from quantummeta_license.core.hardware import (
    get_mac_address,
    get_disk_serial,
    get_system_uuid,
    get_machine_id,
    verify_machine_id
)


class TestHardwareFingerprinting:
    """Test hardware fingerprinting functions."""
    
    def test_get_mac_address(self):
        """Test MAC address retrieval."""
        mac = get_mac_address()
        assert isinstance(mac, str)
        assert len(mac) > 0
        # Should be in XX:XX:XX:XX:XX:XX format or "unknown"
        assert mac == "unknown" or len(mac.split(':')) == 6
    
    def test_get_disk_serial(self):
        """Test disk serial retrieval."""
        serial = get_disk_serial()
        assert isinstance(serial, str)
        assert len(serial) > 0
    
    def test_get_system_uuid(self):
        """Test system UUID retrieval."""
        uuid = get_system_uuid()
        assert isinstance(uuid, str)
        assert len(uuid) > 0
    
    def test_get_machine_id(self):
        """Test machine ID generation."""
        machine_id = get_machine_id()
        assert isinstance(machine_id, str)
        assert len(machine_id) == 32  # First 32 chars of SHA-256
        
        # Should be consistent
        machine_id2 = get_machine_id()
        assert machine_id == machine_id2
    
    def test_verify_machine_id_same(self):
        """Test machine ID verification with same ID."""
        machine_id = get_machine_id()
        assert verify_machine_id(machine_id) is True
    
    def test_verify_machine_id_different(self):
        """Test machine ID verification with different ID."""
        fake_id = "different-machine-id-12345"
        assert verify_machine_id(fake_id) is False
    
    @patch('platform.system', return_value='Windows')
    @patch('subprocess.run')
    def test_get_disk_serial_windows(self, mock_run):
        """Test disk serial retrieval on Windows."""
        mock_run.return_value.stdout = "SerialNumber\nTEST123456\n"
        mock_run.return_value.returncode = 0
        
        from quantummeta_license.core.hardware import get_disk_serial
        serial = get_disk_serial()
        assert serial == "TEST123456"
    
    @patch('platform.system', return_value='Linux')
    @patch('builtins.open', mock_open(read_data='LINUX_SERIAL_123'))
    def test_get_disk_serial_linux(self):
        """Test disk serial retrieval on Linux."""
        from quantummeta_license.core.hardware import get_disk_serial
        with patch('subprocess.run', side_effect=Exception("No lsblk")):
            serial = get_disk_serial()
            assert serial == "LINUX_SERIAL_123"
    
    @patch('platform.system', return_value='Windows')
    @patch('subprocess.run')
    def test_get_system_uuid_windows(self, mock_run):
        """Test system UUID retrieval on Windows."""
        mock_run.return_value.stdout = "UUID\n12345678-1234-1234-1234-123456789ABC\n"
        mock_run.return_value.returncode = 0
        
        from quantummeta_license.core.hardware import get_system_uuid
        uuid = get_system_uuid()
        assert uuid == "12345678-1234-1234-1234-123456789ABC"
    
    @patch('platform.system', return_value='Linux')
    @patch('builtins.open', mock_open(read_data='linux-uuid-12345'))
    def test_get_system_uuid_linux(self):
        """Test system UUID retrieval on Linux."""
        from quantummeta_license.core.hardware import get_system_uuid
        uuid = get_system_uuid()
        assert uuid == "linux-uuid-12345"
