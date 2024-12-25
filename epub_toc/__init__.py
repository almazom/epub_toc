"""EPUB Table of Contents Extraction Package.

This package provides tools for extracting and manipulating table of contents
from EPUB files. It supports multiple extraction methods and preserves the
hierarchical structure of the TOC.

Examples:
    Basic usage:
    >>> from epub_toc import EPUBTOCParser
    >>> parser = EPUBTOCParser('book.epub')
    >>> toc = parser.extract_toc()
    >>> print(toc[0]['title'])
    'Chapter 1'

Notes:
    The package automatically selects the best extraction method based on
    the EPUB file structure and content.
"""

__version__ = "1.0.0"

from .parser import EPUBTOCParser, TOCItem
from .exceptions import (
    EPUBTOCError,
    ValidationError,
    ExtractionError,
    StructureError,
    ParsingError,
    ConversionError,
    OutputError
)

__all__ = [
    "EPUBTOCParser",
    "TOCItem",
    "EPUBTOCError",
    "ValidationError",
    "ExtractionError",
    "StructureError",
    "ParsingError",
    "ConversionError",
    "OutputError"
] 