#!/usr/bin/env python3

import sys
from pathlib import Path
from epub_toc import EPUBTOCParser

def analyze_epub(epub_path, output_dir):
    """Analyze EPUB file and test different extraction methods."""
    print(f"\nAnalyzing {epub_path.name}...")
    
    try:
        parser = EPUBTOCParser(epub_path)
        
        # Try each extraction method
        print("\nTesting extraction methods:")
        
        print("1. epub_meta method:", end=" ")
        try:
            meta_toc = parser._extract_from_epub_meta()
            if meta_toc:
                print("✓ Success")
                print(f"  Items found: {len(meta_toc)}")
            else:
                print("✗ No TOC found")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            
        print("2. NCX method:", end=" ")
        try:
            ncx_toc = parser._extract_from_ncx()
            if ncx_toc:
                print("✓ Success")
                print(f"  Items found: {len(ncx_toc)}")
            else:
                print("✗ No TOC found")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            
        print("3. OPF method:", end=" ")
        try:
            opf_toc = parser._extract_from_opf()
            if opf_toc:
                print("✓ Success")
                print(f"  Items found: {len(opf_toc)}")
            else:
                print("✗ No TOC found")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            
        # Try automatic extraction
        print("\nTrying automatic extraction:")
        try:
            toc = parser.extract_toc()
            print("✓ Success")
            print(f"Items found: {len(toc)}")
            
            # Save to JSON
            json_path = output_dir / f"{epub_path.stem}_toc.json"
            parser.save_toc_to_json(json_path)
            print(f"TOC saved to: {json_path}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")

def process_directory(input_dir, output_dir):
    """Process all EPUB files in the input directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all EPUB files
    epub_files = list(input_path.glob("*.epub"))
    
    if not epub_files:
        print(f"No EPUB files found in {input_dir}")
        return
        
    print(f"Found {len(epub_files)} EPUB files")
    
    # Process each file
    for epub_file in epub_files:
        analyze_epub(epub_file, output_path)

def main():
    input_dir = "tests/data/epub_samples"
    output_dir = "tests/data/epub_toc_json"
    
    if not Path(input_dir).exists():
        print(f"Error: Input directory {input_dir} not found")
        sys.exit(1)
        
    process_directory(input_dir, output_dir)

if __name__ == '__main__':
    main() 