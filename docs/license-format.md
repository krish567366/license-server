# License Format

Understanding the structure and format of QuantumMeta license files.

## File Format

QuantumMeta licenses are stored in encrypted `.qkey` files using AES-256-GCM encryption. The file structure consists of:

1. **Salt** (16 bytes) - Random salt for key derivation
2. **Nonce** (12 bytes) - Random nonce for AES-GCM
3. **Authentication Tag** (16 bytes) - GCM authentication tag
4. **Encrypted Data** (variable) - JSON license data

## JSON Structure

When decrypted, the license file contains JSON data with the following structure:

```json
{
  "package": "quantum-metalearn",
  "user": "user@company.com", 
  "machine_id": "abc123def456789012345678901234567890",
  "issued": "2025-07-15T10:30:00",
  "expires": "2026-07-15T10:30:00",
  "features": ["core", "pro"],
  "signature": "base64-encoded-ed25519-signature"
}
```

## Field Descriptions

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `package` | string | Package name (lowercase, normalized) |
| `user` | string | User email or identifier |
| `machine_id` | string | Hardware fingerprint (32-char hex) |
| `issued` | string | Issue date in ISO 8601 format |
| `expires` | string | Expiration date in ISO 8601 format |
| `features` | array | List of enabled feature strings |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `signature` | string | Base64-encoded Ed25519 signature |

## Machine ID Format

The machine ID is a 32-character hexadecimal string generated from:

- System UUID
- Primary network interface MAC address  
- Primary disk serial number
- Hostname
- CPU information
- Total memory

Example: `abc123def456789012345678901234567890`

## Feature System

Features are case-insensitive strings that enable specific functionality:

### Standard Features

- `core` - Basic package functionality
- `pro` - Advanced features
- `enterprise` - Enterprise-grade features
- `api` - API access
- `unlimited` - Unlimited usage/resources

### Custom Features

Packages can define custom features:

```json
{
  "features": [
    "core",
    "quantum-simulation", 
    "ai-models",
    "distributed-computing"
  ]
}
```

## Date Format

All dates use ISO 8601 format:

- `YYYY-MM-DD` - Date only
- `YYYY-MM-DDTHH:MM:SS` - Date and time
- `YYYY-MM-DDTHH:MM:SS.ffffff` - With microseconds
- `YYYY-MM-DDTHH:MM:SS+05:00` - With timezone

Examples:
```json
{
  "issued": "2025-07-15",
  "expires": "2026-07-15T23:59:59"
}
```

## Signature Format

Ed25519 signatures are base64-encoded and cover all fields except the signature itself:

```json
{
  "package": "example",
  "user": "user@example.com",
  "signature": "MEUCIQDx...base64...xyz="
}
```

The signature is generated from canonical JSON (sorted keys, no whitespace).

## Encryption Details

### AES-256-GCM

- **Algorithm**: AES-256 in GCM mode
- **Key Size**: 256 bits (32 bytes)
- **Nonce Size**: 96 bits (12 bytes) 
- **Tag Size**: 128 bits (16 bytes)

### Key Derivation

Keys are derived using PBKDF2-HMAC-SHA256:

- **Iterations**: 100,000
- **Salt Size**: 128 bits (16 bytes)
- **Output Size**: 256 bits (32 bytes)
- **Default Password**: "quantummeta"

### File Structure

```
[Salt:16][Nonce:12][Tag:16][Encrypted JSON:variable]
```

## Validation Rules

### Package Name
- Must be non-empty string
- Converted to lowercase
- Whitespace trimmed

### User
- Must be non-empty string
- Typically email address
- No format validation enforced

### Machine ID
- Must be 32-character hex string
- Generated deterministically from hardware
- Case-insensitive comparison

### Dates
- Must be valid ISO 8601 format
- Expiration must be after issue date
- Timezone information optional

### Features
- Array of strings
- Case-insensitive matching
- Empty array allowed
- Duplicates ignored

## Example License Files

### Basic License

```json
{
  "package": "quantum-sim", 
  "user": "researcher@university.edu",
  "machine_id": "a1b2c3d4e5f67890123456789abcdef01",
  "issued": "2025-07-15T09:00:00",
  "expires": "2025-12-31T23:59:59", 
  "features": ["core"]
}
```

### Pro License with Signature

```json
{
  "package": "ai-models",
  "user": "developer@company.com", 
  "machine_id": "f1e2d3c4b5a6978012345678fedcba09",
  "issued": "2025-07-15T10:30:00.123456",
  "expires": "2026-07-15T10:30:00.123456",
  "features": ["core", "pro", "api"],
  "signature": "Rx8kKZ...ed25519-signature...abc123="
}
```

### Enterprise License

```json
{
  "package": "quantum-cloud",
  "user": "admin@enterprise.com",
  "machine_id": "123456789abcdef01234567890abcdef",  
  "issued": "2025-01-01T00:00:00Z",
  "expires": "2027-01-01T00:00:00Z",
  "features": [
    "core",
    "pro", 
    "enterprise",
    "unlimited",
    "priority-support",
    "custom-integrations"
  ],
  "signature": "4B7hKL...enterprise-signature...xyz789="
}
```

## Security Considerations

### Encryption Strength
- AES-256-GCM provides authenticated encryption
- PBKDF2 with 100K iterations resists brute force
- Random salts prevent rainbow table attacks

### Hardware Binding
- Machine ID prevents license sharing
- Multiple hardware components increase uniqueness
- Deterministic generation ensures consistency

### Digital Signatures
- Ed25519 provides strong cryptographic signatures
- Prevents license tampering
- Enables license authenticity verification

### Best Practices
- Use strong passwords for license generation
- Rotate signing keys periodically  
- Monitor for license validation failures
- Implement proper key management
