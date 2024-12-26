# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Project structure and documentation
- Basic TOC extraction functionality
- Test framework setup
- CI/CD pipeline configuration

## [1.0.0] - 2024-01-26
### Added
- First stable release on PyPI
- Automated installation tests in isolated environments
- Comprehensive test suite with categories
- Enhanced test reporting and visualization
- PyPI badges and installation documentation
- Test coverage reporting and analysis
- Automated dependency management
- Development mode installation support

### Changed
- Improved test organization and execution
- Enhanced documentation with installation verification
- Updated test runner script with better visualization
- Streamlined package installation process
- Automated dependency resolution

### Fixed
- Installation issues in different environments
- Package import after installation
- Development mode setup
- Dependency conflicts

## [0.1.0-alpha] - 2024-01-01

### Added
- Initial alpha release
- Support for multiple TOC extraction methods (NCX, epub_meta, OPF)
- Hierarchical TOC structure preservation
- JSON output format
- Command-line interface
- Basic test suite
- Logging system
- EPUB file analysis functionality

### Dependencies
- Python 3.7+
- epub_meta>=0.0.7
- lxml>=4.9.3
- beautifulsoup4>=4.12.2 

### Known Issues
- JSON export validation needs improvement
- Some ebooklib deprecation warnings present
- Test coverage at 85% (target: 90%) 