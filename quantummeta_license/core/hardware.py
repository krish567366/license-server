"""Hardware fingerprinting for machine locking."""

import hashlib
import platform
import uuid
from typing import Optional
import psutil
import os
import json
from pathlib import Path


# Cache for machine ID to ensure consistency
_MACHINE_ID_CACHE = None


def _get_cache_file() -> Path:
    """Get the path to the machine ID cache file."""
    try:
        import platformdirs
        cache_dir = Path(platformdirs.user_cache_dir("quantummeta"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "machine_id.json"
    except Exception:
        # Fallback to temp directory
        import tempfile
        return Path(tempfile.gettempdir()) / "quantummeta_machine_id.json"


def _load_cached_machine_id() -> Optional[str]:
    """Load machine ID from cache if available."""
    try:
        cache_file = _get_cache_file()
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get('machine_id')
    except Exception:
        pass
    return None


def _save_cached_machine_id(machine_id: str) -> None:
    """Save machine ID to cache."""
    try:
        cache_file = _get_cache_file()
        cache_data = {'machine_id': machine_id}
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
    except Exception:
        pass  # Fail silently if we can't cache


def get_mac_address() -> str:
    """Get the MAC address of the first network interface."""
    try:
        # Get MAC address using uuid.getnode()
        mac = uuid.getnode()
        mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        return mac_str
    except Exception:
        return "unknown"


def get_disk_serial() -> str:
    """Get the serial number of the primary disk."""
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ["wmic", "diskdrive", "get", "serialnumber"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                serial = line.strip()
                if serial and serial != "SerialNumber":
                    return serial
        else:
            # For Unix-like systems, try different approaches
            try:
                # Try lsblk first
                import subprocess
                result = subprocess.run(
                    ["lsblk", "-o", "SERIAL", "-n"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                serials = [s.strip() for s in result.stdout.split('\n') if s.strip()]
                if serials:
                    return serials[0]
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
                
            # Fallback: try to read from /sys
            try:
                with open("/sys/block/sda/device/serial", "r") as f:
                    return f.read().strip()
            except (FileNotFoundError, PermissionError):
                pass
                
    except Exception:
        pass
    
    return "unknown"


def get_system_uuid() -> str:
    """Get system UUID."""
    try:
        if platform.system() == "Windows":
            import subprocess
            result = subprocess.run(
                ["wmic", "csproduct", "get", "uuid"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                system_uuid = line.strip()
                if system_uuid and system_uuid != "UUID":
                    return system_uuid
        else:
            # Try different locations for system UUID on Unix-like systems
            uuid_files = [
                "/sys/class/dmi/id/product_uuid",
                "/proc/sys/kernel/random/uuid"
            ]
            
            for uuid_file in uuid_files:
                try:
                    with open(uuid_file, "r") as f:
                        system_uuid = f.read().strip()
                        if system_uuid:
                            return system_uuid
                except (FileNotFoundError, PermissionError):
                    continue
    except Exception:
        pass
    
    # Fallback to Python's uuid if system UUID is not available
    return str(uuid.uuid4())


def get_machine_id() -> str:
    """
    Generate a unique machine identifier based on hardware characteristics.
    
    This combines multiple hardware identifiers to create a unique fingerprint
    that should remain stable across reboots but change if the hardware changes.
    The result is cached to ensure consistency within the same environment.
    
    Returns:
        str: A unique machine identifier hash
    """
    global _MACHINE_ID_CACHE
    
    # Return cached value if available
    if _MACHINE_ID_CACHE:
        return _MACHINE_ID_CACHE
    
    # Try to load from persistent cache
    cached_id = _load_cached_machine_id()
    if cached_id:
        _MACHINE_ID_CACHE = cached_id
        return cached_id
    
    # Generate new machine ID
    # Collect hardware identifiers with fallbacks
    identifiers = []
    
    # System UUID - most reliable identifier
    try:
        system_uuid = get_system_uuid()
        if system_uuid and system_uuid != "unknown":
            identifiers.append(f"uuid:{system_uuid}")
    except Exception:
        pass
    
    # MAC address - fairly stable
    try:
        mac_addr = get_mac_address()
        if mac_addr and mac_addr != "unknown":
            identifiers.append(f"mac:{mac_addr}")
    except Exception:
        pass
    
    # Disk serial - stable hardware identifier
    try:
        disk_serial = get_disk_serial()
        if disk_serial and disk_serial != "unknown":
            identifiers.append(f"disk:{disk_serial}")
    except Exception:
        pass
    
    # Hostname - somewhat stable
    try:
        hostname = platform.node()
        if hostname:
            identifiers.append(f"host:{hostname}")
    except Exception:
        pass
    
    # Machine type - hardware architecture
    try:
        machine_type = platform.machine()
        if machine_type:
            identifiers.append(f"arch:{machine_type}")
    except Exception:
        pass
    
    # CPU info - if available
    try:
        cpu_info = platform.processor()
        if cpu_info and len(cpu_info) > 5:  # Filter out empty/short strings
            identifiers.append(f"cpu:{cpu_info}")
    except Exception:
        pass
    
    # Memory total - reasonably stable
    try:
        memory = psutil.virtual_memory()
        if memory and memory.total > 0:
            identifiers.append(f"mem:{memory.total}")
    except Exception:
        pass
    
    # Ensure we have at least some identifiers
    if not identifiers:
        # Fallback to Python's uuid if nothing else works
        import uuid
        fallback_id = str(uuid.uuid4())
        identifiers.append(f"fallback:{fallback_id}")
    
    # Create a combined string and hash it
    combined = "|".join(identifiers)
    
    # Use SHA-256 to create a consistent hash
    machine_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    machine_id = machine_hash[:32]  # Return first 32 characters for readability
    
    # Cache the result
    _MACHINE_ID_CACHE = machine_id
    _save_cached_machine_id(machine_id)
    
    return machine_id


def verify_machine_id(stored_machine_id: str) -> bool:
    """
    Verify if the current machine ID matches the stored one.
    
    Args:
        stored_machine_id: The machine ID from the license
        
    Returns:
        bool: True if machine IDs match, False otherwise
    """
    current_machine_id = get_machine_id()
    return current_machine_id == stored_machine_id


if __name__ == "__main__":
    # For testing purposes
    print(f"Machine ID: {get_machine_id()}")
    print(f"System UUID: {get_system_uuid()}")
    print(f"MAC Address: {get_mac_address()}")
    print(f"Disk Serial: {get_disk_serial()}")
