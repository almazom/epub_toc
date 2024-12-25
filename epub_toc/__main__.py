"""Command line interface for EPUB TOC Parser."""

import sys
import logging
from pathlib import Path

from .parser import EPUBTOCParser
from .exceptions import ValidationError, ExtractionError

def main():
    """Run the parser from command line."""
    if len(sys.argv) != 2:
        print("Usage: python -m epub_toc path/to/book.epub")
        sys.exit(1)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    epub_path = sys.argv[1]
    
    try:
        parser = EPUBTOCParser(epub_path)
        toc = parser.extract_toc()
        
        # Print TOC
        parser.print_toc()
        
        # Save to JSON
        output_path = str(Path(epub_path).with_suffix('')) + '_toc.json'
        parser.save_toc_to_json(output_path)
        print(f"\nTOC saved to {output_path}")
        
    except (ValidationError, ExtractionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 