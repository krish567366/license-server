# QuantumMeta License Manager

<div align="center">
  <h1>🚀 Universal Licensing for QuantumMeta Ecosystem</h1>
  <p><em>Secure, flexible, and developer-friendly licensing system</em></p>
</div>

---

## 🌟 Welcome

QuantumMeta License Manager is a production-ready, universal licensing system designed specifically for the QuantumMeta ecosystem of PyPI packages in AI, quantum computing, and AGI. It provides a seamless balance between security and user experience.

## ✨ Key Features

### 🔐 **Secure License Management**
- **AES-256 Encryption**: All license files (`.qkey`) are encrypted with military-grade encryption
- **Hardware Locking**: Licenses are tied to unique machine fingerprints preventing unauthorized sharing
- **Digital Signatures**: Optional Ed25519 signatures for additional verification

### ⏳ **Grace Period System**
- **7-Day Trial**: Automatic grace period for new users without requiring upfront licensing
- **Seamless Transition**: Smooth progression from trial to licensed usage
- **Smart Tracking**: Usage patterns stored securely in `~/.quantummeta/usage_log.json`

### 🧪 **Developer-Friendly CLI**
- **Simple Commands**: `quantum-license generate`, `activate`, `validate`
- **Rich Output**: Beautiful terminal interface with tables and color coding
- **Flexible Integration**: Easy integration into any Python package

### 🛡️ **Feature Gating**
- **Granular Control**: Enable specific features like `["core", "pro", "enterprise"]`
- **Runtime Validation**: Real-time feature availability checking
- **License Tiers**: Support for multiple licensing tiers per package

### 🔧 **Development Mode**
- **Bypass for Developers**: Set `QUANTUMMETA_DEV=1` to skip all license checks
- **Testing Support**: Perfect for CI/CD and development environments

### 🌐 **Admin Dashboard**
- **Web Interface**: Modern, responsive admin dashboard for license management
- **Secure Login**: Email and token-based authentication system
- **Real-time Management**: Generate, validate, expire, and delete licenses
- **Usage Analytics**: Track license usage and system statistics
- **Batch Operations**: Manage multiple licenses efficiently

## 🚦 Quick Example

```python
from quantummeta_license import validate_or_grace

# Simple integration - handles grace period automatically
def my_ai_function():
    validate_or_grace("quantum-metalearn")
    # Your AI/quantum computing code here
    return "Advanced AI computation completed!"

# Feature-gated functionality
def premium_feature():
    validate_or_grace("quantum-metalearn", required_features=["pro"])
    # Premium functionality only for licensed users
    return "Premium AI model accessed!"
```

## 📦 Package Structure

```
quantummeta_license/
├── core/                    # Core licensing logic
│   ├── validation.py        # Main validation functions
│   ├── license_manager.py   # License CRUD operations
│   ├── hardware.py          # Hardware fingerprinting
│   ├── encryption.py        # AES-256 + Ed25519 crypto
│   └── usage_tracker.py     # Grace period management
├── cli/                     # Typer-based CLI interface
│   └── main.py             # quantum-license command
├── utils/                   # Logging and utilities
├── docs/                    # Documentation and admin dashboard
│   └── admin-app.html      # Web-based admin interface
└── tests/                   # Comprehensive PyTest suite
```

## 🎯 Perfect For

- **🧠 AI/ML Packages**: License complex machine learning models and algorithms
- **⚛️ Quantum Computing**: Secure quantum computing libraries and simulators  
- **🤖 AGI Research**: Protect advanced artificial general intelligence research
- **📊 Data Science**: License premium data analysis and visualization tools
- **🔬 Scientific Computing**: Secure access to specialized scientific libraries

## 🔄 License Lifecycle

1. **📝 Generate**: Admin creates encrypted `.qkey` license files via CLI or dashboard
2. **⚡ Activate**: Users install licenses with `quantum-license activate`
3. **✅ Validate**: Automatic validation on package import
4. **⏰ Grace**: 7-day trial period for new users
5. **🔄 Renew**: Seamless license renewal and updates
6. **📊 Monitor**: Track usage through admin dashboard

## 🌐 Cross-Platform Support

- ✅ **Windows** (PowerShell, CMD)
- ✅ **macOS** (Terminal, iTerm2)  
- ✅ **Linux** (All major distributions)
- ✅ **Docker** containers
- ✅ **CI/CD** environments
- ✅ **Web Browsers** (Admin dashboard)

## 💡 Use Cases

### For Package Publishers
- Monetize premium features and advanced algorithms
- Control access to proprietary AI models
- Track usage and prevent unauthorized distribution
- Implement tiered licensing (Basic/Pro/Enterprise)

### For End Users  
- Try packages risk-free with 7-day grace period
- Simple one-command license activation
- Transparent license status and feature availability
- Offline usage after initial activation

### For Enterprises
- Secure deployment of licensed AI/quantum software
- Hardware-locked licenses prevent license sharing
- Centralized license management and tracking
- Development mode for internal testing

## 🚀 Get Started

Ready to secure your QuantumMeta packages? Check out our [Installation Guide](installation.md) and [Quick Start Tutorial](quickstart.md)!

---

<div align="center">
  <p><strong>Built with ❤️ by the QuantumMeta Team</strong></p>
  <p><em>Empowering the future of AI, Quantum Computing, and AGI</em></p>
</div>
