#!/usr/bin/env python3
"""Example of using specific TOC extraction methods."""

from epub_toc import EPUBTOCParser, ExtractionError

def extract_with_method(epub_path, methods):
    """Try to extract TOC using specified methods."""
    parser = EPUBTOCParser(epub_path, extraction_methods=methods)
    try:
        toc = parser.extract_toc()
        print(f"\nSuccessfully extracted using {methods}:")
        parser.print_toc()
        return True
    except ExtractionError as e:
        print(f"\nFailed to extract using {methods}:")
        print(str(e))
        return False

def main():
    epub_path = 'sample_books/book.epub'
    
    # Try different extraction methods
    methods_to_try = [
        ['ncx'],                    # Try NCX only
        ['epub_meta'],             # Try epub_meta only
        ['ncx', 'opf'],           # Try NCX, then OPF
        ['epub_meta', 'ncx', 'opf'] # Try all three in order
    ]
    
    for methods in methods_to_try:
        print(f"\nTrying extraction methods: {methods}")
        success = extract_with_method(epub_path, methods)
        print(f"Success: {success}")

if __name__ == '__main__':
    main() 