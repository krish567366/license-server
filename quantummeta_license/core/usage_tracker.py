"""Usage tracking for grace period management."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import platformdirs


class UsageTracker:
    """Tracks package usage for grace period management."""
    
    def __init__(self):
        self.config_dir = Path(platformdirs.user_config_dir("quantummeta"))
        self.usage_log_file = self.config_dir / "usage_log.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_usage_log(self) -> Dict:
        """Load the usage log from disk."""
        if not self.usage_log_file.exists():
            return {}
        
        try:
            with open(self.usage_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_usage_log(self, log_data: Dict) -> None:
        """Save the usage log to disk."""
        try:
            with open(self.usage_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2)
        except IOError:
            pass  # Fail silently if we can't write
    
    def get_first_use_date(self, package_name: str) -> Optional[datetime]:
        """
        Get the first use date for a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            datetime or None: First use date if recorded
        """
        log_data = self._load_usage_log()
        
        if package_name in log_data:
            try:
                return datetime.fromisoformat(log_data[package_name]["first_use"])
            except (KeyError, ValueError):
                pass
        
        return None
    
    def record_first_use(self, package_name: str) -> datetime:
        """
        Record the first use of a package if not already recorded.
        
        Args:
            package_name: Name of the package
            
        Returns:
            datetime: The first use date (existing or newly recorded)
        """
        log_data = self._load_usage_log()
        
        if package_name not in log_data:
            first_use = datetime.now()
            log_data[package_name] = {
                "first_use": first_use.isoformat(),
                "last_check": first_use.isoformat()
            }
            self._save_usage_log(log_data)
            return first_use
        else:
            # Update last check time
            log_data[package_name]["last_check"] = datetime.now().isoformat()
            self._save_usage_log(log_data)
            return datetime.fromisoformat(log_data[package_name]["first_use"])
    
    def is_grace_period_expired(self, package_name: str, grace_days: int = 7) -> bool:
        """
        Check if the grace period has expired for a package.
        
        Args:
            package_name: Name of the package
            grace_days: Number of grace days (default: 7)
            
        Returns:
            bool: True if grace period has expired
        """
        first_use = self.get_first_use_date(package_name)
        
        if first_use is None:
            # Never used before, record first use
            self.record_first_use(package_name)
            return False
        
        expiry_date = first_use + timedelta(days=grace_days)
        return datetime.now() > expiry_date
    
    def get_grace_period_info(self, package_name: str, grace_days: int = 7) -> Dict:
        """
        Get detailed grace period information.
        
        Args:
            package_name: Name of the package
            grace_days: Number of grace days (default: 7)
            
        Returns:
            dict: Grace period information
        """
        first_use = self.get_first_use_date(package_name)
        
        if first_use is None:
            first_use = self.record_first_use(package_name)
        
        expiry_date = first_use + timedelta(days=grace_days)
        is_expired = datetime.now() > expiry_date
        
        if not is_expired:
            remaining_time = expiry_date - datetime.now()
            days_remaining = remaining_time.days
            hours_remaining = remaining_time.seconds // 3600
        else:
            days_remaining = 0
            hours_remaining = 0
        
        return {
            "package_name": package_name,
            "first_use": first_use.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "is_expired": is_expired,
            "days_remaining": days_remaining,
            "hours_remaining": hours_remaining,
            "grace_days": grace_days
        }
    
    def clear_usage_data(self, package_name: Optional[str] = None) -> None:
        """
        Clear usage data for a specific package or all packages.
        
        Args:
            package_name: Name of package to clear, or None for all packages
        """
        if package_name is None:
            # Clear all data
            self._save_usage_log({})
        else:
            # Clear specific package data
            log_data = self._load_usage_log()
            log_data.pop(package_name, None)
            self._save_usage_log(log_data)
    
    def get_all_usage_data(self) -> Dict:
        """Get all usage data for all packages."""
        return self._load_usage_log()
