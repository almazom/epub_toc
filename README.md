# EPUB TOC

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

```bash
pip install epub_toc
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
[
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
```

## Testing

The module has been successfully tested on various EPUB files:
- Russian books (NCX method)
- English books (epub_meta method)
- Files with different TOC structures
- Files of different sizes (from 400KB to 8MB)

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