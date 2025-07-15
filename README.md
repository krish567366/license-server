# QuantumMeta License Manager

[![PyPI version](https://badge.fury.io/py/quantummeta-license.svg)](https://badge.fury.io/py/quantummeta-license)
[![Python versions](https://img.shields.io/pypi/pyversions/quantummeta-license.svg)](https://pypi.org/project/quantummeta-license/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://quantummeta.github.io/quantummeta-license)

A universal, secure licensing system for the entire QuantumMeta ecosystem of PyPI packages in AI, quantum computing, and AGI.

## 🚀 Features

- 🔐 **Secure License Management**: AES-256 encrypted `.qkey` files with hardware locking
- 🖥️ **Machine Locking**: License tied to unique hardware fingerprint (UUID + MAC + disk serial)
- ⏳ **Grace Period**: 7-day free trial on first import, then license required
- 🧪 **CLI Tool**: Easy license generation, activation, and validation
- 🛡️ **Feature Gating**: Control access to specific package features
- 🔧 **Developer Friendly**: Development bypass with `QUANTUMMETA_DEV=1`

## 📦 Installation

```bash
pip install quantummeta-license
```

## 🚀 Quick Start

### For End Users

1. **Activate a license** (if you have one):
```bash
quantum-license activate /path/to/your/license.qkey
```

2. **Check license status**:
```bash
quantum-license validate quantum-metalearn
```

3. **Use in your Python code**:
```python
from quantummeta_license import validate_or_grace

# This will either validate the license or start the 7-day grace period
validate_or_grace("quantum-metalearn")
```

### For Package Developers

Integrate licensing into your QuantumMeta package:

```python
from quantummeta_license import validate_or_grace, LicenseError

def my_premium_function():
    try:
        # Validate license with specific features
        validate_or_grace("my-quantum-package", required_features=["pro"])
        # Your premium functionality here
        return "Premium feature activated!"
    except LicenseError:
        return "This feature requires a Pro license."
```

## 🧪 CLI Commands

The `quantum-license` CLI provides these commands:

- `generate`: Create a new license (admin use)
- `activate`: Install a license file
- `validate`: Check license status and features
- `info`: Display system information

### Examples

```bash
# Generate a license (admin only)
quantum-license generate --package quantum-metalearn --user user@example.com --features core,pro

# Activate a license
quantum-license activate license.qkey

# Validate specific package
quantum-license validate quantum-metalearn

# Show system info
quantum-license info
```

## 🔧 Development Mode

For development and testing, set the environment variable:

```bash
export QUANTUMMETA_DEV=1  # Unix/Linux/macOS
set QUANTUMMETA_DEV=1     # Windows
```

This bypasses license checks entirely.

## 📁 License Storage

Licenses are stored in:
- **Windows**: `%USERPROFILE%\.quantummeta\licenses\`
- **macOS**: `~/.quantummeta/licenses/`
- **Linux**: `~/.quantummeta/licenses/`

Usage tracking is stored in:
- `~/.quantummeta/usage_log.json`

## 🧠 Package Integration

To integrate QuantumMeta License into your package:

```python
from quantummeta_license import validate_or_grace, LicenseError

def __init_license():
    """Call this in your package's __init__.py"""
    try:
        validate_or_grace("your-package-name")
    except LicenseError as e:
        print(f"License Error: {e}")
        # Handle license error appropriately

# Call on package import
__init_license()
```

## 📚 Documentation

Full documentation is available at: [https://quantummeta.github.io/quantummeta-license](https://quantummeta.github.io/quantummeta-license)

## 🛡️ Security

- All license files are encrypted with AES-256
- Hardware fingerprinting prevents license sharing
- Secure key derivation using PBKDF2
- Optional Ed25519 digital signatures

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://quantummeta.github.io/quantummeta-license)
- 🐛 [Issue Tracker](https://github.com/quantummeta/quantummeta-license/issues)
- 💬 [Discussions](https://github.com/quantummeta/quantummeta-license/discussions)

---

Made with ❤️ by the QuantumMeta Team
