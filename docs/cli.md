# CLI Reference

Complete reference for the `quantum-license` command-line interface.

## Global Options

All commands support these global options:

- `--help` - Show help message
- `--version` - Show version information

## Commands

### Core Commands

#### `generate`

Generate a new license file (admin use only).

```bash
quantum-license generate [OPTIONS]
```

**Required Options:**
- `--package, -p TEXT` - Package name to license
- `--user, -u TEXT` - User email or ID  
- `--output, -o TEXT` - Output license file path

**Optional Options:**
- `--features, -f TEXT` - Comma-separated list of features (default: "core")
- `--days, -d INTEGER` - License validity in days (default: 365)
- `--machine-id, -m TEXT` - Target machine ID (default: current machine)
- `--sign, -s` - Sign the license with Ed25519

**Examples:**

```bash
# Basic license
quantum-license generate -p "quantum-metalearn" -u "user@company.com" -o license.qkey

# License with multiple features
quantum-license generate -p "quantum-metalearn" -u "user@company.com" -f "core,pro,enterprise" -o license.qkey

# 6-month license with signature
quantum-license generate -p "quantum-metalearn" -u "user@company.com" -d 180 --sign -o license.qkey

# License for specific machine
quantum-license generate -p "quantum-metalearn" -u "user@company.com" -m "abc123def456" -o license.qkey
```

### Admin Commands

#### `admin setup`

Set up admin configuration for the license management system.

```bash
quantum-license admin setup [OPTIONS]
```

**Optional Options:**
- `--config, -c TEXT` - Config file path (default: ~/.quantummeta/admin_config.json)

**Examples:**

```bash
# Setup with default config location
quantum-license admin setup

# Setup with custom config file
quantum-license admin setup --config /path/to/admin.json
```

#### `admin server`

Start the web-based admin dashboard server.

```bash
quantum-license admin server [OPTIONS]
```

**Optional Options:**
- `--port, -p INTEGER` - Server port (default: 8080)
- `--host, -h TEXT` - Server host (default: localhost)
- `--open/--no-open` - Open browser automatically (default: true)

**Examples:**

```bash
# Start server on default port
quantum-license admin server

# Start server on custom port
quantum-license admin server --port 9000

# Start server without opening browser
quantum-license admin server --no-open
```

#### `admin dashboard`

Open the admin dashboard directly in browser (file-based).

```bash
quantum-license admin dashboard
```

#### `admin list-licenses`

List all licenses in the system.

```bash
quantum-license admin list-licenses [OPTIONS]
```

**Optional Options:**
- `--package, -p TEXT` - Filter by package name
- `--status, -s TEXT` - Filter by status (active, expired, suspended)
- `--format, -f TEXT` - Output format (table, json) (default: table)

**Examples:**

```bash
# List all licenses in table format
quantum-license admin list-licenses

# List licenses for specific package
quantum-license admin list-licenses --package quantum-metalearn

# List only active licenses in JSON format
quantum-license admin list-licenses --status active --format json
```

#### `admin expire-license`

Expire a specific license.

```bash
quantum-license admin expire-license LICENSE_ID [OPTIONS]
```

**Arguments:**
- `LICENSE_ID` - The license ID to expire

**Optional Options:**
- `--yes, -y` - Skip confirmation prompt

**Examples:**

```bash
# Expire license with confirmation
quantum-license admin expire-license lic_2025_001

# Expire license without confirmation
quantum-license admin expire-license lic_2025_001 --yes
```

#### `admin delete-license`

Delete a specific license permanently.

```bash
quantum-license admin delete-license LICENSE_ID [OPTIONS]
```

**Arguments:**
- `LICENSE_ID` - The license ID to delete

**Optional Options:**
- `--yes, -y` - Skip confirmation prompt

**Examples:**

```bash
# Delete license with confirmation
quantum-license admin delete-license lic_2025_001

# Delete license without confirmation
quantum-license admin delete-license lic_2025_001 --yes
```

### User Commands

#### `activate`

Activate a license by installing it to the system.

```bash
quantum-license activate LICENSE_FILE
```

**Arguments:**
- `LICENSE_FILE` - Path to the `.qkey` license file

**Examples:**

```bash
# Activate license
quantum-license activate license.qkey

# Activate from different directory
quantum-license activate /path/to/license.qkey
```

#### `validate`

Validate license for a specific package.

```bash
quantum-license validate PACKAGE [OPTIONS]
```

**Arguments:**
- `PACKAGE` - Package name to validate

**Optional Options:**
- `--features, -f TEXT` - Required features (comma-separated)

**Examples:**

```bash
# Basic validation
quantum-license validate quantum-metalearn

# Validate with required features
quantum-license validate quantum-metalearn -f "pro,enterprise"
```

**Exit Codes:**
- `0` - License is valid (or development mode)
- `1` - License is invalid, expired, or missing

#### `info`

Display system information and installed licenses.

```bash
quantum-license info
```

Shows:
- Machine ID
- Development mode status
- All installed licenses with status
- Grace period usage data

**Example output:**

```
System Information
Machine ID: abc123def456ghi789
Development Mode: Disabled

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Package           ┃ User               ┃ Expires    ┃ Features     ┃ Status        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ quantum-metalearn │ user@company.com   │ 2025-12-31 │ core, pro    │ ✅ Valid      │
│ quantum-nlp       │ user@company.com   │ 2025-06-30 │ core         │ ⏰ Expired    │
└───────────────────┴────────────────────┴────────────┴──────────────┴───────────────┘

Grace Period Usage
  test-package: Active (first use: 2025-07-10T10:30:00)
```

#### `list`

List all installed licenses.

```bash
quantum-license list
```

Similar to `info` but shows only the license table.

#### `remove`

Remove a license for a specific package.

```bash
quantum-license remove PACKAGE [OPTIONS]
```

**Arguments:**
- `PACKAGE` - Package name to remove license for

**Optional Options:**
- `--yes, -y` - Skip confirmation prompt

**Examples:**

```bash
# Remove with confirmation
quantum-license remove quantum-metalearn

# Remove without confirmation
quantum-license remove quantum-metalearn -y
```

## Environment Variables

### `QUANTUMMETA_DEV`

Enable development mode to bypass all license checks.

**Values:** `1`, `true`, `yes`, `on` (case insensitive)

```bash
# Unix/Linux/macOS
export QUANTUMMETA_DEV=1

# Windows PowerShell  
$env:QUANTUMMETA_DEV = "1"

# Windows CMD
set QUANTUMMETA_DEV=1
```

## Configuration Files

### License Storage

Licenses are stored in:

- **Windows:** `%USERPROFILE%\.quantummeta\licenses\`
- **macOS:** `~/.quantummeta/licenses/`
- **Linux:** `~/.quantummeta/licenses/`

Each package gets its own `.qkey` file: `{package-name}.qkey`

### Usage Tracking

Grace period data is stored in:
- `~/.quantummeta/usage_log.json`

Example content:
```json
{
  "quantum-metalearn": {
    "first_use": "2025-07-15T10:30:00.123456",
    "last_check": "2025-07-16T14:22:11.654321"
  }
}
```

## Error Handling

### Common Error Messages

**License not found:**
```
❌ Grace period for 'package-name' expired on 2025-07-22T10:30:00. Please activate a valid license.
```

**Wrong machine:**
```
❌ License for 'package-name' is not valid for this machine
```

**Missing features:**
```
❌ License for 'package-name' does not include required features: ['enterprise']
```

**Expired license:**
```
❌ License for 'package-name' has expired on 2025-01-15T00:00:00
```

### Exit Codes

- `0` - Success
- `1` - Error (invalid license, missing file, etc.)

## Advanced Usage

### Batch License Generation

Generate multiple licenses:

```bash
#!/bin/bash
users=("user1@company.com" "user2@company.com" "user3@company.com")
for user in "${users[@]}"; do
    quantum-license generate -p "quantum-metalearn" -u "$user" -o "license-$user.qkey"
done
```

### License Status in Scripts

Check license status in scripts:

```bash
if quantum-license validate quantum-metalearn; then
    echo "License is valid"
    python run_analysis.py
else
    echo "License validation failed"
    exit 1
fi
```

### Machine ID for Remote Deployment

Get machine ID for remote license generation:

```bash
# On target machine
quantum-license info | grep "Machine ID"

# Use the ID for license generation
quantum-license generate -p "quantum-metalearn" -u "user@company.com" -m "target-machine-id" -o license.qkey
```
