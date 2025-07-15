# QuantumMeta License Server

🚀 **Full-Featured Licensing Engine for QuantumMeta Ecosystem**

A secure, hardware-locked, encrypted licensing system with CLI activation and comprehensive developer documentation portal, deployable to GitHub Pages.

## 🎯 Live License Server

**[🌐 Request Your License](license-server.html)** - Get instant access to QuantumMeta packages

**[🔧 Admin Dashboard](admin-app.html)** - Manage licenses and system settings

**[📖 Documentation Portal](index.md)** - Complete developer guide

## ✨ Key Features

### 🔐 **Secure License Engine**

- **AES-256-GCM Encryption**: Military-grade license file protection
- **Ed25519 Signatures**: Cryptographic license verification
- **Hardware Locking**: Machine-specific license binding
- **Grace Period**: 7-day trial for all packages

### 🌐 **REST API Backend**

- **License Generation**: `POST /api/request-license`
- **License Validation**: `POST /api/validate-license`
- **Status Checking**: `GET /api/status/{email}`
- **Rate Limiting**: Built-in protection against abuse
- **Email Delivery**: Automatic license file distribution

### 🧠 **CLI Activation Tool**

- **Simple Commands**: `quantum-license activate`, `validate`, `generate`
- **Local Storage**: `~/.quantummeta/licenses/` directory structure
- **Development Mode**: `QUANTUMMETA_DEV=1` bypass for developers
- **Rich Interface**: Beautiful terminal output with progress indicators

### 📦 **Supported Packages**

- `quantum-metalearn` - Advanced ML algorithms
- `se-agi` - Software Engineering AGI tools
- `kyber-pqc` - Post-quantum cryptography
- `neural-quantum` - Quantum neural networks
- `meta-compute` - Distributed computing framework

## 🚦 Quick Start

### For End Users

1. **Request License**: Visit our [License Server](license-server.html)
2. **Download `.qkey`**: Receive encrypted license file via email
3. **Activate License**: `quantum-license activate license.qkey`
4. **Use Package**: Import and use any QuantumMeta package

### For Developers

```python
from quantummeta_license import validate_or_grace

# Validate license or use grace period
def my_ai_function():
    validate_or_grace("quantum-metalearn")
    # Your protected code here
    return "Advanced AI computation!"
```

## 🏗️ Architecture

```bash
quantummeta-license-server/
├── 🌐 api/                    # FastAPI backend simulation
│   ├── main.py               # Server entry point
│   ├── license_gen.py        # License generation logic
│   ├── crypto.py             # Encryption & signatures
│   ├── models.py             # Data models
│   ├── emailer.py            # Email delivery
│   └── db.py                 # Database operations
├── 🧠 cli/                    # CLI activation tool
│   └── main.py               # quantum-license command
├── 📘 docs/                   # MkDocs documentation
│   ├── license-server.html   # License request portal
│   ├── admin-app.html        # Admin dashboard
│   └── *.md                  # Documentation pages
├── 🧪 tests/                  # Comprehensive test suite
├── 📦 mkdocs.yml              # Documentation config
└── 🚀 .github/workflows/     # GitHub Actions
    └── deploy.yml            # Auto-deploy to Pages
```

## 🔧 API Endpoints

### License Management

- `POST /api/request-license` - Request new license
- `POST /api/validate-license` - Validate existing license
- `GET /api/status/{email}` - Check license status
- `GET /api/download/{license_id}` - Download license file

### Admin Operations

- `POST /api/admin/generate` - Generate license (admin)
- `DELETE /api/admin/revoke/{license_id}` - Revoke license
- `GET /api/admin/analytics` - Usage analytics

## 🛡️ Security Features

- **Rate Limiting**: 10 requests per minute per IP
- **Email Validation**: RFC-compliant email verification
- **CORS Protection**: Secure cross-origin requests
- **Audit Logging**: Complete operation tracking
- **Token-based Auth**: Secure admin access

## 📧 License Delivery

Licenses are automatically delivered via email with:

- Encrypted `.qkey` attachment
- Installation instructions
- CLI activation commands
- Support contact information

## 🎨 GitHub Pages Integration

This entire system is designed to run on GitHub Pages with:

- Static file serving for documentation
- JavaScript-based API simulation
- Local storage for demo purposes
- Responsive Material Design theme

## 📱 Mobile Responsive

Full mobile support with:

- Touch-friendly interface
- Responsive layout
- Progressive Web App features
- Offline documentation access

---

**Built with ❤️ for the QuantumMeta ecosystem**
