# Installation Tests

This directory contains tests to verify that the `epub_toc` package can be properly installed and imported.

## Test Files

1. `test_installation.sh` - Shell script to test installation in clean virtual environments
   - Tests regular installation on Python 3.7-3.11
   - Tests editable installation
   - Verifies imports and version
   - Cleans up after tests

2. `test_installation.py` - Python unit tests for installation verification
   - Tests package presence in sys.modules
   - Verifies version format
   - Checks all public interfaces are importable
   - Verifies dependencies are installed
   - Validates package metadata

## Running Tests

### Shell Script Tests
```bash
# Make script executable
chmod +x test_installation.sh

# Run installation tests
./test_installation.sh
```

### Python Unit Tests
```bash
# Run with unittest
python -m unittest test_installation.py

# Or with pytest
pytest test_installation.py
```

## Test Coverage

The tests verify:
1. Package Installation
   - Regular pip install
   - Editable install (-e flag)
   - Multiple Python versions

2. Package Structure
   - All public interfaces available
   - Version information present
   - Package metadata correct

3. Dependencies
   - All required packages installed
   - Version requirements met

4. Import Functionality
   - Package can be imported
   - All submodules accessible
   - Public API available

## Requirements

- Python versions 3.7-3.11 installed
- pip and virtualenv/venv
- Access to PyPI or local package distribution 