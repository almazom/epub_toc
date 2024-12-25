# EPUB TOC Examples

This directory contains examples of using the `epub_toc` package.

## Installation

```bash
# Install from PyPI
pip install epub_toc

# Install in development mode from source
git clone https://github.com/almazilaletdinov/epub_toc.git
cd epub_toc
pip install -e .
```

## Basic Usage

```python
from epub_toc import EPUBTOCParser

# Create parser instance
parser = EPUBTOCParser('path/to/your/book.epub')

# Extract table of contents
toc = parser.extract_toc()

# Print TOC to console
parser.print_toc()

# Save TOC to JSON file
parser.save_toc_to_json('toc.json')
```

## Advanced Usage Examples

1. [basic_extraction.py](basic_extraction.py) - Simple TOC extraction
2. [custom_methods.py](custom_methods.py) - Using specific extraction methods
3. [batch_processing.py](batch_processing.py) - Processing multiple EPUB files
4. [error_handling.py](error_handling.py) - Handling various error cases 