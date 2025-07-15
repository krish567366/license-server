#!/usr/bin/env python3
"""
Example script demonstrating QuantumMeta License Manager integration.

This script shows how to integrate licensing into a hypothetical
quantum computing package.
"""

import sys
import os
from datetime import datetime

# Add the package to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from quantummeta_license import (
    validate_or_grace, 
    LicenseError,
    LicenseExpiredError,
    FeatureNotLicensedError,
    LicenseNotFoundError
)


class QuantumProcessor:
    """Example quantum computing class with license integration."""
    
    def __init__(self):
        self.package_name = "quantum-processor-example"
        print("🚀 Initializing Quantum Processor...")
        
        # Check basic license on initialization
        try:
            validate_or_grace(self.package_name)
            print("✅ License validated - Quantum Processor ready!")
        except LicenseError as e:
            print(f"⚠️ License notice: {e}")
            print("Some features may be limited.")
    
    def basic_computation(self, data):
        """Basic quantum computation - available to all users."""
        try:
            validate_or_grace(self.package_name)
            print(f"🔄 Running basic quantum computation on: {data}")
            return f"Basic quantum result for {data}"
        except LicenseError as e:
            print(f"❌ Cannot perform computation: {e}")
            return None
    
    def advanced_computation(self, data):
        """Advanced quantum computation - requires Pro license."""
        try:
            validate_or_grace(self.package_name, required_features=["pro"])
            print(f"⚡ Running advanced quantum computation on: {data}")
            return f"Advanced quantum result for {data}"
        except FeatureNotLicensedError:
            print("🔒 Advanced computation requires Pro license")
            print("💡 Falling back to basic computation...")
            return self.basic_computation(data)
        except LicenseError as e:
            print(f"❌ Cannot perform computation: {e}")
            return None
    
    def enterprise_simulation(self, data):
        """Enterprise quantum simulation - requires Enterprise license."""
        try:
            validate_or_grace(self.package_name, required_features=["enterprise"])
            print(f"🌟 Running enterprise quantum simulation on: {data}")
            return f"Enterprise quantum simulation result for {data}"
        except FeatureNotLicensedError:
            print("🔒 Enterprise simulation requires Enterprise license")
            print("📧 Contact sales@quantummeta.com for upgrade options")
            return None
        except LicenseError as e:
            print(f"❌ Cannot perform simulation: {e}")
            return None


def demonstrate_licensing():
    """Demonstrate the licensing system in action."""
    print("=" * 60)
    print("🔬 QuantumMeta License Manager Demo")
    print("=" * 60)
    print()
    
    # Create quantum processor instance
    processor = QuantumProcessor()
    print()
    
    # Test basic computation
    print("📋 Testing Basic Computation:")
    result1 = processor.basic_computation("sample_data_1")
    if result1:
        print(f"✅ Result: {result1}")
    print()
    
    # Test advanced computation
    print("📋 Testing Advanced Computation:")
    result2 = processor.advanced_computation("sample_data_2")
    if result2:
        print(f"✅ Result: {result2}")
    print()
    
    # Test enterprise simulation
    print("📋 Testing Enterprise Simulation:")
    result3 = processor.enterprise_simulation("sample_data_3")
    if result3:
        print(f"✅ Result: {result3}")
    print()
    
    # Show helpful information
    print("💡 Helpful Commands:")
    print("   • Check license status: quantum-license validate quantum-processor-example")
    print("   • View system info: quantum-license info")
    print("   • Enable dev mode: set QUANTUMMETA_DEV=1")
    print()


def show_license_status():
    """Show current license status information."""
    from quantummeta_license.core.validation import check_license_status
    
    print("📊 Current License Status:")
    print("-" * 40)
    
    package_name = "quantum-processor-example"
    status = check_license_status(package_name)
    
    if status["status"] == "development_mode":
        print("🚧 Development Mode: ACTIVE")
        print("   All license checks are bypassed")
    elif status["status"] == "licensed":
        info = status["license_info"]
        print(f"✅ Status: LICENSED")
        print(f"   User: {info['user']}")
        print(f"   Expires: {info['expires']}")
        print(f"   Features: {', '.join(info['features'])}")
    elif status["status"] == "grace_period":
        grace = status["grace_info"]
        print(f"⏳ Status: GRACE PERIOD")
        print(f"   Days remaining: {grace['days_remaining']}")
        print(f"   Hours remaining: {grace['hours_remaining']}")
        print(f"   Expires: {grace['expiry_date']}")
    else:
        print(f"❌ Status: {status['status'].upper()}")
        print(f"   Message: {status['message']}")
    
    print()


def show_machine_info():
    """Show machine information."""
    from quantummeta_license.core.hardware import get_machine_id
    from quantummeta_license.core.validation import is_development_mode
    
    print("🖥️ Machine Information:")
    print("-" * 40)
    print(f"Machine ID: {get_machine_id()}")
    print(f"Development Mode: {'Enabled' if is_development_mode() else 'Disabled'}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()


if __name__ == "__main__":
    # Show current status
    show_machine_info()
    show_license_status()
    
    # Run the demonstration
    demonstrate_licensing()
    
    print("🔚 Demo completed!")
    print("📚 For more information, visit: https://quantummeta.github.io/quantummeta-license")
