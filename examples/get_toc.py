#!/usr/bin/env python3
"""
Simple script to get TOC from EPUB file.
Usage:
    python get_toc.py path/to/file.epub
    python get_toc.py https://example.com/book.epub
"""

import sys
import json
from epub_toc import EPUBTOCParser

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def get_toc(path_or_url):
    extractor = EPUBTOCParser()
    if path_or_url.startswith(('http://', 'https://')):
        return extractor.extract_from_url(path_or_url)
    return extractor.extract_from_file(path_or_url)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  For local file:")
        print("    python get_toc.py path/to/file.epub")
        print("\n  For online EPUB:")
        print("    python get_toc.py https://example.com/book.epub")
        print("\nAvailable test files:")
        from epub_links import AVAILABLE_EPUBS
        for title, path in AVAILABLE_EPUBS.items():
            print(f"  - {path}")
        sys.exit(1)
    
    path_or_url = sys.argv[1]
    try:
        toc = get_toc(path_or_url)
        print_json(toc)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr) 