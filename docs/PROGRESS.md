# Project Development Guidelines

## Project Status
- Version: 0.1.0
- Status: Alpha
- Code Coverage: 85%
- Python Support: 3.7+

## Development Principles

### SOLID Principles
1. Single Responsibility Principle (SRP)
   - Each class/module has one specific purpose
   - Clear separation of concerns

2. Open/Closed Principle (OCP)
   - Classes open for extension, closed for modification
   - Use inheritance and interfaces for extensibility

3. Liskov Substitution Principle (LSP)
   - Subclasses must enhance, not replace base class behavior
   - Maintain base class contracts

4. Interface Segregation Principle (ISP)
   - Keep interfaces small and focused
   - Clients shouldn't depend on unused methods

5. Dependency Inversion Principle (DIP)
   - Depend on abstractions, not implementations
   - Use dependency injection

### DRY (Don't Repeat Yourself)
- Avoid code duplication
- Extract common logic into utility functions
- Use shared components

## Best Practices
1. Documentation
   - All public methods must have docstrings
   - Keep README.md up to date
   - Document changes in CHANGELOG.md

2. Error Handling
   - Use specific exceptions
   - Add informative error messages
   - Log errors with context

3. Testing
   - Write unit tests for public methods
   - Maintain >80% code coverage
   - Use fixtures and mocks for isolation

4. Naming Conventions
   - Use meaningful variable and function names
   - Follow PEP 8 for Python code
   - Use snake_case for functions and variables

5. Security
   - No sensitive data in code
   - Use environment variables for configuration
   - Validate input data

6. Performance
   - Optimize after profiling
   - Use appropriate data structures
   - Avoid premature optimization

## Development Process
1. Planning
   - Document requirements
   - Create issues in tracker
   - Update CHANGELOG.md

2. Code
   - Follow project code style
   - Write self-documenting code
   - Make atomic commits

3. Review
   - Conduct code reviews
   - Run linters and tests
   - Check documentation

## Modularity and Reuse
1. Component Design
   - Develop independent modules
   - Minimize external dependencies
   - Create clear interfaces
   - Document integration requirements
   - Follow loose coupling principle
   - Maintain backward compatibility
   - Provide integration examples

2. Configuration
   - Use external config files
   - Provide default settings
   - Validate config parameters
   - Document all options

3. Versioning
   - Follow Semantic Versioning
   - Maintain changelog
   - Support multiple stable versions
   - Mark breaking changes clearly

## Community Guidelines
1. Contributing
   - Fork repository
   - Create feature branch
   - Follow coding standards
   - Submit pull request
   - Participate in code review

2. Communication
   - Use English for all communication
   - Be respectful and inclusive
   - Provide clear context
   - Welcome new contributors

## Release Schedule
- Alpha: Current
- Beta: Q2 2024
- 1.0: Q3 2024

## Support Channels
- GitHub Issues
- Discussions
- Documentation
- Stack Overflow tag 

# Project Progress

## Open Source Preparation Checklist

### ✅ Completed Steps
1. Package Configuration
   - Enhanced setup.py with proper PyPI metadata
   - Added pyproject.toml for modern Python packaging
   - Configured development dependencies

2. GitHub Templates and CI
   - Created GitHub Actions CI workflow
   - Added issue templates for bugs and feature requests
   - Added pull request template
   - Added installation testing to CI

3. Documentation Standards
   - Created DOCUMENTATION_STANDARD.md
   - Defined docstring format and rules
   - Enhanced module docstrings
   - Improved class documentation for TOCItem and EPUBTOCParser

4. Examples and Usage Documentation
   - Created examples directory structure
   - Added installation instructions
   - Created basic usage examples
   - Added advanced usage examples:
     - Basic TOC extraction
     - Custom extraction methods
     - Batch processing
     - Error handling

5. Installation Testing
   - Added shell script for testing installation
   - Added Python unit tests for installation verification
   - Integrated installation tests into CI workflow
   - Test both regular and editable installs
   - Test across Python versions 3.7-3.11

### 🔄 In Progress
1. Documentation Improvements
   - [x] Created documentation standards
   - [x] Enhanced module docstrings
   - [x] Improved main class documentation
   - [x] Created usage examples
   - [ ] Add API documentation
   - [ ] Create a detailed development guide
   - [ ] Set up documentation generation (Sphinx/MkDocs)

2. Testing and Quality
   - [x] Review and enhance test coverage (Current: 85%)
   - [x] Add integration tests (31 tests total)
   - [ ] Fix JSON export validation (30 files failing)
   - [ ] Add benchmarks
   - [ ] Address ebooklib deprecation warnings (60 warnings)

### 📝 Pending Steps
1. Testing and Quality Improvements
   - [ ] Fix JSON validation in test_json_export
   - [ ] Update ebooklib usage to address warnings
   - [ ] Add performance benchmarks
   - [ ] Increase test coverage to 90%

2. Distribution Preparation
   - [ ] Create PyPI account
   - [ ] Test package installation from TestPyPI
   - [ ] Prepare first release
   - [ ] Create MANIFEST.in if needed

3. Repository Enhancement
   - [ ] Add badges to README
     - [ ] PyPI version
     - [ ] Python versions
     - [ ] CI status
     - [ ] Test coverage
   - [ ] Update CHANGELOG.md with proper versioning
   - [ ] Review and update package metadata

## Development Progress

### Current Sprint
- Improving documentation quality
- Setting up documentation infrastructure
- Enhancing test coverage

### Next Steps
1. Set up Sphinx/MkDocs for documentation generation
2. Enhance test coverage
3. Prepare for PyPI distribution

### Notes
- All changes should follow project's style guidelines
- Keep CHANGELOG.md updated with all changes
- Document all decisions and architectural choices 

## TOC Extraction Methods Analysis

### Method Effectiveness

1. **epub_meta Method**
   - Works only for well-structured EPUB files (~10% success rate)
   - Provides consistent results when available
   - Limited by metadata quality

2. **NCX Method**
   - Most reliable for structured EPUBs (~90% success rate)
   - Provides hierarchical navigation
   - Fails when NCX file is missing or empty

3. **OPF Method**
   - Works for all EPUB files (100% success rate)
   - Can produce too many items (needs filtering)
   - Best as a fallback method

4. **Automatic Extraction**
   - Combines benefits of all methods
   - Intelligently selects best results
   - Provides consistent output format

### Best Practices for TOC Extraction

1. **Method Selection**
   - Try NCX method first
   - Fall back to epub_meta if available
   - Use OPF as last resort
   - Apply filtering for large TOCs

2. **Quality Assurance**
   - Validate TOC structure
   - Check for reasonable item count
   - Verify hierarchy levels
   - Test navigation links

3. **Performance Optimization**
   - Cache extraction results
   - Implement parallel processing
   - Filter unnecessary items early
   - Optimize memory usage

### Future Improvements

1. **Content Analysis**
   - Implement semantic section detection
   - Add support for custom markers
   - Improve heading recognition

2. **Hybrid Approach**
   - Combine multiple method results
   - Implement smart filtering
   - Add confidence scoring

3. **Error Handling**
   - Improve error reporting
   - Add recovery mechanisms
   - Implement validation checks 

## Test Results Analysis (2024-12-26)

### Current Status
- Total Tests: 31
- Passed: 31
- Failed: 0
- Warnings: 60 (ebooklib deprecation notices)
- Coverage: 85%

### Recent Changes
1. JSON Export Format
   - Simplified JSON structure
   - Removed unnecessary fields
   - Added required metadata fields
   - Fixed validation issues

2. Test Updates
   - Updated test cases for new format
   - Added more validation checks
   - Improved error messages
   - Fixed integration tests

3. Documentation
   - Updated format specifications
   - Added validation rules
   - Improved examples
   - Fixed outdated references

### Issues to Address
1. ebooklib Warnings
   - Future version will change ignore_ncx default to True
   - XML search behavior will be updated
   - Need to update code to handle these changes

### Action Items
1. [x] Review and fix JSON export validation
2. [ ] Update ebooklib usage for future compatibility
3. [x] Document JSON format requirements
4. [x] Add validation tests for each export format 

## Testing Strategy

### Test Structure
```
tests/
├── unit/          # Unit tests for individual components
├── integration/   # Integration tests for component interactions
├── installation/  # Package installation tests
├── data/         # Test data and fixtures
└── conftest.py   # Shared test configurations
```

### Testing Principles
1. **Transparency**
   - Clear test structure with separate directories for different test types
   - Descriptive test names that explain the test purpose
   - Detailed test documentation and comments
   - Visual feedback during test execution

2. **Test Coverage**
   - Unit tests for individual components
   - Integration tests for component interactions
   - Installation tests for package deployment
   - Coverage tracking with visual reporting

3. **Quality Metrics**
   - Code coverage target: >80%
   - Quality ratings: Excellent (90%+), Very Good (80%+), Good (70%+)
   - Visual progress indicators
   - Detailed HTML coverage reports

4. **Development Process**
   - Test-driven development (TDD) approach
   - Continuous integration with automated testing
   - Regular test suite maintenance
   - Performance benchmarking

### Test Execution
The `run_tests.sh` script provides:
- Real-time progress visualization
- Multiple progress indicators
- Coverage quality assessment
- Detailed test results
- HTML coverage reports 

### Test Writing Principles

1. **Documentation**
   - Each test module has a clear docstring explaining its purpose
   - Test functions have descriptive names and docstrings
   - Complex test logic includes inline comments
   - Test fixtures are well-documented

2. **Test Organization**
   - Tests are grouped by functionality
   - Fixtures provide reusable test data
   - Helper functions encapsulate common validation logic
   - Clear separation of test cases

3. **Error Handling**
   - Explicit error checking
   - Validation of error conditions
   - Clear error messages
   - Proper exception handling

4. **Test Coverage**
   - Basic functionality tests
   - Edge case testing
   - Error condition testing
   - Integration scenarios

5. **Test Data Management**
   - Centralized test data storage
   - Reusable test fixtures
   - Clear data validation
   - Sample data for different scenarios

### Example Test Structure
```python
def test_feature():
    """Test description explaining purpose and approach."""
    # Setup
    test_data = prepare_test_data()
    
    # Test execution
    result = function_under_test(test_data)
    
    # Validation
    assert expected_condition(result)
    validate_specific_aspects(result)
``` 

### Test Examples from Codebase

1. **Unit Test Example**
```python
def test_toc_item_creation():
    """Test TOCItem creation and default values."""
    item = TOCItem(title="Test", href="test.html", level=0)
    assert item.title == "Test"
    assert item.href == "test.html"
    assert item.level == 0
    assert item.children == []
    assert item.description is None
```
- Clear purpose in docstring
- Tests basic functionality
- Validates all attributes
- Checks default values

2. **Integration Test Example**
```python
def test_extraction_methods(sample_epub_files):
    """Test individual extraction methods."""
    results = {}
    errors = {}
    
    for epub_file in sample_epub_files:
        parser = EPUBTOCParser(epub_file)
        
        for method_name, method_attr in EPUBTOCParser.EXTRACTION_METHODS:
            try:
                method = getattr(parser, method_attr)
                result = method()
                # ... validation logic ...
            except Exception as e:
                errors.setdefault(method_name, []).append({
                    'file': epub_file.name,
                    'error': str(e)
                })
```
- Tests component interaction
- Handles errors gracefully
- Provides detailed reporting
- Uses real test data

3. **Test Fixtures Example**
```python
@pytest.fixture
def sample_toc_item():
    """Create a sample TOC item for testing."""
    parent = TOCItem(
        title="Test Chapter",
        href="chapter1.html",
        level=0
    )
    child = TOCItem(
        title="Test Section",
        href="chapter1.html#section1",
        level=1
    )
    parent.add_child(child)
    return parent
```
- Reusable test data
- Clear documentation
- Representative sample
- Hierarchical structure

4. **Error Handling Example**
```python
def test_parser_initialization_with_invalid_file():
    """Test parser initialization with non-existent file."""
    with pytest.raises(ValidationError, match="File not found"):
        EPUBTOCParser("nonexistent.epub")
```
- Explicit error checking
- Clear error messages
- Specific error types
- Pattern matching 

### Test Visualization and Monitoring

1. **Real-time Progress**
```bash
┌───────────────────────────────────────┐
│          Test Suite Runner            │
└───────────────────────────────────────┘

⠹ Running tests... ▃ ⡿ [00:00:01]
```
- Animated progress indicators
- Multiple visual elements
- Time tracking
- Clear status display

2. **Test Results Display**
```
┌───────────────────────────────────────┐
│ Total Tests:  31                      │
│ Passed:       31                      │
│ Warnings:     0                       │
└───────────────────────────────────────┘
```
- Clear statistics
- Color-coded results
- Structured layout
- Warning tracking

3. **Coverage Report**
```
┌─────────────── Coverage Summary ─────────────┐
│ Coverage: 87.5%                              │
│ [████████████████████░░░░░░░░░░░░░░░░░░] │
├─────────────── Quality Rating ─────────────┤
│ ▰▰▰▰ Very Good                             │
└──────────────────────────────────────────┘
```
- Visual coverage bar
- Quality indicators
- Percentage display
- Rating system

4. **Monitoring Features**
- Real-time test execution tracking
- Visual progress indicators
- Performance metrics
- Error highlighting
- Coverage trending 