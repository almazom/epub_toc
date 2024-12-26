# EPUB TOC

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/epub-toc.svg)](https://badge.fury.io/py/epub-toc)
[![Downloads](https://pepy.tech/badge/epub-toc)](https://pepy.tech/project/epub-toc)
[![PyPI Status](https://img.shields.io/pypi/status/epub-toc.svg)](https://pypi.python.org/pypi/epub-toc)
[![Tests](https://github.com/almazilaletdinov/epub_toc/workflows/Tests/badge.svg)](https://github.com/almazilaletdinov/epub_toc/actions)

A Python tool for extracting table of contents from EPUB files with hierarchical structure support.

## Features
- Multiple extraction methods support (NCX, epub_meta, OPF)
- Automatic best method selection
- Hierarchical TOC structure preservation
- Russian and English language support
- JSON output format
- Detailed logging
- EPUB file analysis reports

## Installation

### From PyPI (recommended)

```bash
pip install epub_toc
```

### From source (for development)

```bash
git clone https://github.com/almazilaletdinov/epub_toc.git
cd epub_toc
pip install -e .
```

### Verify installation

```bash
python -c "import epub_toc; print(epub_toc.__version__)"
```

### Dependencies

All dependencies will be automatically installed with pip:
- epub_meta>=0.0.7
- lxml>=4.9.3
- beautifulsoup4>=4.12.2
- ebooklib>=0.18
- tika>=2.6

For development, additional dependencies can be installed with:
```bash
pip install -e .[dev]
```

## Usage

### As a module

```python
from epub_toc import EPUBTOCParser

# Create parser
parser = EPUBTOCParser('path/to/book.epub')

# Extract TOC
toc = parser.extract_toc()

# Print to console
parser.print_toc()

# Save to JSON
parser.save_toc_to_json('output.json')
```

### From command line

```bash
epub-toc path/to/book.epub
```

### EPUB File Analysis

To analyze all EPUB files in tests/data/epub_samples directory:

```bash
python tests/integration/test_epub_analysis.py
```

Analysis results are saved in `reports/` directory:
- `epub_analysis_YYYYMMDD_HHMMSS.json` - detailed report in JSON format
- `epub_analysis_YYYYMMDD_HHMMSS.txt` - brief report in text format
- `toc/*.json` - extracted TOCs for each EPUB file

Report structure:
1. JSON report contains:
   - Overall statistics for all files
   - Extraction methods success rate
   - Detailed results for each file
   - Links to extracted TOC files

2. Text report includes:
   - Brief statistics
   - Information about each file
   - Paths to extracted TOCs

3. TOC files:
   - Saved in `toc/` subdirectory
   - Named as `book_name_toc.json`
   - Contain complete TOC in JSON format

## Output Format

TOC is saved in JSON format with the following structure:

```json
{
  "metadata": {
    "title": "Book Title",
    "authors": ["Author 1", "Author 2"],
    "publisher": "Publisher Name",
    "publication_date": "2024-01-01",
    "language": "en",
    "description": "Book description",
    "cover_image_path": "path/to/cover.jpg",
    "isbn": "978-3-16-148410-0",
    "rights": "Copyright information",
    "series": "Series Name",
    "series_index": 1,
    "identifiers": {
      "isbn13": "978-3-16-148410-0",
      "uuid": "550e8400-e29b-41d4-a716-446655440000"
    },
    "subjects": ["Fiction", "Adventure"],
    "file_size": 1234567,
    "file_name": "book.epub"
  },
  "toc": [
    {
      "title": "Chapter 1",
      "href": "chapter1.html",
      "level": 0,
      "children": [
        {
          "title": "Section 1.1",
          "href": "chapter1.html#section1",
          "level": 1,
          "children": []
        }
      ]
    }
  ]
}
```

All metadata fields are optional and will be omitted if not available in the EPUB file.

## Testing

The module includes comprehensive test suites:

### Running Tests

To run all tests with detailed reporting:

```bash
./run_tests.sh
```

This will run:
- Installation tests (pip install/uninstall)
- Integration tests (EPUB parsing, TOC extraction)
- Unit tests (core functionality)

### Test Coverage

The test suite includes:
- Installation verification
- Package dependencies
- Russian books (NCX method)
- English books (epub_meta method)
- Files with different TOC structures
- Files of different sizes (from 400KB to 8MB)

Test results and coverage reports are generated in:
- `coverage.xml` - Code coverage report
- `reports/` - Test execution reports
- `tests/data/epub_toc_json/` - Generated TOC files

## Requirements
- Python 3.7+
- epub_meta>=0.0.7
- lxml>=4.9.3
- beautifulsoup4>=4.12.2 

## Contributing

We welcome contributions! If you'd like to help:

1. Fork the repository
2. Create a branch for your changes
3. Make changes and add tests
4. Ensure all tests pass
5. Create a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Security

If you discover a security vulnerability, please DO NOT create a public issue.
Instead, send a report following the instructions in [SECURITY.md](SECURITY.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Additional EPUB format support
- [ ] Improved complex hierarchical structure handling
- [ ] Integration with popular e-readers
- [ ] Web service API
- [ ] Additional language support 