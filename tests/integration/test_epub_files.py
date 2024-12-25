"""Integration tests for EPUB file handling."""

import pytest
from pathlib import Path
from epub_toc import (
    EPUBTOCParser,
    TOCItem,
    ValidationError,
    ExtractionError
)

# Fixture for test EPUB files directory
@pytest.fixture
def epub_samples_dir():
    """Return path to directory with test EPUB files."""
    return Path(__file__).parent.parent / "data" / "epub_samples"

def test_epub_file_not_found():
    """Test behavior with non-existent EPUB file."""
    with pytest.raises(ValidationError):
        EPUBTOCParser("nonexistent_book.epub")

@pytest.mark.skipif(
    not (Path(__file__).parent.parent / "data" / "epub_samples").exists(),
    reason="Test EPUB files not available"
)
def test_sample_epub_extraction(epub_samples_dir):
    """Test TOC extraction from sample EPUB files."""
    # Only process actual files, not directories
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    failed_files = []
    for epub_file in epub_files:
        try:
            parser = EPUBTOCParser(epub_file)
            toc = parser.extract_toc()
            
            # Basic validation of extracted TOC
            assert toc is not None, f"Failed to extract TOC from {epub_file.name}"
            assert isinstance(toc, list), f"TOC from {epub_file.name} should be a list"
            assert len(toc) > 0, f"TOC from {epub_file.name} should not be empty"
            
            # Validate TOC structure
            for item in toc:
                assert "title" in item, f"TOC item from {epub_file.name} should have title"
                assert "href" in item, f"TOC item from {epub_file.name} should have href"
                assert "level" in item, f"TOC item from {epub_file.name} should have level"
                assert isinstance(item["children"], list), f"children in {epub_file.name} should be a list"
                
                # Additional validations
                assert item["title"].strip(), f"Empty title in TOC item from {epub_file.name}"
                assert item["href"].strip(), f"Empty href in TOC item from {epub_file.name}"
                assert isinstance(item["level"], int), f"Level in {epub_file.name} should be integer"
                assert item["level"] >= 0, f"Level in {epub_file.name} should be non-negative"
                
        except Exception as e:
            failed_files.append((epub_file.name, str(e)))
    
    if failed_files:
        print("\nFailed files in test_sample_epub_extraction:")
        for name, error in failed_files:
            print(f"- {name}: {error}")
        pytest.fail(f"Test failed for {len(failed_files)} files")

@pytest.mark.skipif(
    not (Path(__file__).parent.parent / "data" / "epub_samples").exists(),
    reason="Test EPUB files not available"
)
def test_json_export(epub_samples_dir, tmp_path):
    """Test JSON export functionality with real EPUB files."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    failed_files = []
    for epub_file in epub_files:
        try:
            parser = EPUBTOCParser(epub_file)
            toc = parser.extract_toc()
            
            # Save to temporary file
            json_path = tmp_path / f"{epub_file.stem}_toc.json"
            parser.save_toc_to_json(json_path)
            
            # Verify JSON file
            assert json_path.exists(), f"JSON file for {epub_file.name} should be created"
            assert json_path.stat().st_size > 0, f"JSON file for {epub_file.name} should not be empty"
            
            # Validate JSON structure
            import json
            with open(json_path) as f:
                data = json.load(f)
                assert isinstance(data, list), f"JSON data for {epub_file.name} should be a list"
                assert len(data) > 0, f"JSON data for {epub_file.name} should not be empty"
                
                for item in data:
                    assert "title" in item, f"JSON item from {epub_file.name} missing title"
                    assert "href" in item, f"JSON item from {epub_file.name} missing href"
                    assert "level" in item, f"JSON item from {epub_file.name} missing level"
                    assert "children" in item, f"JSON item from {epub_file.name} missing children"
                    
        except Exception as e:
            failed_files.append((epub_file.name, str(e)))
    
    if failed_files:
        print("\nFailed files in test_json_export:")
        for name, error in failed_files:
            print(f"- {name}: {error}")
        pytest.fail(f"Test failed for {len(failed_files)} files")

def test_extraction_methods(epub_samples_dir):
    """Test all extraction methods with real EPUB files."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    failed_files = []
    method_success = {
        "epub_meta": [],
        "ncx": [],
        "opf": []
    }
    
    for epub_file in epub_files:
        try:
            parser = EPUBTOCParser(epub_file)
            
            # Test each method separately
            epub_meta_toc = parser._extract_from_epub_meta()
            ncx_toc = parser._extract_from_ncx()
            opf_toc = parser._extract_from_opf()
            
            # Track successful methods
            if epub_meta_toc:
                method_success["epub_meta"].append(epub_file.name)
            if ncx_toc:
                method_success["ncx"].append(epub_file.name)
            if opf_toc:
                method_success["opf"].append(epub_file.name)
            
            # At least one method should work
            assert any([epub_meta_toc, ncx_toc, opf_toc]), \
                f"No extraction method worked for {epub_file.name}"
            
            # Verify structure of successful extractions
            for method_name, toc in [
                ("epub_meta", epub_meta_toc),
                ("ncx", ncx_toc),
                ("opf", opf_toc)
            ]:
                if toc:
                    assert isinstance(toc, list), \
                        f"{method_name} TOC for {epub_file.name} should be a list"
                    assert len(toc) > 0, \
                        f"{method_name} TOC for {epub_file.name} should not be empty"
                    assert all(isinstance(item, TOCItem) for item in toc), \
                        f"{method_name} TOC items for {epub_file.name} should be TOCItem instances"
                    assert all(hasattr(item, 'title') for item in toc), \
                        f"{method_name} TOC items for {epub_file.name} should have title"
                    
        except Exception as e:
            failed_files.append((epub_file.name, str(e)))
    
    # Print method success statistics
    print("\nExtraction method success rates:")
    for method, successful_files in method_success.items():
        success_rate = len(successful_files) / len(epub_files) * 100
        print(f"- {method}: {success_rate:.1f}% ({len(successful_files)}/{len(epub_files)})")
        if successful_files:
            print(f"  Successful files: {', '.join(successful_files)}")
    
    if failed_files:
        print("\nFailed files in test_extraction_methods:")
        for name, error in failed_files:
            print(f"- {name}: {error}")
        pytest.fail(f"Test failed for {len(failed_files)} files") 