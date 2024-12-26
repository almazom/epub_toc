"""Integration tests for EPUB TOC Parser."""

import pytest
from pathlib import Path
from typing import List, Dict

from epub_toc import (
    EPUBTOCParser,
    TOCItem,
    ValidationError,
    ExtractionError,
    StructureError,
    ParsingError
)

def validate_toc_structure(toc_items: List[Dict]) -> List[str]:
    """Validate TOC structure with simplified checks."""
    errors = []
    
    def validate_item(item: Dict, path: str = "root"):
        # Only check if required fields exist
        required_fields = ['title', 'href']
        
        for field in required_fields:
            if field not in item:
                errors.append(f"{path}: Missing required field '{field}'")
        
        # Check children if they exist
        if 'children' in item and isinstance(item['children'], list):
            for i, child in enumerate(item['children']):
                validate_item(child, f"{path}->child[{i}]")
    
    # Handle both old and new format
    if isinstance(toc_items, dict) and 'toc' in toc_items:
        items_to_validate = toc_items['toc']
    else:
        items_to_validate = toc_items
    
    if not isinstance(items_to_validate, list):
        errors.append("TOC must be a list")
        return errors
        
    for i, item in enumerate(items_to_validate):
        validate_item(item, f"item[{i}]")
    
    return errors

@pytest.fixture
def sample_epub_files(epub_samples_dir):
    """Get list of sample EPUB files."""
    files = [
        f for f in epub_samples_dir.glob("*.epub")
        if f.is_file()  # Only include actual files, not directories
    ]
    if not files:
        pytest.skip("No EPUB files found in test directory")
    return files

def test_parser_initialization(sample_epub_files):
    """Test parser initialization with different configurations."""
    epub_file = sample_epub_files[0]
    
    # Test default initialization
    parser = EPUBTOCParser(epub_file)
    assert parser.active_methods == EPUBTOCParser.EXTRACTION_METHODS
    
    # Test custom method selection
    methods = ['epub_meta', 'ncx']
    parser = EPUBTOCParser(epub_file, extraction_methods=methods)
    assert len(parser.active_methods) == 2
    assert all(m[0] in methods for m in parser.active_methods)
    
    # Test invalid file
    with pytest.raises(ValidationError):
        EPUBTOCParser("nonexistent.epub")
    
    # Test invalid methods
    with pytest.raises(ValidationError):
        EPUBTOCParser(epub_file, extraction_methods=[])

def test_toc_item_validation():
    """Test TOC item validation with simplified checks."""
    # Test valid item
    item = TOCItem("Title", "href.html", 0)
    assert item.title == "Title"
    assert item.href == "href.html"
    assert item.level == 0
    
    # Test missing title
    with pytest.raises(ValidationError):
        TOCItem("", "href.html", 0)
    
    # Test missing href
    with pytest.raises(ValidationError):
        TOCItem("Title", "", 0)

def test_extraction_methods(sample_epub_files):
    """Test individual extraction methods."""
    results = {}
    errors = {}
    
    for epub_file in sample_epub_files:
        parser = EPUBTOCParser(epub_file)
        
        for method_name, method_attr in EPUBTOCParser.EXTRACTION_METHODS:
            try:
                method = getattr(parser, method_attr)
                result = method()
                
                if result:
                    # Validate structure
                    toc_dicts = [item.to_dict() for item in result]
                    validation_errors = validate_toc_structure(toc_dicts)
                    
                    if not validation_errors:
                        results.setdefault(method_name, []).append(epub_file.name)
                    else:
                        errors.setdefault(method_name, []).append({
                            'file': epub_file.name,
                            'errors': validation_errors
                        })
                        
            except Exception as e:
                errors.setdefault(method_name, []).append({
                    'file': epub_file.name,
                    'error': str(e)
                })
    
    # Report results
    print("\nExtraction Method Results:")
    for method, successful_files in results.items():
        success_rate = len(successful_files) / len(sample_epub_files) * 100
        print(f"\n{method}:")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Successful files: {len(successful_files)}")
    
    print("\nExtraction Method Errors:")
    for method, method_errors in errors.items():
        print(f"\n{method}:")
        for error in method_errors:
            if 'errors' in error:
                print(f"- {error['file']}: Structure validation failed")
                for err in error['errors']:
                    print(f"  - {err}")
            else:
                print(f"- {error['file']}: {error['error']}")
    
    # Ensure at least one method works for each file
    for epub_file in sample_epub_files:
        assert any(
            epub_file.name in successful_files
            for successful_files in results.values()
        ), f"No extraction method succeeded for {epub_file.name}"

def test_fallback_behavior(sample_epub_files):
    """Test parser fallback behavior."""
    for epub_file in sample_epub_files:
        # Try with most reliable method first
        parser = EPUBTOCParser(epub_file, extraction_methods=['epub_meta'])
        
        try:
            toc = parser.extract_toc()
            # If succeeded, validate structure
            validation_errors = validate_toc_structure(toc)
            assert not validation_errors, f"Structure validation failed:\n" + "\n".join(validation_errors)
            
        except ExtractionError:
            # Try fallback to all methods
            parser = EPUBTOCParser(epub_file)
            toc = parser.extract_toc()
            validation_errors = validate_toc_structure(toc)
            assert not validation_errors, f"Structure validation failed:\n" + "\n".join(validation_errors)

def test_error_handling(sample_epub_files):
    """Test error handling with simplified validation."""
    epub_file = sample_epub_files[0]
    
    # Test with invalid extraction method
    with pytest.raises(ValidationError):
        parser = EPUBTOCParser(epub_file, extraction_methods=['invalid_method'])
    
    # Test with corrupted EPUB
    with pytest.raises(StructureError):
        with open("test.epub", "w") as f:
            f.write("Not an EPUB file")
        parser = EPUBTOCParser("test.epub")
        parser.extract_toc()

def test_toc_conversion():
    """Test TOC conversion between formats."""
    # Test valid conversion
    data = {
        'title': 'Chapter 1',
        'href': 'chapter1.html',
        'level': 0,
        'children': [
            {
                'title': 'Section 1.1',
                'href': 'section1.1.html',
                'level': 1,
                'children': []
            }
        ]
    }
    
    item = TOCItem.from_dict(data)
    assert item.title == 'Chapter 1'
    assert item.href == 'chapter1.html'
    assert item.level == 0
    assert len(item.children) == 1
    assert item.children[0].title == 'Section 1.1'
    
    # Test round-trip conversion
    converted = item.to_dict()
    assert converted == data

def test_toc_validation():
    """Test TOC validation with basic structure checks."""
    # Test valid minimal structure
    valid_data = {
        "metadata": {
            "title": "Test Book",
            "authors": ["Test Author"],
            "file_name": "test.epub",
            "file_size": 1000
        },
        "toc": [{
            "title": "Chapter 1",
            "href": "chapter1.html",
            "level": 0,
            "children": []
        }]
    }
    
    errors = validate_toc_structure(valid_data)
    assert not errors, "Valid TOC should pass validation"
    
    # Test missing required field
    invalid_data = {
        "metadata": {
            "title": "Test Book",
            "authors": ["Test Author"],
            "file_name": "test.epub"
        },
        "toc": [{
            "title": "Chapter 1",
            # missing href
            "level": 0,
            "children": []
        }]
    }
    errors = validate_toc_structure(invalid_data)
    assert len(errors) > 0, "Missing required field should fail validation"
    
    # Test invalid root structure
    invalid_data = {
        "metadata": {
            "title": "Test Book"
        }
        # missing toc
    }
    errors = validate_toc_structure(invalid_data)
    assert len(errors) > 0, "Invalid root structure should fail validation"

def test_toc_hierarchy():
    """Test TOC hierarchy with simplified validation."""
    # Valid hierarchy
    valid_toc = [{
        'title': 'Chapter 1',
        'href': 'chapter1.html',
        'children': [
            {
                'title': 'Section 1.1',
                'href': 'section1.1.html',
                'children': []
            }
        ]
    }]
    assert validate_toc_structure(valid_toc) == []
    
    # Invalid structure (missing required field)
    invalid_toc = [{
        'title': 'Chapter 1',
        # missing href
        'children': []
    }]
    errors = validate_toc_structure(invalid_toc)
    assert len(errors) > 0, "Expected validation errors for missing required field"

def test_toc_hierarchy_logic(sample_epub_files):
    """Test logical aspects of TOC hierarchy with relaxed validation."""
    for epub_file in sample_epub_files:
        parser = EPUBTOCParser(epub_file)
        toc = parser.extract_toc()
        
        def check_hierarchy_logic(items, parent_title=""):
            for item in items:
                # Title should be different from parent
                assert item['title'] != parent_title, \
                       f"Child title same as parent: {item['title']}"
                
                # Check children
                if 'children' in item and item['children']:
                    # Relaxed title length check
                    for child in item['children']:
                        assert len(child['title']) >= 1, \
                               f"Child title too short: {child['title']}"
                    
                    check_hierarchy_logic(item['children'], item['title'])
        
        check_hierarchy_logic(toc)

def test_functional_toc_extraction(sample_epub_files):
    """Test functional aspects of TOC extraction."""
    for epub_file in sample_epub_files:
        parser = EPUBTOCParser(epub_file)
        toc = parser.extract_toc()
        
        # Basic functional checks
        assert isinstance(toc, list), "TOC should be a list"
        
        def check_toc_item(item):
            # Check content validity
            assert 'title' in item, "Item should have a title"
            assert item['title'], "Title should not be empty"
            
            assert 'href' in item, "Item should have an href"
            assert item['href'], "Href should not be empty"
            
            # Check if href points to a valid file or anchor
            assert item['href'].endswith(('.html', '.xhtml', '.htm')) or '#' in item['href'], \
                   f"Invalid href format: {item['href']}"
            
            # Check children recursively
            if 'children' in item:
                assert isinstance(item['children'], list), "Children should be a list"
                for child in item['children']:
                    check_toc_item(child)
        
        # Check each top-level item
        for item in toc:
            check_toc_item(item)

def test_toc_content_consistency(sample_epub_files):
    """Test that extracted TOC content is consistent with EPUB content."""
    for epub_file in sample_epub_files:
        parser = EPUBTOCParser(epub_file)
        toc = parser.extract_toc()
        
        # Get all hrefs from TOC
        def collect_hrefs(item):
            hrefs = [item['href']]
            if 'children' in item:
                for child in item['children']:
                    hrefs.extend(collect_hrefs(child))
            return hrefs
            
        all_hrefs = []
        for item in toc:
            all_hrefs.extend(collect_hrefs(item))
            
        # Check that hrefs are unique
        unique_hrefs = set(all_hrefs)
        assert len(all_hrefs) == len(unique_hrefs), "TOC contains duplicate hrefs"
        
        # Check that hrefs follow a logical pattern
        for href in unique_hrefs:
            if '#' in href:
                base_href, anchor = href.split('#', 1)
                assert anchor, f"Empty anchor in href: {href}"
            else:
                assert any(href.endswith(ext) for ext in ['.html', '.xhtml', '.htm']), \
                       f"Invalid href extension: {href}"

def test_toc_extraction_methods_comparison(sample_epub_files):
    """Compare results from different extraction methods."""
    for epub_file in sample_epub_files:
        results = {}
        
        # Try each method individually
        for method_name in ['epub_meta', 'ncx', 'opf']:
            parser = EPUBTOCParser(epub_file, extraction_methods=[method_name])
            try:
                toc = parser.extract_toc()
                if toc:
                    results[method_name] = toc
            except Exception:
                continue
        
        # Skip if less than 2 methods succeeded
        if len(results) < 2:
            continue
            
        # Compare number of entries
        entry_counts = {method: len(toc) for method, toc in results.items()}
        max_diff = max(entry_counts.values()) - min(entry_counts.values())
        assert max_diff <= 2, f"Too much variance in TOC size between methods: {entry_counts}"
        
        # Compare titles (they should be similar between methods)
        for method1, toc1 in results.items():
            for method2, toc2 in results.items():
                if method1 >= method2:
                    continue
                    
                titles1 = set(item['title'] for item in toc1)
                titles2 = set(item['title'] for item in toc2)
                
                common_titles = titles1.intersection(titles2)
                assert len(common_titles) >= min(len(titles1), len(titles2)) * 0.5, \
                       f"Too few common titles between {method1} and {method2}" 