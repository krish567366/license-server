# Integration Guide

Advanced patterns for integrating QuantumMeta License Manager into your packages.

## Basic Integration

### Package-Level Integration

Add to your package's `__init__.py`:

```python
from quantummeta_license import validate_or_grace, LicenseError

# Package metadata
__version__ = "1.0.0"
__license_package__ = "your-package-name"

def _check_license():
    """Check license on package import."""
    try:
        validate_or_grace(__license_package__)
    except LicenseError as e:
        print(f"License validation failed: {e}")
        print("Please activate a valid license or contact support.")
        # Optional: raise exception to prevent package use
        # raise

# Automatic license check on import
_check_license()
```

### Function-Level Decoration

Create a decorator for license-protected functions:

```python
from functools import wraps
from quantummeta_license import validate_or_grace, LicenseError

def requires_license(package_name, features=None):
    """Decorator to require license validation."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validate_or_grace(package_name, required_features=features)
                return func(*args, **kwargs)
            except LicenseError as e:
                raise RuntimeError(f"License required for {func.__name__}: {e}")
        return wrapper
    return decorator

# Usage
@requires_license("your-package", features=["pro"])
def premium_function():
    return "Premium feature accessed!"
```

## Advanced Patterns

### Class-Level Licensing

```python
from quantummeta_license import validate_or_grace, FeatureNotLicensedError

class LicensedAIModel:
    """AI model with tiered licensing."""
    
    def __init__(self, model_type="basic"):
        self.package_name = "quantum-ai-models"
        self.model_type = model_type
        self._check_access()
    
    def _check_access(self):
        """Validate license based on model type."""
        required_features = []
        
        if self.model_type == "pro":
            required_features = ["core", "pro"]
        elif self.model_type == "enterprise":
            required_features = ["core", "pro", "enterprise"]
        
        validate_or_grace(self.package_name, required_features)
    
    def predict(self, data):
        """Basic prediction - available to all license types."""
        return f"Basic prediction on {data}"
    
    def advanced_predict(self, data):
        """Advanced prediction - requires pro license."""
        try:
            validate_or_grace(self.package_name, ["pro"])
            return f"Advanced AI prediction on {data}"
        except FeatureNotLicensedError:
            return "Advanced predictions require a Pro license"
    
    def enterprise_analytics(self, data):
        """Enterprise analytics - requires enterprise license."""
        validate_or_grace(self.package_name, ["enterprise"])
        return f"Enterprise-grade analytics on {data}"
```

### Context Manager for License Scope

```python
from contextlib import contextmanager
from quantummeta_license import validate_or_grace

@contextmanager
def licensed_context(package_name, features=None):
    """Context manager for license-required operations."""
    try:
        validate_or_grace(package_name, required_features=features)
        print(f"License validated for {package_name}")
        yield
    except Exception as e:
        print(f"License validation failed: {e}")
        raise
    finally:
        print("Licensed operation completed")

# Usage
with licensed_context("quantum-computing", ["quantum-sim"]):
    # Perform quantum computations
    result = run_quantum_algorithm()
```

### Lazy License Validation

For packages with multiple modules, validate licenses only when specific features are used:

```python
# main_module.py
from quantummeta_license import validate_or_grace, LicenseError

class LazyLicensedPackage:
    def __init__(self):
        self._license_checked = {}
    
    def _ensure_license(self, feature_set="core"):
        """Lazy license validation per feature set."""
        if feature_set not in self._license_checked:
            try:
                validate_or_grace("your-package", [feature_set])
                self._license_checked[feature_set] = True
            except LicenseError:
                self._license_checked[feature_set] = False
                raise
        
        if not self._license_checked[feature_set]:
            raise LicenseError(f"Feature {feature_set} not licensed")
    
    def basic_feature(self):
        self._ensure_license("core")
        return "Basic functionality"
    
    def advanced_feature(self):
        self._ensure_license("pro")
        return "Advanced functionality"
```

## Error Handling Strategies

### Graceful Degradation

```python
from quantummeta_license import validate_or_grace, LicenseError

class SmartAI:
    def analyze(self, data, use_advanced=True):
        """Analysis with graceful degradation."""
        if use_advanced:
            try:
                validate_or_grace("smart-ai", ["advanced"])
                return self._advanced_analysis(data)
            except LicenseError:
                print("Advanced analysis not licensed, falling back to basic")
                use_advanced = False
        
        # Basic analysis (always available during grace period)
        validate_or_grace("smart-ai")
        return self._basic_analysis(data)
    
    def _basic_analysis(self, data):
        return f"Basic analysis of {data}"
    
    def _advanced_analysis(self, data):
        return f"Advanced AI analysis of {data}"
```

### User-Friendly Error Messages

```python
from quantummeta_license import (
    validate_or_grace, 
    LicenseError, 
    LicenseExpiredError,
    FeatureNotLicensedError,
    LicenseNotFoundError
)

def user_friendly_validation(package_name, features=None):
    """Validation with user-friendly error messages."""
    try:
        validate_or_grace(package_name, required_features=features)
        return True
    except LicenseExpiredError as e:
        print("🕒 Your license has expired.")
        print("Please contact support for license renewal.")
        print(f"   Email: support@yourcompany.com")
        return False
    except FeatureNotLicensedError as e:
        print("🔒 This feature requires a higher license tier.")
        print("Available license tiers:")
        print("   • Basic: Core features")
        print("   • Pro: Advanced features") 
        print("   • Enterprise: All features")
        print("Contact sales for an upgrade: sales@yourcompany.com")
        return False
    except LicenseNotFoundError as e:
        print("📋 No license found and grace period has expired.")
        print("To continue using this software:")
        print("1. Contact sales: sales@yourcompany.com")
        print("2. Or activate an existing license: quantum-license activate license.qkey")
        return False
    except LicenseError as e:
        print(f"❌ License validation failed: {e}")
        return False
```

## Configuration and Customization

### Custom Grace Period

```python
from quantummeta_license import validate_or_grace

def custom_validation(package_name, grace_days=14):
    """Custom grace period length."""
    return validate_or_grace(package_name, grace_days=grace_days)
```

### Feature Detection

```python
from quantummeta_license.core.license_manager import LicenseManager

def get_available_features(package_name):
    """Get list of available features for a package."""
    manager = LicenseManager()
    license_obj = manager.get_license(package_name)
    
    if license_obj and not license_obj.is_expired():
        return license_obj.features
    else:
        # During grace period, assume basic features
        return ["core"]

# Usage
features = get_available_features("your-package")
if "pro" in features:
    # Enable pro features in UI
    enable_pro_features()
```

### License Information Display

```python
from quantummeta_license.core.validation import check_license_status

def show_license_info(package_name):
    """Display license information to user."""
    status = check_license_status(package_name)
    
    if status["status"] == "licensed":
        info = status["license_info"]
        print(f"✅ Licensed to: {info['user']}")
        print(f"📅 Expires: {info['expires']}")
        print(f"🔧 Features: {', '.join(info['features'])}")
    elif status["status"] == "grace_period":
        grace = status["grace_info"]
        print(f"⏳ Grace period: {grace['days_remaining']} days remaining")
        print(f"📅 Expires: {grace['expiry_date']}")
    else:
        print("❌ No valid license found")
```

## Testing and Development

### Unit Testing with Mocks

```python
import pytest
from unittest.mock import patch
from your_package import licensed_function

def test_licensed_function_with_valid_license():
    """Test function with valid license."""
    with patch('quantummeta_license.validate_or_grace', return_value=True):
        result = licensed_function()
        assert result == "expected_output"

def test_licensed_function_without_license():
    """Test function behavior without license."""
    with patch('quantummeta_license.validate_or_grace', side_effect=LicenseError("No license")):
        with pytest.raises(LicenseError):
            licensed_function()
```

### Development Mode Integration

```python
from quantummeta_license.core.validation import is_development_mode

def smart_validation(package_name):
    """Smart validation that respects development mode."""
    if is_development_mode():
        print("🚧 Development mode - skipping license check")
        return True
    
    return validate_or_grace(package_name)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test with License

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest
    
    - name: Run tests with development mode
      run: |
        export QUANTUMMETA_DEV=1
        pytest tests/
```

### Docker Integration

```dockerfile
FROM python:3.9

# Install package
COPY . /app
WORKDIR /app
RUN pip install -e .

# Enable development mode for container
ENV QUANTUMMETA_DEV=1

CMD ["python", "app.py"]
```

## Best Practices

1. **Fail Gracefully**: Always handle license errors gracefully
2. **Clear Messages**: Provide clear, actionable error messages
3. **Feature Gating**: Use feature-based licensing for flexibility
4. **Development Mode**: Always support development mode for testing
5. **Lazy Validation**: Validate licenses only when features are used
6. **User Education**: Help users understand licensing requirements
7. **Offline Support**: Design for offline usage after initial validation

## Real-World Example

Complete example for a quantum computing package:

```python
# quantum_simulator/__init__.py
from quantummeta_license import validate_or_grace, LicenseError

__version__ = "1.0.0"
__license_package__ = "quantum-simulator"

# Check basic license on import
try:
    validate_or_grace(__license_package__)
    print("✅ Quantum Simulator licensed - ready for quantum computations!")
except LicenseError as e:
    print(f"⚠️ License notice: {e}")

from .simulator import QuantumSimulator
from .algorithms import QuantumAlgorithms

# quantum_simulator/simulator.py
from quantummeta_license import validate_or_grace, FeatureNotLicensedError

class QuantumSimulator:
    def __init__(self, max_qubits=8):
        self.max_qubits = max_qubits
        self.package_name = "quantum-simulator"
    
    def basic_simulation(self, circuit):
        """Basic quantum simulation - available to all users."""
        validate_or_grace(self.package_name)
        return f"Simulating {circuit} with up to {self.max_qubits} qubits"
    
    def advanced_simulation(self, circuit):
        """Advanced simulation with optimization - requires Pro license."""
        try:
            validate_or_grace(self.package_name, ["pro"])
            return f"Advanced optimized simulation of {circuit}"
        except FeatureNotLicensedError:
            return "Advanced simulation requires Pro license - using basic simulation"
    
    def enterprise_cluster_sim(self, circuit):
        """Distributed cluster simulation - requires Enterprise license."""
        validate_or_grace(self.package_name, ["enterprise"])
        return f"Running {circuit} on quantum computing cluster"
```
