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
            
            # Try each extraction method
            meta_toc = parser._extract_from_epub_meta()
            ncx_toc = parser._extract_from_ncx()
            opf_toc = parser._extract_from_opf()
            
            if meta_toc:
                result["extraction_method"] = "epub_meta"
            elif ncx_toc:
                result["extraction_method"] = "ncx"
            elif opf_toc:
                result["extraction_method"] = "opf"
            
            # Extract full TOC
            toc = parser.extract_toc()
            if toc:
                # Validate TOC structure
                validation_errors = []
                for item in toc:
                    if not item.get("title", "").strip():
                        validation_errors.append("Empty title found")
                    if not item.get("href", "").strip():
                        validation_errors.append("Empty href found")
                    if not isinstance(item.get("level"), int):
                        validation_errors.append("Invalid level type")
                    elif item.get("level", -1) < 0:
                        validation_errors.append("Negative level found")
                    if not isinstance(item.get("children", []), list):
                        validation_errors.append("Children not a list")
                
                if not validation_errors:
                    result["success"] = True
                    result["toc_items"] = len(toc)
                    
                    # Calculate max depth
                    def get_depth(items, current_depth=0):
                        if not items:
                            return current_depth
                        return max(get_depth(item.get("children", []), current_depth + 1) for item in items)
                    
                    result["max_depth"] = get_depth(toc)
                    
                    # Save TOC to JSON
                    json_path = output_dir / f"{epub_file.stem}_toc.json"
                    parser.save_toc_to_json(json_path)
                    result["toc_file"] = json_path.name
                else:
                    result["validation_errors"] = validation_errors
                    result["error"] = "Validation failed"
                    
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
            
        results.append(result)
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "successful_extractions": sum(1 for r in results if r["success"]),
        "failed_extractions": sum(1 for r in results if not r["success"]),
        "extraction_methods": {
            "epub_meta": sum(1 for r in results if r["extraction_method"] == "epub_meta"),
            "ncx": sum(1 for r in results if r["extraction_method"] == "ncx"),
            "opf": sum(1 for r in results if r["extraction_method"] == "opf")
        },
        "files": results
    }
    
    # Save JSON report
    json_report_path = report_dir / f"epub_analysis_{timestamp}.json"
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Save text report
    txt_report_path = report_dir / f"epub_analysis_{timestamp}.txt"
    with open(txt_report_path, "w", encoding="utf-8") as f:
        f.write("=== EPUB TOC Extraction Report ===\n\n")
        f.write(f"Timestamp: {report['timestamp']}\n")
        f.write(f"Total files processed: {report['total_files']}\n")
        f.write(f"Successful extractions: {report['successful_extractions']}\n")
        f.write(f"Failed extractions: {report['failed_extractions']}\n\n")
        
        f.write("Extraction methods used:\n")
        f.write(f"- epub_meta: {report['extraction_methods']['epub_meta']}\n")
        f.write(f"- NCX: {report['extraction_methods']['ncx']}\n")
        f.write(f"- OPF: {report['extraction_methods']['opf']}\n\n")
        
        f.write("File details:\n")
        for result in sorted(results, key=lambda x: x["file_name"]):
            f.write(f"\n{result['file_name']}:\n")
            f.write(f"  Size: {result['file_size']:.1f} KB\n")
            f.write(f"  Success: {'Yes' if result['success'] else 'No'}\n")
            if result["success"]:
                f.write(f"  Extraction method: {result['extraction_method']}\n")
                f.write(f"  TOC items: {result['toc_items']}\n")
                f.write(f"  Max depth: {result['max_depth']}\n")
                f.write(f"  TOC file: {result['toc_file']}\n")
            if result["error"]:
                f.write(f"  Error: {result['error']}\n")
            if result["validation_errors"]:
                f.write("  Validation errors:\n")
                for error in result["validation_errors"]:
                    f.write(f"    - {error}\n")
    
    # Validate results
    assert report["total_files"] > 0, "No files were processed"
    assert report["successful_extractions"] > 0, "No successful extractions"
    assert len(list(output_dir.glob("*.json"))) > 0, "No TOC files were created" 