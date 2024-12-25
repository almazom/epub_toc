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
    return TOCItem(
        title="Test Chapter",
        href="chapter1.html",
        level=0,
        children=[
            TOCItem(
                title="Test Section",
                href="chapter1.html#section1",
                level=1
            )
        ]
    )

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

def test_save_toc_to_json(tmp_path, sample_toc_item):
    """Test saving TOC to JSON file."""
    epub_path = tmp_path / "test.epub"
    create_minimal_epub(epub_path)
    json_path = tmp_path / "toc.json"
    
    parser = EPUBTOCParser(epub_path)
    parser.toc = [sample_toc_item]
    parser.save_toc_to_json(json_path)
    
    with open(json_path) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["title"] == "Test Chapter"
    assert data[0]["children"][0]["title"] == "Test Section"

def test_print_toc_without_extraction(tmp_path):
    """Test print_toc when TOC is not extracted."""
    epub_path = tmp_path / "test.epub"
    create_minimal_epub(epub_path)
    parser = EPUBTOCParser(epub_path)
    with pytest.raises(ValidationError, match="not extracted"):
        parser.print_toc() 