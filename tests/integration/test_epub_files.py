"""Integration tests for EPUB file handling."""

import pytest
from pathlib import Path
from epub_toc import (
    EPUBTOCParser,
    TOCItem,
    ValidationError,
    ExtractionError
)
import json
import os
import shutil

# Fixture for test EPUB files directory
@pytest.fixture
def epub_samples_dir():
    """Return path to directory with test EPUB files."""
    return Path(__file__).parent.parent / "data" / "epub_samples"

@pytest.fixture
def test_output_dir():
    """Return path to epub_toc_json directory."""
    output_dir = Path(__file__).parent.parent / "data" / "epub_toc_json"
    output_dir.mkdir(exist_ok=True)
    return output_dir

def validate_toc_structure(data, filename=""):
    """Validate TOC structure against schema.
    
    Args:
        data: Dictionary containing TOC data
        filename: Optional filename for error messages
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Validate root structure
    if not isinstance(data, dict):
        errors.append(f"Root should be a dictionary, got {type(data)}")
        return errors
        
    # Check required root keys
    for key in ['metadata', 'toc']:
        if key not in data:
            errors.append(f"Missing required key: {key}")
            
    # Validate metadata
    if 'metadata' in data:
        metadata = data['metadata']
        if not isinstance(metadata, dict):
            errors.append("Metadata should be a dictionary")
        else:
            # Check required metadata fields
            for field in ['title', 'authors', 'file_name']:
                if field not in metadata:
                    errors.append(f"Metadata missing required field: {field}")
            
            # Validate field types
            if 'authors' in metadata and not isinstance(metadata['authors'], list):
                errors.append("Metadata authors should be a list")
                
    # Validate TOC
    if 'toc' in data:
        if not isinstance(data['toc'], list):
            errors.append(f"TOC should be a list, got {type(data['toc'])}")
        else:
            for i, item in enumerate(data['toc']):
                if not isinstance(item, dict):
                    errors.append(f"TOC item {i} should be a dictionary")
                    continue
                    
                # Check required fields
                for field in ['title', 'href', 'level']:
                    if field not in item:
                        errors.append(f"TOC item {i} missing required field: {field}")
                
                # Validate field types
                if 'title' in item and not isinstance(item['title'], (str, type(None))):
                    errors.append(f"TOC item {i} title should be string or None")
                if 'href' in item and not isinstance(item['href'], (str, type(None))):
                    errors.append(f"TOC item {i} href should be string or None")
                if 'level' in item:
                    if not isinstance(item['level'], (int, type(None))):
                        errors.append(f"TOC item {i} level should be integer or None")
                    elif isinstance(item['level'], int) and item['level'] < 0:
                        errors.append(f"TOC item {i} level should be non-negative")
                
                # Validate children if present
                if 'children' in item:
                    if not isinstance(item['children'], list):
                        errors.append(f"TOC item {i} children should be a list")
                    else:
                        for j, child in enumerate(item['children']):
                            if not isinstance(child, dict):
                                errors.append(f"TOC item {i} child {j} should be a dictionary")
                                continue
                            
                            # Check required fields for children
                            for field in ['title', 'href', 'level']:
                                if field not in child:
                                    errors.append(f"TOC item {i} child {j} missing required field: {field}")
                            
                            # Validate field types for children
                            if 'title' in child and not isinstance(child['title'], (str, type(None))):
                                errors.append(f"TOC item {i} child {j} title should be string or None")
                            if 'href' in child and not isinstance(child['href'], (str, type(None))):
                                errors.append(f"TOC item {i} child {j} href should be string or None")
                            if 'level' in child:
                                if not isinstance(child['level'], (int, type(None))):
                                    errors.append(f"TOC item {i} child {j} level should be integer or None")
                                elif isinstance(child['level'], int) and child['level'] < 0:
                                    errors.append(f"TOC item {i} child {j} level should be non-negative")
    
    return errors

def test_epub_file_not_found():
    """Test behavior with non-existent EPUB file."""
    with pytest.raises(ValidationError):
        EPUBTOCParser("nonexistent_book.epub")

@pytest.mark.skipif(
    not (Path(__file__).parent.parent / "data" / "epub_samples").exists(),
    reason="Test EPUB files not available"
)
def test_sample_epub_extraction(epub_samples_dir, test_output_dir):
    """Test TOC extraction from sample EPUB files."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    failed_files = []
    for epub_file in epub_files:
        try:
            parser = EPUBTOCParser(epub_file)
            toc = parser.extract_toc()
            
            # Basic validation of extracted TOC
            assert isinstance(toc, list), f"TOC from {epub_file.name} should be a list"
            assert len(toc) > 0, f"TOC from {epub_file.name} should not be empty"
            
            # Validate TOC structure
            for item in toc:
                assert isinstance(item, dict), f"TOC item from {epub_file.name} should be a dictionary"
                assert "title" in item, f"TOC item from {epub_file.name} should have title"
                assert "href" in item, f"TOC item from {epub_file.name} should have href"
                assert "level" in item, f"TOC item from {epub_file.name} should have level"
                
                # Additional validations
                assert item["title"].strip(), f"Empty title in TOC item from {epub_file.name}"
                assert item["href"].strip(), f"Empty href in TOC item from {epub_file.name}"
                assert isinstance(item["level"], int), f"Level in {epub_file.name} should be integer"
                assert item["level"] >= 0, f"Level in {epub_file.name} should be non-negative"
                
                # Children field is optional but must be a list if present
                if "children" in item:
                    assert isinstance(item["children"], list), f"children in {epub_file.name} should be a list"
                
        except Exception as e:
            failed_files.append((epub_file.name, str(e)))
    
    if failed_files:
        print("\nFailed files in test_sample_epub_extraction:")
        for name, error in failed_files:
            print(f"- {name}:")
            print(f"  {error}")
        pytest.fail(f"Test failed for {len(failed_files)} files")

@pytest.mark.skipif(
    not (Path(__file__).parent.parent / "data" / "epub_samples").exists(),
    reason="Test EPUB files not available"
)
def test_json_export(epub_samples_dir, test_output_dir):
    """Test JSON export functionality with real EPUB files."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    failed_files = []
    for epub_file in epub_files:
        try:
            parser = EPUBTOCParser(epub_file)
            
            # Extract TOC first
            parser.extract_toc()
            
            # Save to JSON
            output_file = test_output_dir / f"{epub_file.stem}_toc.json"
            parser.save_toc_to_json(output_file)
            
            # Verify file exists and not empty
            assert output_file.exists(), f"JSON file for {epub_file.name} should be created"
            assert output_file.stat().st_size > 0, f"JSON file for {epub_file.name} should not be empty"
            
            # Validate JSON structure
            with open(output_file) as f:
                data = json.load(f)
            
            # Validate root structure
            assert isinstance(data, dict), f"Root should be a dictionary for {epub_file.name}"
            assert "metadata" in data, f"Missing metadata key in {epub_file.name}"
            assert "toc" in data, f"Missing toc key in {epub_file.name}"
            
            # Validate metadata
            assert isinstance(data["metadata"], dict), f"Metadata should be a dictionary in {epub_file.name}"
            
            # Required metadata fields
            required_metadata = ["title", "authors", "file_name"]  # Made file_size optional
            for field in required_metadata:
                assert field in data["metadata"], f"Missing required metadata field '{field}' in {epub_file.name}"
            
            # Type checks for metadata
            assert isinstance(data["metadata"]["title"], (str, type(None))), f"Title should be string or None in {epub_file.name}"
            assert isinstance(data["metadata"]["authors"], (list, type(None))), f"Authors should be list or None in {epub_file.name}"
            assert isinstance(data["metadata"]["file_name"], (str, type(None))), f"File name should be string or None in {epub_file.name}"
            if "file_size" in data["metadata"]:
                assert isinstance(data["metadata"]["file_size"], (int, type(None))), f"File size should be integer or None in {epub_file.name}"
            
            # Optional metadata fields should have correct types if present
            if "publisher" in data["metadata"]:
                assert isinstance(data["metadata"]["publisher"], (str, type(None))), f"Publisher should be string or None in {epub_file.name}"
            if "publication_date" in data["metadata"]:
                assert isinstance(data["metadata"]["publication_date"], (str, type(None))), f"Publication date should be string or None in {epub_file.name}"
            if "language" in data["metadata"]:
                assert isinstance(data["metadata"]["language"], (str, type(None))), f"Language should be string or None in {epub_file.name}"
            if "description" in data["metadata"]:
                assert isinstance(data["metadata"]["description"], (str, type(None))), f"Description should be string or None in {epub_file.name}"
            
            # Validate TOC
            assert isinstance(data["toc"], list), f"TOC should be a list in {epub_file.name}"
            for item in data["toc"]:
                assert isinstance(item, dict), f"TOC item should be a dictionary in {epub_file.name}"
                assert "title" in item, f"TOC item missing title in {epub_file.name}"
                assert "href" in item, f"TOC item missing href in {epub_file.name}"
                assert "level" in item, f"TOC item missing level in {epub_file.name}"
                
                # Validate field types
                assert isinstance(item["title"], (str, type(None))), f"Title should be string or None in {epub_file.name}"
                assert isinstance(item["href"], (str, type(None))), f"Href should be string or None in {epub_file.name}"
                assert isinstance(item["level"], (int, type(None))), f"Level should be integer or None in {epub_file.name}"
                if isinstance(item["level"], int):
                    assert item["level"] >= 0, f"Level should be non-negative in {epub_file.name}"
                
                # Children field is optional but must be a list if present
                if "children" in item:
                    assert isinstance(item["children"], list), f"Children should be a list in {epub_file.name}"
                    # Recursively validate children
                    def validate_children(children):
                        for child in children:
                            assert isinstance(child, dict), f"Child TOC item should be a dictionary in {epub_file.name}"
                            assert "title" in child, f"Child TOC item missing title in {epub_file.name}"
                            assert "href" in child, f"Child TOC item missing href in {epub_file.name}"
                            assert "level" in child, f"Child TOC item missing level in {epub_file.name}"
                            assert isinstance(child["title"], (str, type(None))), f"Child title should be string or None in {epub_file.name}"
                            assert isinstance(child["href"], (str, type(None))), f"Child href should be string or None in {epub_file.name}"
                            assert isinstance(child["level"], (int, type(None))), f"Child level should be integer or None in {epub_file.name}"
                            if isinstance(child["level"], int):
                                assert child["level"] >= 0, f"Child level should be non-negative in {epub_file.name}"
                            if "children" in child:
                                assert isinstance(child["children"], list), f"Child's children should be a list in {epub_file.name}"
                                validate_children(child["children"])
                    
                    validate_children(item["children"])
            
        except Exception as e:
            failed_files.append((epub_file.name, str(e)))
    
    if failed_files:
        print("\nFailed files in test_json_export:")
        for name, error in failed_files:
            print(f"- {name}:")
            print(f"  {error}")
        pytest.fail(f"Test failed for {len(failed_files)} files")

def test_metadata_extraction(epub_samples_dir):
    """Test metadata extraction from EPUB files."""
    epub_files = [f for f in epub_samples_dir.glob("*.epub") if f.is_file()]
    if not epub_files:
        pytest.skip("No EPUB files found in test directory")
    
    for epub_file in epub_files:
        parser = EPUBTOCParser(epub_file)
        metadata = parser.extract_metadata()
        
        # Basic validation of metadata
        assert isinstance(metadata, dict), f"Metadata from {epub_file.name} should be a dictionary"
        
        # Check required fields are of correct type if present
        if "title" in metadata:
            assert isinstance(metadata["title"], str)
        if "authors" in metadata:
            assert isinstance(metadata["authors"], list)
        if "file_size" in metadata:
            assert isinstance(metadata["file_size"], (int, type(None)))
        if "file_name" in metadata:
            assert isinstance(metadata["file_name"], str)
            assert metadata["file_name"] == epub_file.name 