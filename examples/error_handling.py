#!/usr/bin/env python3
"""Example of handling various error cases when extracting TOC."""

from epub_toc import (
    EPUBTOCParser,
    EPUBTOCError,
    ValidationError,
    ExtractionError,
    StructureError
)

def demonstrate_error_handling(epub_path):
    """Demonstrate how to handle various error cases."""
    try:
        # Initialize parser
        parser = EPUBTOCParser(epub_path)
        
        # Try to extract TOC
        toc = parser.extract_toc()
        
        # If successful, print and save
        print("\nSuccessfully extracted TOC:")
        parser.print_toc()
        parser.save_toc_to_json('output/successful_toc.json')
        
    except ValidationError as e:
        print(f"\nValidation Error: {e}")
        print("This usually means:")
        print("- File doesn't exist")
        print("- File is not an EPUB")
        print("- File path points to a directory")
        
    except StructureError as e:
        print(f"\nStructure Error: {e}")
        print("This usually means:")
        print("- File is not a valid EPUB")
        print("- Required EPUB files are missing")
        print("- EPUB structure is corrupted")
        
    except ExtractionError as e:
        print(f"\nExtraction Error: {e}")
        print("This usually means:")
        print("- No TOC found in the EPUB")
        print("- All extraction methods failed")
        print("- TOC format is not supported")
        
    except EPUBTOCError as e:
        print(f"\nGeneral EPUB TOC Error: {e}")
        print("This is a base class for all epub_toc errors")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("This is not a specific epub_toc error")

def main():
    # Test with various problematic files
    test_files = [
        'sample_books/non_existent.epub',      # File doesn't exist
        'sample_books/not_an_epub.txt',        # Not an EPUB file
        'sample_books/corrupted.epub',         # Corrupted EPUB
        'sample_books/no_toc.epub',            # EPUB without TOC
        'sample_books/valid.epub'              # Valid EPUB (should succeed)
    ]
    
    for file_path in test_files:
        print(f"\nTesting with: {file_path}")
        print("-" * 50)
        demonstrate_error_handling(file_path)

if __name__ == '__main__':
    main() 