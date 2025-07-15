# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of QuantumMeta License Manager
- AES-256 encrypted license files (.qkey format)
- Hardware fingerprinting for machine locking
- 7-day grace period system
- CLI tool with Typer framework
- Ed25519 digital signature support
- Feature-gated licensing
- Development mode bypass
- Comprehensive test suite with PyTest
- MkDocs documentation with Material theme
- GitHub Actions for documentation deployment

### Security
- Secure encryption with AES-256-GCM
- PBKDF2 key derivation with 100,000 iterations
- Hardware-based machine fingerprinting
- Optional Ed25519 digital signatures

## [1.0.0] - 2025-07-15

### Added
- Initial production release
- Complete licensing system for QuantumMeta ecosystem
- CLI commands: generate, activate, validate, info, list, remove
- Grace period management with usage tracking
- Cross-platform support (Windows, macOS, Linux)
- Comprehensive documentation and examples
