# Quick Start

This guide will get you up and running with QuantumMeta License Manager in minutes.

## For End Users

### 1. Check Your System

First, let's see your machine information:

```bash
quantum-license info
```

### 2. Activate a License (if you have one)

If you received a `.qkey` license file:

```bash
quantum-license activate path/to/your/license.qkey
```

### 3. Check License Status

Verify your license is working:

```bash
quantum-license validate quantum-metalearn
```

### 4. Use in Python Code

```python
from quantummeta_license import validate_or_grace

# This will either validate your license or start a 7-day grace period
def my_function():
    validate_or_grace("quantum-metalearn")
    print("Access granted!")
    # Your code here

my_function()
```

## For Package Developers

### 1. Integrate License Checking

Add this to your package's `__init__.py`:

```python
from quantummeta_license import validate_or_grace, LicenseError

def _check_license():
    try:
        validate_or_grace("your-package-name")
    except LicenseError as e:
        print(f"License Error: {e}")
        # Handle gracefully or exit

# Check license on import
_check_license()
```

### 2. Feature-Gated Functions

```python
from quantummeta_license import validate_or_grace, FeatureNotLicensedError

def basic_feature():
    validate_or_grace("your-package")
    return "Basic functionality"

def premium_feature():
    try:
        validate_or_grace("your-package", required_features=["pro"])
        return "Premium functionality unlocked!"
    except FeatureNotLicensedError:
        return "This feature requires a Pro license"
```

## For License Administrators

### 1. Generate a License

```bash
quantum-license generate \
    --package "quantum-metalearn" \
    --user "user@company.com" \
    --features "core,pro" \
    --days 365 \
    --output license.qkey
```

### 2. Generate with Digital Signature

```bash
quantum-license generate \
    --package "quantum-metalearn" \
    --user "user@company.com" \
    --features "core,pro,enterprise" \
    --days 365 \
    --sign \
    --output signed-license.qkey
```

This creates both `signed-license.qkey` and `signed-license.pub` (public key).

## Development Mode

For development and testing, bypass all license checks:

```bash
# Unix/Linux/macOS
export QUANTUMMETA_DEV=1

# Windows PowerShell
$env:QUANTUMMETA_DEV = "1"

# Windows CMD
set QUANTUMMETA_DEV=1
```

Now all license validations will return `True` immediately.

## Common Workflows

### New User Experience

1. User installs your package: `pip install quantum-metalearn`
2. User imports/uses package → 7-day grace period starts automatically
3. User sees grace period notifications with remaining time
4. After 7 days, user must activate a license to continue

### Licensed User Experience

1. User receives `.qkey` file from you
2. User runs: `quantum-license activate license.qkey`
3. User can now use the package indefinitely (until license expires)
4. License is tied to their specific machine

### Enterprise Deployment

1. IT admin generates licenses for each machine/user
2. Licenses are distributed and activated on target machines
3. Applications work seamlessly with validated licenses
4. Development machines use `QUANTUMMETA_DEV=1` for testing

## Troubleshooting

### Grace Period Issues

Check grace period status:
```bash
quantum-license validate your-package-name
```

Reset grace period (testing only):
```python
from quantummeta_license.core.usage_tracker import UsageTracker
tracker = UsageTracker()
tracker.clear_usage_data("your-package-name")
```

### License Activation Problems

Common issues:
- **Wrong machine**: License is tied to a different machine
- **Expired license**: Check expiration date
- **Corrupted file**: Re-download the license file

Check detailed status:
```bash
quantum-license info
```

### Development Setup

Make sure development mode is working:
```python
from quantummeta_license.core.validation import is_development_mode
print(f"Dev mode: {is_development_mode()}")
```

## Next Steps

- [CLI Reference](cli.md) - Complete command documentation
- [Integration Guide](integration.md) - Advanced integration patterns
- [License Format](license-format.md) - Understanding license structure
- [Security](security.md) - Security considerations and best practices
