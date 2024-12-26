"""Unit tests for EPUB TOC Parser."""

import pytest
from pathlib import Path
from epub_toc import (
    EPUBTOCParser,
    TOCItem,
    ValidationError,
    ExtractionError
)
import json
import zipfile
import os

def create_minimal_epub(path):
    """Create a minimal valid EPUB file for testing."""
    with zipfile.ZipFile(path, 'w') as epub:
        # Add mimetype file
        epub.writestr('mimetype', 'application/epub+zip')
        
        # Add container.xml
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
        epub.writestr('META-INF/container.xml', container_xml)
        
        # Add minimal content.opf
        content_opf = '''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Test Book</dc:title>
        <dc:creator>Test Author</dc:creator>
        <dc:identifier id="uid">test-id</dc:identifier>
        <dc:language>en</dc:language>
    </metadata>
    <manifest>
        <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    </manifest>
    <spine>
        <itemref idref="nav"/>
    </spine>
</package>'''
        epub.writestr('content.opf', content_opf)

@pytest.fixture
def sample_toc_item():
    """Create a sample TOC item for testing."""
    parent = TOCItem(
        title="Test Chapter",
        href="chapter1.html",
        level=0
    )
    child = TOCItem(
        title="Test Section",
        href="chapter1.html#section1",
        level=1
    )
    parent.add_child(child)
    return parent

def test_toc_item_creation():
    """Test TOCItem creation and default values."""
    item = TOCItem(title="Test", href="test.html", level=0)
    assert item.title == "Test"
    assert item.href == "test.html"
    assert item.level == 0
    assert item.children == []
    assert item.description is None

def test_toc_item_to_dict(sample_toc_item):
    """Test TOCItem serialization to dictionary."""
    result = sample_toc_item.to_dict()
    assert result["title"] == "Test Chapter"
    assert result["href"] == "chapter1.html"
    assert result["level"] == 0
    assert len(result["children"]) == 1
    assert result["children"][0]["title"] == "Test Section"

def test_parser_initialization_with_invalid_file():
    """Test parser initialization with non-existent file."""
    with pytest.raises(ValidationError, match="File not found"):
        EPUBTOCParser("nonexistent.epub")

def test_parser_initialization_with_wrong_extension(tmp_path):
    """Test parser initialization with wrong file extension."""
    wrong_file = tmp_path / "test.txt"
    wrong_file.touch()
    with pytest.raises(ValidationError, match="Not an EPUB file"):
        EPUBTOCParser(wrong_file)

@pytest.fixture
def mock_epub_meta(mocker):
    """Mock epub_meta.get_epub_metadata function."""
    return mocker.patch("epub_toc.parser.get_epub_metadata")

def test_extract_from_epub_meta_empty(mock_epub_meta, tmp_path):
    """Test extraction when epub_meta returns no TOC."""
    epub_path = tmp_path / "test.epub"
    create_minimal_epub(epub_path)
    mock_epub_meta.return_value = {"toc": []}
    
    parser = EPUBTOCParser(epub_path)
    result = parser._extract_from_epub_meta()
    assert result is None

def test_extract_from_epub_meta_success(mock_epub_meta, tmp_path):
    """Test successful TOC extraction via epub_meta."""
    epub_path = tmp_path / "test.epub"
    create_minimal_epub(epub_path)
    mock_epub_meta.return_value = {
        "toc": [
            {"title": "Chapter 1", "src": "ch1.html", "level": 0},
            {"title": "Section 1.1", "src": "ch1.html#1", "level": 1}
        ]
    }
    
    parser = EPUBTOCParser(epub_path)
    result = parser._extract_from_epub_meta()
    assert result is not None
    assert len(result) == 1
    assert result[0].title == "Chapter 1"
    assert result[0].href == "ch1.html"
    assert len(result[0].children) == 1
    assert result[0].children[0].title == "Section 1.1"

def test_save_toc_to_json(tmp_path):
    """Test saving TOC to JSON file with simplified format."""
    # Create test file
    test_file = tmp_path / "test.epub"
    create_minimal_epub(test_file)
    
    # Initialize parser
    parser = EPUBTOCParser(test_file)
    
    # Create sample TOC
    toc = [
        TOCItem(title="Chapter 1", href="ch1.html", level=1),
        TOCItem(title="Chapter 2", href="ch2.html", level=1)
    ]
    parser.toc = toc
    
    # Save to JSON
    json_file = tmp_path / "toc.json"
    parser.save_toc_to_json(json_file)
    
    # Verify JSON content
    with open(json_file) as f:
        data = json.load(f)
    
    # Check main structure
    assert isinstance(data, dict), "Root should be a dictionary"
    assert "metadata" in data, "Should have metadata"
    assert "toc" in data, "Should have toc"
    
    # Check metadata structure
    metadata = data["metadata"]
    assert isinstance(metadata, dict)
    assert "title" in metadata
    assert "authors" in metadata
    assert "file_name" in metadata
    assert "file_size" in metadata
    assert isinstance(metadata["authors"], list)
    
    # Check TOC structure
    toc_data = data["toc"]
    assert isinstance(toc_data, list)
    assert len(toc_data) == 2
    
    # Check first item
    assert toc_data[0]["title"] == "Chapter 1"
    assert toc_data[0]["href"] == "ch1.html"
    assert toc_data[0]["level"] == 1
    assert isinstance(toc_data[0]["children"], list)
    
    # Check second item
    assert toc_data[1]["title"] == "Chapter 2"
    assert toc_data[1]["href"] == "ch2.html"
    assert toc_data[1]["level"] == 1
    assert isinstance(toc_data[1]["children"], list)

def test_print_toc_without_extraction(tmp_path):
    """Test print_toc when TOC is not extracted."""
    epub_path = tmp_path / "test.epub"
    create_minimal_epub(epub_path)
    parser = EPUBTOCParser(epub_path)
    with pytest.raises(ValidationError, match="not extracted"):
        parser.print_toc() 