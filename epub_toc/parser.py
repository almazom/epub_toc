"""EPUB TOC Parser implementation.

This module provides the core functionality for parsing and extracting
table of contents from EPUB files. It includes classes for representing
TOC items and the main parser implementation.

Examples:
    Basic parsing:
    >>> parser = EPUBTOCParser('book.epub')
    >>> toc = parser.extract_toc()
    
    Working with TOC items:
    >>> item = TOCItem('Chapter 1', 'chapter1.html', level=0)
    >>> item.add_child(TOCItem('Section 1.1', 'chapter1.html#section1', level=1))
"""

import json
import logging
import zipfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple

from bs4 import BeautifulSoup
from epub_meta import get_epub_metadata
from lxml import etree
from ebooklib import epub
from tika import parser as tika_parser

from .exceptions import (
    ValidationError,
    ExtractionError,
    StructureError,
    ParsingError,
    ConversionError
)

logger = logging.getLogger(__name__)

class TOCItem:
    """Represents a single item in the table of contents.
    
    This class implements a node in the hierarchical table of contents structure.
    Each item has a title, link to content (href), nesting level, and optional
    child items.

    Attributes:
        title (str): The display text for this TOC item
        href (str): The link to the content this item points to
        level (int): The nesting level in the TOC hierarchy (0-based)
        children (List[TOCItem]): Child items in the TOC hierarchy
        description (Optional[str]): Optional description of the item
        REQUIRED_FIELDS (set): Class attribute defining required fields for validation

    Examples:
        Create a simple TOC item:
        >>> item = TOCItem('Chapter 1', 'chapter1.html')
        >>> print(item.title)
        'Chapter 1'

        Create nested structure:
        >>> parent = TOCItem('Part 1', 'part1.html', level=0)
        >>> child = TOCItem('Chapter 1', 'chapter1.html', level=1)
        >>> parent.children.append(child)
        >>> print(len(parent.children))
        1
    
    Notes:
        - Level 0 represents top-level items
        - All items must have a title and href
        - Children should have a higher level than their parent
    """
    
    REQUIRED_FIELDS = {'title', 'href', 'level'}
    
    def __init__(self, title: str, href: str, level: int = 0, children: List['TOCItem'] = None):
        """Initialize TOC item.
        
        Args:
            title: Display text for this TOC item
            href: Link to the content this item points to
            level: Nesting level in the TOC hierarchy (0-based)
            children: Optional list of child items
        
        Raises:
            ValidationError: If title is empty or not a string,
                           if href is not a string, or if level is negative
        """
        self.validate_fields(title, href, level)
        self.title = title
        self.href = href
        self.level = level
        self.children = children or []
        self.description = None
    
    @classmethod
    def validate_fields(cls, title: str, href: str, level: int) -> None:
        """Validate TOC item fields.
        
        Performs validation of the essential fields for a TOC item.
        
        Args:
            title: Item title to validate
            href: Content link to validate
            level: Nesting level to validate
            
        Raises:
            ValidationError: If any field fails validation:
                - title is empty or not a string
                - href is not a string
                - level is negative or not an integer
        """
        if not title or not isinstance(title, str):
            raise ValidationError("Title must be a non-empty string")
        if not isinstance(href, str):
            raise ValidationError("Href must be a string")
        if not isinstance(level, int) or level < 0:
            raise ValidationError("Level must be a non-negative integer")
    
    def to_dict(self) -> Dict:
        """Convert TOC item to dictionary representation.
        
        Creates a dictionary containing all item data, including children
        recursively converted to dictionaries.
        
        Returns:
            Dict containing the following keys:
                - title: Item title
                - href: Content link
                - level: Nesting level
                - children: List of child items as dictionaries
                - description: Optional description if set
        """
        result = {
            'title': self.title,
            'href': self.href,
            'level': self.level,
            'children': [child.to_dict() for child in self.children]
        }
        if self.description is not None:
            result['description'] = self.description
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TOCItem':
        """Create TOC item from dictionary data.
        
        Factory method to create a TOC item from a dictionary representation.
        
        Args:
            data: Dictionary containing TOC item data with required fields:
                - title: Item title
                - href: Content link
                - level: Nesting level
                Optional fields:
                - children: List of child items as dictionaries
                - description: Optional item description
            
        Returns:
            New TOCItem instance populated with the dictionary data
            
        Raises:
            ValidationError: If any required fields are missing or invalid
        """
        missing_fields = cls.REQUIRED_FIELDS - set(data.keys())
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
        
        children = [cls.from_dict(child) for child in data.get('children', [])]
        item = cls(
            title=data['title'],
            href=data['href'],
            level=data['level'],
            children=children
        )
        if 'description' in data:
            item.description = data['description']
        return item

class EPUBTOCParser:
    """Parser for extracting table of contents from EPUB files.
    
    This class provides multiple methods for extracting the table of contents
    from EPUB files. It automatically tries different extraction methods in
    order of preference until one succeeds.

    Attributes:
        epub_path (Path): Path to the EPUB file being parsed
        toc (Optional[List[TOCItem]]): Extracted table of contents, None if not yet extracted
        active_methods (List[Tuple[str, str]]): List of (method_name, method_attr) pairs to try
        EXTRACTION_METHODS (List[Tuple[str, str]]): Available extraction methods

    Examples:
        Basic usage:
        >>> parser = EPUBTOCParser('book.epub')
        >>> toc = parser.extract_toc()
        >>> print(toc[0]['title'])
        'Chapter 1'

        Using specific methods:
        >>> parser = EPUBTOCParser('book.epub', extraction_methods=['ncx', 'opf'])
        >>> toc = parser.extract_toc()

    Notes:
        - The parser validates the EPUB file structure before extraction
        - Methods are tried in order until one succeeds
        - Supports various EPUB formats and structures
    """
    
    EXTRACTION_METHODS = [
        ('epub_meta', '_extract_from_epub_meta'),
        ('ncx', '_extract_from_ncx'),
        ('opf', '_extract_from_opf'),
        ('ebooklib', '_extract_from_ebooklib'),
        ('tika', '_extract_from_tika'),
        ('calibre', '_extract_from_calibre')
    ]
    
    def __init__(self, epub_path: Union[str, Path], extraction_methods: List[str] = None):
        """Initialize parser.
        
        Args:
            epub_path: Path to EPUB file
            extraction_methods: List of method names to use, in priority order.
                              If None, all methods will be used in default order.
        
        Raises:
            ValidationError: If file doesn't exist or has wrong extension
        """
        self.epub_path = Path(epub_path)
        self.toc = None
        
        # Set up extraction methods
        if extraction_methods is not None:
            if not extraction_methods:
                raise ValidationError("No extraction methods specified")
            self.active_methods = [
                (name, method) for name, method in self.EXTRACTION_METHODS
                if name in extraction_methods
            ]
            if not self.active_methods:
                raise ValidationError(f"No valid extraction methods found in: {extraction_methods}")
        else:
            self.active_methods = self.EXTRACTION_METHODS
            
        self._validate_file()
        logger.info(f"Initialized parser for {self.epub_path} with methods: {[m[0] for m in self.active_methods]}")
    
    def _validate_file(self):
        """Validate EPUB file existence and format.
        
        Raises:
            ValidationError: If file validation fails
            StructureError: If file is not a valid EPUB
        """
        if not self.epub_path.exists():
            raise ValidationError("File not found")
        if self.epub_path.suffix.lower() != '.epub':
            raise ValidationError("Not an EPUB file")
        if self.epub_path.is_dir():
            raise ValidationError("Path points to a directory")
            
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as epub:
                # Check for required EPUB files
                required_files = ['META-INF/container.xml']
                missing_files = [f for f in required_files if f not in epub.namelist()]
                if missing_files:
                    raise StructureError(f"Missing required files: {missing_files}")
                
                # Validate container.xml
                container = epub.read('META-INF/container.xml')
                tree = etree.fromstring(container)
                rootfiles = tree.findall('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile')
                if not rootfiles:
                    raise StructureError("No rootfiles found in container.xml")
                
        except zipfile.BadZipFile:
            raise StructureError("File is not a valid ZIP archive")
        except Exception as e:
            raise StructureError(f"Invalid EPUB structure: {str(e)}")
            
        logger.debug("File validation passed")
    
    def extract_toc(self) -> List[Dict]:
        """Extract table of contents using configured methods.
        
        Returns:
            List of TOC items as dictionaries
        
        Raises:
            ExtractionError: If no extraction method succeeds
        """
        errors = {}
        
        for method_name, method_attr in self.active_methods:
            try:
                logger.info(f"Trying extraction method: {method_name}")
                method = getattr(self, method_attr)
                result = method()
                
                if result:
                    # Validate TOC structure
                    self._validate_toc_structure(result)
                    
                    logger.info(f"Successfully extracted TOC using {method_name}")
                    self.toc = result
                    return [item.to_dict() for item in result]
                    
            except Exception as e:
                logger.warning(f"Method {method_name} failed: {str(e)}")
                errors[method_name] = str(e)
        
        # If we get here, no method succeeded
        error_details = "\n".join(f"- {name}: {error}" for name, error in errors.items())
        raise ExtractionError(f"All extraction methods failed:\n{error_details}")
    
    def _validate_toc_structure(self, toc_items: List[TOCItem]) -> None:
        """Validate TOC structure.
        
        Args:
            toc_items: List of TOC items to validate
            
        Raises:
            ValidationError: If structure is invalid
        """
        if not isinstance(toc_items, list):
            raise ValidationError("TOC must be a list")
        if not toc_items:
            raise ValidationError("TOC cannot be empty")
            
        def validate_item(item: TOCItem, path: str = "root") -> None:
            if not isinstance(item, TOCItem):
                raise ValidationError(f"{path}: Item must be a TOCItem instance")
            
            # Validate children
            for i, child in enumerate(item.children):
                validate_item(child, f"{path}->child[{i}]")
                
                # Validate level hierarchy
                if child.level <= item.level:
                    raise ValidationError(
                        f"{path}->child[{i}]: Child level must be greater than parent level"
                    )
        
        for i, item in enumerate(toc_items):
            validate_item(item, f"item[{i}]")
    
    def _extract_from_epub_meta(self) -> Optional[List[TOCItem]]:
        """Extract TOC using epub_meta library."""
        try:
            logger.info("Attempting extraction using epub_meta")
            metadata = get_epub_metadata(str(self.epub_path))
            toc = metadata.get('toc')
            if not toc:
                logger.warning("No TOC found in epub_meta metadata")
                return None
            
            logger.debug(f"Found {len(toc)} TOC items in epub_meta")
            
            # Convert to our format
            result = []
            current_level = 0
            stack = [(result, -1)]
            
            for item in toc:
                level = item.get('level', 0)
                title = item.get('title', '')
                href = item.get('src', '')
                
                logger.debug(f"Processing TOC item: {title} (level {level})")
                
                while level <= stack[-1][1]:
                    stack.pop()
                
                toc_item = TOCItem(title=title, href=href, level=level)
                stack[-1][0].append(toc_item)
                stack.append((toc_item.children, level))
            
            logger.info(f"Successfully extracted {len(result)} top-level items using epub_meta")
            return result
        except Exception as e:
            logger.warning(f"Failed to extract TOC using epub_meta: {e}")
            return None
    
    def _extract_from_ncx(self) -> Optional[List[TOCItem]]:
        """Extract TOC from NCX file."""
        try:
            logger.info("Attempting extraction from NCX")
            with zipfile.ZipFile(self.epub_path, 'r') as epub:
                # Find NCX file
                ncx_files = [f for f in epub.namelist() if f.endswith('.ncx')]
                if not ncx_files:
                    logger.warning("No NCX file found in EPUB")
                    return None
                
                ncx_path = ncx_files[0]
                logger.debug(f"Found NCX file: {ncx_path}")
                
                # Parse NCX
                ncx_content = epub.read(ncx_path)
                tree = etree.fromstring(ncx_content)
                
                # Define namespace
                ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
                
                def process_nav_point(nav_point, level=0) -> Optional[TOCItem]:
                    """Process navigation point recursively."""
                    # Get title
                    nav_label = nav_point.find('ncx:navLabel', ns)
                    text = nav_label.find('ncx:text', ns) if nav_label is not None else None
                    if text is None or not text.text:
                        logger.debug(f"Skipping nav point at level {level}: no title")
                        return None
                    
                    # Get content
                    content = nav_point.find('ncx:content', ns)
                    href = content.get('src', '') if content is not None else ''
                    
                    # Process children
                    children = []
                    for child in nav_point.findall('ncx:navPoint', ns):
                        child_item = process_nav_point(child, level + 1)
                        if child_item:
                            children.append(child_item)
                    
                    return TOCItem(
                        title=text.text,
                        href=href,
                        level=level,
                        children=children
                    )
                
                # Process all nav points
                result = []
                nav_map = tree.find('ncx:navMap', ns)
                if nav_map is not None:
                    for nav_point in nav_map.findall('ncx:navPoint', ns):
                        item = process_nav_point(nav_point)
                        if item:
                            result.append(item)
                
                if not result:
                    logger.warning("No valid navigation points found in NCX")
                    return None
                
                logger.info(f"Successfully extracted {len(result)} top-level items from NCX")
                return result
                
        except Exception as e:
            logger.warning(f"Failed to extract TOC from NCX: {e}")
            return None
    
    def _extract_from_opf(self) -> Optional[List[TOCItem]]:
        """Extract TOC from OPF file."""
        try:
            logger.info("Attempting extraction from OPF")
            with zipfile.ZipFile(self.epub_path, 'r') as epub:
                # Find OPF file
                opf_files = [f for f in epub.namelist() if f.endswith('.opf')]
                if not opf_files:
                    logger.warning("No OPF file found in EPUB")
                    return None
                
                opf_path = opf_files[0]
                logger.debug(f"Found OPF file: {opf_path}")
                
                # Parse OPF
                opf_content = epub.read(opf_path)
                tree = etree.fromstring(opf_content)
                
                # Find spine and manifest
                spine = tree.find('.//{http://www.idpf.org/2007/opf}spine')
                manifest = tree.find('.//{http://www.idpf.org/2007/opf}manifest')
                
                if spine is None or manifest is None:
                    logger.warning("No spine or manifest found in OPF")
                    return None
                
                # Create id -> href mapping
                id_to_href = {}
                for item in manifest.findall('.//{http://www.idpf.org/2007/opf}item'):
                    item_id = item.get('id')
                    href = item.get('href')
                    if item_id and href:
                        id_to_href[item_id] = href
                
                # Extract structure from spine
                result = []
                for i, itemref in enumerate(spine.findall('.//{http://www.idpf.org/2007/opf}itemref')):
                    idref = itemref.get('idref')
                    if idref in id_to_href:
                        result.append(TOCItem(
                            title=f'Chapter {i+1}',
                            href=id_to_href[idref],
                            level=0
                        ))
                
                if not result:
                    logger.warning("No valid items found in OPF spine")
                    return None
                
                logger.info(f"Successfully extracted {len(result)} items from OPF")
                return result
                
        except Exception as e:
            logger.warning(f"Failed to extract TOC from OPF: {e}")
            return None
    
    def _extract_from_ebooklib(self) -> Optional[List[TOCItem]]:
        """Extract TOC using ebooklib."""
        try:
            logger.info("Attempting extraction using ebooklib")
            book = epub.read_epub(str(self.epub_path))
            toc = book.toc
            
            if not toc:
                logger.warning("No TOC found in ebooklib")
                return None
            
            def process_toc_item(item, level=0) -> TOCItem:
                if isinstance(item, tuple):
                    # Handle tuple format (section, items)
                    section, children = item
                    title = section.title
                    href = section.href or ''
                else:
                    # Handle single item
                    title = item.title
                    href = item.href or ''
                    children = []
                
                toc_item = TOCItem(title=title, href=href, level=level)
                
                # Process children recursively
                if isinstance(item, tuple):
                    toc_item.children = [process_toc_item(child, level+1) 
                                       for child in children]
                
                return toc_item
                
            result = [process_toc_item(item) for item in toc]
            
            if not result:
                logger.warning("No valid items found in ebooklib TOC")
                return None
            
            logger.info(f"Successfully extracted {len(result)} top-level items using ebooklib")
            return result
            
        except Exception as e:
            logger.warning(f"Failed to extract TOC using ebooklib: {e}")
            return None
    
    def _extract_from_tika(self) -> Optional[List[TOCItem]]:
        """Extract TOC using Apache Tika."""
        try:
            logger.info("Attempting extraction using Tika")
            parsed = tika_parser.from_file(str(self.epub_path))
            metadata = parsed.get('metadata', {})
            
            if not metadata or 'toc' not in metadata:
                logger.warning("No TOC found in Tika metadata")
                return None
            
            toc_data = metadata['toc']
            result = []
            
            # Process Tika's TOC format
            def process_tika_item(item, level=0) -> TOCItem:
                return TOCItem(
                    title=item.get('title', ''),
                    href=item.get('href', ''),
                    level=level,
                    children=[process_tika_item(child, level+1) 
                             for child in item.get('children', [])]
                )
            
            result = [process_tika_item(item) for item in toc_data]
            
            if not result:
                logger.warning("No valid items found in Tika TOC")
                return None
            
            logger.info(f"Successfully extracted {len(result)} top-level items using Tika")
            return result
            
        except Exception as e:
            logger.warning(f"Failed to extract TOC using Tika: {e}")
            return None
    
    def _extract_from_calibre(self) -> Optional[List[TOCItem]]:
        """Extract TOC using Calibre's ebook-meta tool."""
        try:
            logger.info("Attempting extraction using Calibre")
            result = subprocess.run(
                ['ebook-meta', str(self.epub_path), '--get-toc'],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                logger.warning("No TOC found using Calibre")
                return None
            
            # Parse Calibre's output format
            lines = result.stdout.strip().split('\n')
            result = []
            stack = [(result, -1)]
            
            for line in lines:
                if not line.strip():
                    continue
                    
                # Calculate indentation level
                level = len(line) - len(line.lstrip())
                line = line.strip()
                
                # Extract title and href
                parts = line.split(' -> ')
                title = parts[0].strip()
                href = parts[1].strip() if len(parts) > 1 else ''
                
                # Create TOC item
                while level <= stack[-1][1]:
                    stack.pop()
                
                toc_item = TOCItem(title=title, href=href, level=level)
                stack[-1][0].append(toc_item)
                stack.append((toc_item.children, level))
            
            if not result:
                logger.warning("No valid items found in Calibre TOC")
                return None
            
            logger.info(f"Successfully extracted {len(result)} top-level items using Calibre")
            return result
            
        except Exception as e:
            logger.warning(f"Failed to extract TOC using Calibre: {e}")
            return None
    
    def save_toc_to_json(self, output_path: Union[str, Path]):
        """Save extracted TOC to JSON file.
        
        Args:
            output_path: Path to save JSON file
        
        Raises:
            ValidationError: If TOC hasn't been extracted yet
        """
        if not self.toc:
            raise ValidationError("TOC not extracted")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([item.to_dict() for item in self.toc], f, 
                     ensure_ascii=False, indent=2)
        logger.info(f"Saved TOC to {output_path}")
    
    def print_toc(self):
        """Print extracted TOC to console.
        
        Raises:
            ValidationError: If TOC hasn't been extracted yet
        """
        if not self.toc:
            raise ValidationError("TOC not extracted")
        
        def print_item(item: TOCItem, level: int = 0):
            print('  ' * level + f'- {item.title}')
            for child in item.children:
                print_item(child, level + 1)
        
        print("\nTable of Contents:")
        for item in self.toc:
            print_item(item) 