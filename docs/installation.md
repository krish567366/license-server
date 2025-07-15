# Installation

## Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux
- Administrator/root access for some hardware fingerprinting features (optional)

## Install from PyPI

```bash
pip install quantummeta-license
```

## Install from Source

```bash
git clone https://github.com/quantummeta/quantummeta-license.git
cd quantummeta-license
pip install -e .
```

## Verify Installation

Check that the CLI is working:

```bash
quantum-license --help
```

You should see the help output with available commands.

## Optional Dependencies

For development and testing:

```bash
pip install quantummeta-license[dev]
```

For building documentation:

```bash
pip install quantummeta-license[docs]
```
