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
    """Represents a Table of Contents item."""
    
    def __init__(self, title: str, href: str, level: int = 0, description: str = None):
        """Initialize TOC item with validation.
        
        Args:
            title: Title of the TOC item
            href: Link to the content
            level: Nesting level (0 for top level)
            description: Optional description
            
        Raises:
            ValidationError: If title or href is empty
        """
        if not title or not title.strip():
            raise ValidationError("TOC item must have a non-empty title")
        if not href or not href.strip():
            raise ValidationError("TOC item must have a non-empty href")
            
        self.title = title.strip()
        self.href = href.strip()
        self.level = level
        self.description = description.strip() if description else None
        self.children = []

    def add_child(self, child: 'TOCItem') -> None:
        """Add a child TOC item."""
        self.children.append(child)

    def to_dict(self) -> Dict:
        """Convert TOC item to dictionary."""
        result = {
            'title': self.title,
            'href': self.href,
            'level': self.level,
            'children': [child.to_dict() for child in self.children]
        }
        if self.description:
            result['description'] = self.description
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'TOCItem':
        """Create TOC item from dictionary with simplified validation."""
        if not isinstance(data, dict):
            raise ValidationError("TOC item must be a dictionary")
            
        if 'title' not in data or 'href' not in data:
            raise ValidationError("TOC item must have 'title' and 'href' fields")
            
        item = cls(
            title=data['title'],
            href=data['href'],
            level=data.get('level', 0),
            description=data.get('description')
        )
        
        for child_data in data.get('children', []):
            child = cls.from_dict(child_data)
            item.add_child(child)
            
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
        """Extract table of contents using all available methods.
        
        Returns:
            List of dictionaries representing TOC items
            
        Raises:
            ExtractionError: If all extraction methods fail
        """
        errors = {}
        
        # Try each extraction method in order
        for method_name, method_attr in self.EXTRACTION_METHODS:
            try:
                logger.info(f"Trying extraction method: {method_name}")
                method = getattr(self, method_attr)
                result = method()
                
                if result and isinstance(result, list) and result:
                    # Validate TOC structure
                    self._validate_toc_structure(result)
                    
                    # Convert TOCItems to dictionaries
                    toc_dicts = []
                    for item in result:
                        if isinstance(item, TOCItem):
                            toc_dicts.append(item.to_dict())
                        else:
                            logger.warning(f"Invalid TOC item type: {type(item)}")
                            continue
                    
                    if toc_dicts:
                        logger.info(f"Successfully extracted TOC using {method_name}")
                        self.toc = toc_dicts  # Store dictionaries instead of TOCItem objects
                        return toc_dicts
                    
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
            raise ValidationError(f"TOC must be a list, got {type(toc_items)}")
            
        if not toc_items:
            logger.warning("TOC is empty")
            return
            
        def validate_item(item: TOCItem, path: str = "root") -> None:
            if not isinstance(item, TOCItem):
                raise ValidationError(
                    f"{path}: Item must be a TOCItem instance, got {type(item)}"
                )
            
            # Validate required fields
            if not item.title or not isinstance(item.title, str):
                raise ValidationError(f"{path}: Invalid title: {item.title}")
                
            if not item.href or not isinstance(item.href, str):
                raise ValidationError(f"{path}: Invalid href: {item.href}")
                
            if not isinstance(item.level, int) or item.level < 0:
                raise ValidationError(f"{path}: Invalid level: {item.level}")
            
            # Validate children
            if not isinstance(item.children, list):
                raise ValidationError(f"{path}: Children must be a list")
                
            for i, child in enumerate(item.children):
                child_path = f"{path}->child[{i}]"
                validate_item(child, child_path)
                
                # Validate level hierarchy
                if child.level <= item.level:
                    logger.warning(
                        f"{child_path}: Child level ({child.level}) not greater "
                        f"than parent level ({item.level})"
                    )
        
        # Validate each top-level item
        for i, item in enumerate(toc_items):
            validate_item(item, f"item[{i}]")
    
    def _extract_from_epub_meta(self) -> Optional[List[TOCItem]]:
        """Extract TOC using epub_meta library."""
        try:
            logger.info("Attempting extraction using epub_meta")
            metadata = get_epub_metadata(str(self.epub_path))
            
            if not metadata:
                logger.warning("No metadata returned from epub_meta")
                return None
                
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
                try:
                    level = item.get('level', 0)
                    title = item.get('title', '').strip()
                    href = item.get('src', '').strip()
                    
                    if not title:
                        logger.warning(f"Skipping TOC item with empty title: {item}")
                        continue
                        
                    if not href:
                        logger.warning(f"Skipping TOC item with empty href: {item}")
                        continue
                    
                    logger.debug(f"Processing TOC item: {title} (level {level})")
                    
                    while level <= stack[-1][1]:
                        stack.pop()
                    
                    toc_item = TOCItem(title=title, href=href, level=level)
                    stack[-1][0].append(toc_item)
                    stack.append((toc_item.children, level))
                    
                except Exception as e:
                    logger.warning(f"Failed to process TOC item {item}: {e}")
                    continue
            
            if not result:
                logger.warning("No valid TOC items were extracted")
                return None
                
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
                    
                    # Create TOC item first
                    item = TOCItem(
                        title=text.text,
                        href=href,
                        level=level
                    )
                    
                    # Then process children and add them
                    for child in nav_point.findall('ncx:navPoint', ns):
                        child_item = process_nav_point(child, level + 1)
                        if child_item:
                            item.children.append(child_item)
                    
                    return item
                
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
    
    def extract_metadata(self) -> dict:
        """Extract metadata from EPUB file."""
        try:
            metadata = get_epub_metadata(str(self.epub_path))
            return {
                "title": metadata.get('title'),
                "authors": metadata.get('authors', []),
                "publisher": metadata.get('publisher'),
                "publication_date": metadata.get('publication_date'),
                "language": metadata.get('language'),
                "description": metadata.get('description'),
                "cover_image_path": metadata.get('cover_image_path'),
                "isbn": metadata.get('isbn'),
                "rights": metadata.get('rights'),
                "series": metadata.get('series'),
                "series_index": metadata.get('series_index'),
                "identifiers": metadata.get('identifiers', {}),
                "subjects": metadata.get('subjects', []),
                "file_size": Path(self.epub_path).stat().st_size if self.epub_path else None,
                "file_name": Path(self.epub_path).name if self.epub_path else None
            }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {}
    
    def save_toc_to_json(self, output_path: Union[str, Path], metadata: Dict = None) -> None:
        """Save TOC to JSON file with enhanced formatting and metadata.
        
        Args:
            output_path: Path where to save the JSON file
            metadata: Optional metadata to include in the output
            
        Raises:
            OutputError: If saving fails
            ValidationError: If TOC not extracted yet
        """
        if not self.toc:
            raise ValidationError("TOC not extracted yet")
            
        output_path = Path(output_path)
        metadata = metadata or self.extract_metadata()
        
        # Convert TOC items to dictionaries if they are TOCItem objects
        toc_data = []
        for item in self.toc:
            if isinstance(item, TOCItem):
                toc_data.append(item.to_dict())
            elif isinstance(item, dict):
                toc_data.append(item)
            else:
                logger.warning(f"Unexpected TOC item type: {type(item)}")
                continue

        # Prepare output data with simplified structure
        data = {
            "metadata": {
                "title": metadata.get("title"),
                "authors": metadata.get("authors", []),
                "file_name": str(self.epub_path.name),
                "file_size": self.epub_path.stat().st_size if self.epub_path.exists() else None,
                "publisher": metadata.get("publisher"),
                "language": metadata.get("language"),
            },
            "toc": toc_data
        }
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)
        
        logger.info(f"Saved TOC with metadata to: {output_path}")
    
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