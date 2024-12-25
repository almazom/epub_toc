#!/usr/bin/env python3
"""Example of batch processing multiple EPUB files."""

import json
from pathlib import Path
from epub_toc import EPUBTOCParser, ExtractionError

def process_epub_file(epub_path):
    """Process a single EPUB file and return its TOC."""
    try:
        parser = EPUBTOCParser(epub_path)
        toc = parser.extract_toc()
        return {
            'status': 'success',
            'toc': toc,
            'error': None
        }
    except Exception as e:
        return {
            'status': 'error',
            'toc': None,
            'error': str(e)
        }

def batch_process_directory(input_dir, output_dir):
    """Process all EPUB files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all EPUB files
    epub_files = list(input_path.glob('**/*.epub'))
    print(f"Found {len(epub_files)} EPUB files to process")
    
    # Process each file
    results = {}
    for epub_file in epub_files:
        print(f"\nProcessing: {epub_file.name}")
        result = process_epub_file(epub_file)
        
        # Save individual TOC if extraction succeeded
        if result['status'] == 'success':
            output_file = output_path / f"{epub_file.stem}_toc.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result['toc'], f, ensure_ascii=False, indent=2)
            print(f"Saved TOC to: {output_file}")
        else:
            print(f"Failed to extract TOC: {result['error']}")
        
        # Store result
        results[epub_file.name] = result
    
    # Save summary report
    report_file = output_path / 'processing_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        summary = {
            'total_files': len(epub_files),
            'successful': sum(1 for r in results.values() if r['status'] == 'success'),
            'failed': sum(1 for r in results.values() if r['status'] == 'error'),
            'results': {
                name: {
                    'status': result['status'],
                    'error': result['error']
                }
                for name, result in results.items()
            }
        }
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved processing report to: {report_file}")

def main():
    # Process all EPUBs in sample_books directory
    batch_process_directory(
        input_dir='sample_books',
        output_dir='output/batch_results'
    )

if __name__ == '__main__':
    main() 