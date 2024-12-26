"""Integration tests for EPUB analysis functionality."""

import json
import pytest
import shutil
from pathlib import Path
from datetime import datetime
from epub_toc import EPUBTOCParser

def test_epub_analysis(epub_samples_dir):
    """Test analysis of EPUB files."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    success_count = 0
    failed_files = []
    
    for epub_file in epub_files:
        try:
            parser = EPUBTOCParser(epub_file)
            toc = parser.extract_toc()
            
            # Basic validation
            assert isinstance(toc, list), f"TOC for {epub_file.name} is not a list"
            assert len(toc) > 0, f"TOC for {epub_file.name} is empty"
            
            # Structure validation
            for item in toc:
                assert "title" in item, f"Missing title in TOC item for {epub_file.name}"
                assert "href" in item, f"Missing href in TOC item for {epub_file.name}"
                assert "level" in item, f"Missing level in TOC item for {epub_file.name}"
                assert isinstance(item["children"], list), f"Children not a list in TOC item for {epub_file.name}"
                
                # Validate title
                assert item["title"].strip(), f"Empty title in TOC item for {epub_file.name}"
                
                # Validate href
                assert item["href"].strip(), f"Empty href in TOC item for {epub_file.name}"
                
                # Validate level
                assert isinstance(item["level"], int), f"Level not an integer in TOC item for {epub_file.name}"
                assert item["level"] >= 0, f"Negative level in TOC item for {epub_file.name}"
            
            success_count += 1
            
        except Exception as e:
            failed_files.append((epub_file.name, str(e)))
            continue
    
    # Report failures
    if failed_files:
        print("\nFailed files:")
        for name, error in failed_files:
            print(f"- {name}: {error}")
    
    assert success_count > 0, f"No files were successfully processed. Failed files: {failed_files}"

def test_epub_analysis_with_report(epub_samples_dir, tmp_path):
    """Test EPUB analysis with detailed report and JSON export."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    # Create output directories
    output_dir = tmp_path / "epub_toc_json"
    output_dir.mkdir(exist_ok=True)
    
    report_dir = tmp_path / "reports"
    report_dir.mkdir(exist_ok=True)
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for epub_file in epub_files:
        result = {
            "file_name": epub_file.name,
            "file_size": epub_file.stat().st_size / 1024,  # KB
            "success": False,
            "extraction_method": None,
            "toc_items": 0,
            "max_depth": 0,
            "error": None,
            "toc_file": None,
            "validation_errors": []
        }
        
        try:
            parser = EPUBTOCParser(epub_file)
            toc = parser.extract_toc()
            
            if toc:
                result["success"] = True
                result["extraction_method"] = parser.extraction_method
                result["toc_items"] = len(toc)
                
                # Calculate max depth
                def get_depth(items, current_depth=0):
                    max_depth = current_depth
                    for item in items:
                        if "children" in item and item["children"]:
                            child_depth = get_depth(item["children"], current_depth + 1)
                            max_depth = max(max_depth, child_depth)
                    return max_depth
                
                result["max_depth"] = get_depth(toc)
                
                # Save TOC to JSON
                toc_file = output_dir / f"{epub_file.stem}_toc.json"
                parser.save_toc_to_json(toc_file)
                result["toc_file"] = toc_file.name
                
        except Exception as e:
            result["error"] = str(e)
            result["validation_errors"].append(str(e))
        
        results.append(result)
    
    # Generate report
    report_file = report_dir / f"epub_analysis_{timestamp}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generate text report
    text_report = report_dir / f"epub_analysis_{timestamp}.txt"
    with open(text_report, "w", encoding="utf-8") as f:
        f.write("EPUB TOC Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        f.write(f"Total files analyzed: {len(results)}\n")
        f.write(f"Successfully processed: {len(successful)}\n")
        f.write(f"Failed: {len(failed)}\n\n")
        
        if successful:
            f.write("\nSuccessful extractions:\n")
            f.write("-" * 30 + "\n")
            for r in successful:
                f.write(f"\nFile: {r['file_name']}\n")
                f.write(f"Method: {r['extraction_method']}\n")
                f.write(f"TOC items: {r['toc_items']}\n")
                f.write(f"Max depth: {r['max_depth']}\n")
                f.write(f"TOC file: {r['toc_file']}\n")
        
        if failed:
            f.write("\nFailed extractions:\n")
            f.write("-" * 30 + "\n")
            for r in failed:
                f.write(f"\nFile: {r['file_name']}\n")
                f.write(f"Error: {r['error']}\n")
                if r["validation_errors"]:
                    f.write("Validation errors:\n")
                    for err in r["validation_errors"]:
                        f.write(f"- {err}\n")
    
    assert len(successful) > 0, "No successful extractions" 