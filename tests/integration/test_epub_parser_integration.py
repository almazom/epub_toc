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
    """Validate TOC structure and return list of validation errors."""
    errors = []
    
    def validate_item(item: Dict, path: str = "root"):
        required_fields = ['title', 'href', 'level']
        
        # Check required fields
        for field in required_fields:
            if field not in item:
                errors.append(f"{path}: Missing required field '{field}'")
            elif not isinstance(item[field], (str, int)):
                errors.append(f"{path}: Invalid type for field '{field}'")
        
        # Validate field values
        if 'title' in item and not item['title'].strip():
            errors.append(f"{path}: Empty title")
        
        if 'href' in item and not item['href'].strip():
            errors.append(f"{path}: Empty href")
        
        if 'level' in item:
            if not isinstance(item['level'], int):
                errors.append(f"{path}: Level must be integer")
            elif item['level'] < 0:
                errors.append(f"{path}: Level must be non-negative")
        
        # Check children
        if 'children' in item:
            if not isinstance(item['children'], list):
                errors.append(f"{path}: 'children' must be a list")
            else:
                for i, child in enumerate(item['children']):
                    validate_item(child, f"{path}->child[{i}]")
                    
                    # Check level hierarchy
                    if child.get('level', 0) <= item.get('level', 0):
                        errors.append(
                            f"{path}->child[{i}]: Child level must be greater than parent level"
                        )
    
    for i, item in enumerate(toc_items):
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
    """Test TOC item validation."""
    # Test valid item
    item = TOCItem("Title", "href.html", 0)
    assert item.title == "Title"
    assert item.href == "href.html"
    assert item.level == 0
    
    # Test invalid title
    with pytest.raises(ValidationError):
        TOCItem("", "href.html", 0)
    with pytest.raises(ValidationError):
        TOCItem(None, "href.html", 0)
    
    # Test invalid href
    with pytest.raises(ValidationError):
        TOCItem("Title", None, 0)
    
    # Test invalid level
    with pytest.raises(ValidationError):
        TOCItem("Title", "href.html", -1)
    with pytest.raises(ValidationError):
        TOCItem("Title", "href.html", "0")

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
    """Test error handling in different scenarios."""
    epub_file = sample_epub_files[0]
    
    # Test with invalid extraction method
    with pytest.raises(ValidationError):
        parser = EPUBTOCParser(epub_file, extraction_methods=['invalid_method'])
    
    # Test with corrupted EPUB
    with pytest.raises(StructureError):
        # Simulate corrupted EPUB by providing text file
        with open("test.epub", "w") as f:
            f.write("Not an EPUB file")
        parser = EPUBTOCParser("test.epub")
        parser.extract_toc()
    
    # Test with invalid TOC structure
    with pytest.raises(ValidationError):
        parser = EPUBTOCParser(epub_file)
        # Simulate invalid TOC item
        invalid_toc = [{'title': '', 'href': None, 'level': -1}]
        TOCItem.from_dict(invalid_toc[0])

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
    """Test TOC validation with various edge cases."""
    # Test empty TOC
    assert validate_toc_structure([]) == []
    
    # Test minimal valid TOC
    minimal_toc = [{
        'title': 'Chapter 1',
        'href': 'chapter1.html',
        'level': 0,
        'children': []
    }]
    assert validate_toc_structure(minimal_toc) == []
    
    # Test invalid TOC items
    invalid_items = [
        # Missing required fields
        {'title': 'Chapter 1'},
        {'href': 'chapter1.html'},
        {'level': 0},
        
        # Invalid field types
        {'title': '', 'href': 'chapter1.html', 'level': 0},
        {'title': 'Chapter 1', 'href': '', 'level': 0},
        {'title': 'Chapter 1', 'href': 'chapter1.html', 'level': '0'},
        
        # Invalid level values
        {'title': 'Chapter 1', 'href': 'chapter1.html', 'level': -1},
        
        # Invalid children
        {
            'title': 'Chapter 1',
            'href': 'chapter1.html',
            'level': 1,
            'children': 'not a list'
        }
    ]
    
    for item in invalid_items:
        errors = validate_toc_structure([item])
        assert len(errors) > 0, f"Expected validation errors for {item}"

def test_toc_hierarchy():
    """Test TOC hierarchy validation."""
    # Valid hierarchy
    valid_toc = [
        {
            'title': 'Chapter 1',
            'href': 'chapter1.html',
            'level': 0,
            'children': [
                {
                    'title': 'Section 1.1',
                    'href': 'section1.1.html',
                    'level': 1,
                    'children': [
                        {
                            'title': 'Subsection 1.1.1',
                            'href': 'subsection1.1.1.html',
                            'level': 2,
                            'children': []
                        }
                    ]
                }
            ]
        }
    ]
    assert validate_toc_structure(valid_toc) == []
    
    # Invalid hierarchy (child level <= parent level)
    invalid_toc = [
        {
            'title': 'Chapter 1',
            'href': 'chapter1.html',
            'level': 1,
            'children': [
                {
                    'title': 'Section 1.1',
                    'href': 'section1.1.html',
                    'level': 1,  # Same level as parent
                    'children': []
                }
            ]
        }
    ]
    errors = validate_toc_structure(invalid_toc)
    assert len(errors) > 0, "Expected hierarchy validation errors" 