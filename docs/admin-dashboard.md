# Admin Dashboard

The QuantumMeta License Manager includes a powerful web-based admin dashboard for license management.

## Features

- **Secure Login**: Email and token-based authentication
- **License Generation**: Create new licenses with custom parameters
- **License Management**: View, edit, and manage existing licenses
- **License Validation**: Check license status and validity
- **License Expiration**: Set expiration dates and manage lifecycle
- **License Deletion**: Remove licenses from the system

## Getting Started

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Dashboard](#running-the-dashboard)
4. [Admin CLI Commands](#admin-cli-commands)
5. [Dashboard Features](#dashboard-features)

## Installation

The admin dashboard is included with the package but requires additional dependencies:

```bash
pip install quantummeta-license[admin]
```

## Configuration

Create an admin configuration file:

```bash
quantum-license admin setup
```

This will generate:

- Admin email and secure token
- Server configuration
- License storage paths

## Running the Dashboard

### Option 1: Web Server

Start the admin server:

```bash
quantum-license admin server --port 8080 --host localhost
```

The dashboard will be available at `http://localhost:8080`

### Option 2: Direct File Access

Open the dashboard directly:

```bash
quantum-license admin dashboard
```

## Admin CLI Commands

### Setup Admin Configuration

```bash
quantum-license admin setup
```

### Start Web Server

```bash
quantum-license admin server --port 8080
```

### List All Licenses

```bash
quantum-license admin list-licenses --format table
quantum-license admin list-licenses --format json
```

### Expire a License

```bash
quantum-license admin expire-license lic_2025_001
```

### Delete a License

```bash
quantum-license admin delete-license lic_2025_001 --yes
```

## Dashboard Features

### 🔐 Secure Authentication

- Email and token-based login
- Session management
- Secure credential handling

### 📊 Statistics Overview

- Total licenses count
- Active licenses
- Expired licenses
- Suspended licenses

### ➕ License Generation

- Package name specification
- User email assignment
- Feature selection (core, pro, enterprise, ai, quantum)
- Machine ID binding (optional)
- Custom expiry dates
- License type selection
- Downloadable .qkey files

### 📋 License Management

- Real-time license listing
- Search and filter functionality
- License status management
- Bulk operations support

### ✅ License Validation

- License ID verification
- Machine ID matching
- Expiry date checking
- Status validation
- Detailed validation reports

### ⚙️ System Settings

- Default expiry periods
- Grace period configuration
- Encryption key management
- License export functionality

## Live Demo

[Open Admin Dashboard](admin-app.html){ .md-button .md-button--primary }

## Security Notes

- Admin tokens are generated with cryptographically secure random numbers
- All license operations are logged
- Machine ID verification prevents unauthorized usage
- AES-256 encryption protects license files
