# Test Runner Documentation

## Overview

The test runner (`run_tests.sh`) is a comprehensive tool for executing and visualizing test results for the TOC Sandbox Module project. It provides rich visual feedback, progress tracking, and detailed test analytics.

## Features

- 🎨 Rich visual feedback with color-coded output
- 📊 Detailed test dashboard
- 📈 Progress tracking with phase information
- 📝 Comprehensive test reporting
- 🔄 CI/CD compatibility
- 📊 Coverage reporting
- 🛠 Environment validation
- 📋 Detailed logging with phase tracking
- 📁 Organized log file structure

## Requirements

- Python 3.8 or higher
- pytest
- pytest-cov (for coverage reports)

## Usage

```bash
./run_tests.sh [options]
```

### Options

- `-v, --verbose`: Show detailed test output
- `-q, --quiet`: Minimal output mode
- `-c, --coverage`: Generate coverage report
- `-h, --help`: Display help message

### Examples

1. Run all tests with default settings:
```bash
./run_tests.sh
```

2. Run tests with coverage report:
```bash
./run_tests.sh --coverage
```

3. Run tests in verbose mode:
```bash
./run_tests.sh --verbose
```

## Output Structure

### Logs Directory
All test outputs are stored in the `logs/` directory:
- `installation.log` - Package installation test results
- `unit_tests.log` - Unit test outputs and coverage data
- `integration.log` - Integration test results
- `type_check.log` - MyPy type checking results
- `black.log` - Code formatting check results
- `isort.log` - Import sorting check results
- `flake8.log` - Style check results
- `security.log` - Bandit security scan results

### Progress Information
The test runner now provides detailed progress information:
- Current phase of each test (Initializing/Running/Processing/Finalizing)
- Percentage completion for each phase
- Immediate feedback on test status
- Detailed error reporting when tests fail

### Test Dashboard
The test dashboard provides:
- Overall test statistics
- Pass/fail/skip counts
- Coverage metrics
- Performance analysis
- Resource usage statistics
- Strategy recommendations
- Phase-by-phase progress tracking
- Detailed error reporting

### Coverage Report
When running with `--coverage`:
- HTML coverage report is generated in `coverage/html/`
- Detailed line-by-line coverage analysis
- Branch coverage statistics
- Coverage trend analysis

## CI/CD Integration

The test runner automatically detects CI environments and adjusts its output accordingly:
- Disables interactive elements
- Ensures consistent output formatting
- Generates CI-friendly reports

## Troubleshooting

Common issues and solutions:

1. **Missing Requirements**
   - The script will check for required dependencies
   - Clear error messages with installation instructions
   - All error details are logged to specific files

2. **Permission Issues**
   ```bash
   chmod +x run_tests.sh
   ```

3. **Log Access**
   - All logs are stored in the `logs/` directory
   - Use `cat logs/<test_type>.log` to view specific test results
   - Error details are automatically displayed on test failure

4. **Progress Bar Issues**
   - Progress information shows current phase
   - Each phase has detailed status updates
   - Error messages are preserved in log files

## Best Practices

1. **Regular Log Review**
   - Check logs after each test run
   - Review error patterns in failed tests
   - Monitor test execution times

2. **Log Management**
   - Regularly clean old log files
   - Archive important test results
   - Use log rotation for long-running tests

3. **Error Analysis**
   - Check specific log files for detailed error information
   - Compare logs across test runs
   - Use error details for debugging

## Contributing

When modifying the test runner:
1. Maintain backward compatibility
2. Update documentation for new features
3. Test in both local and CI environments
4. Follow the existing code style
5. Update log handling for new test types
6. Maintain the logging structure 