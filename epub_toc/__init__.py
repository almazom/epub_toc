"""EPUB Table of Contents Extraction Package.

This package provides tools for extracting and manipulating table of contents
from EPUB files. It supports multiple extraction methods and preserves the
hierarchical structure of the TOC.

Examples:
    Basic usage:
    >>> from epub_toc import get_toc, search_toc, get_toc_stats, compare_tocs
    >>> toc = get_toc('book.epub')  # returns JSON string
    >>> # If you need Python dict, use json.loads:
    >>> import json
    >>> toc_dict = json.loads(get_toc('book.epub'))

Notes:
    The package automatically selects the best extraction method based on
    the EPUB file structure and content.
"""

__version__ = "1.0.0"

import json
from typing import Dict, List
from .parser import EPUBTOCParser, TOCItem
from .exceptions import (
    EPUBTOCError,
    ValidationError,
    ExtractionError,
    StructureError,
    ParsingError,
    ConversionError,
    OutputError
)

def get_toc(epub_path: str) -> str:
    """
    Get table of contents from EPUB file as JSON string.
    
    Args:
        epub_path: Path to EPUB file
        
    Returns:
        JSON string containing the table of contents
    """
    toc = EPUBTOCParser(epub_path).extract_toc()
    return json.dumps(toc, indent=2, ensure_ascii=False)

def search_toc(epub_path: str, query: str, case_sensitive: bool = False) -> str:
    """
    Search for entries in TOC containing the query.
    
    Args:
        epub_path: Path to EPUB file
        query: Text to search for
        case_sensitive: Whether to perform case-sensitive search
        
    Returns:
        JSON string with list of matching TOC entries with their paths
    """
    toc = json.loads(get_toc(epub_path))
    results = []
    
    def search_in_entry(entry: Dict, path: List[str] = None):
        if path is None:
            path = []
        
        title = entry['title']
        if not case_sensitive:
            title = title.lower()
            query_lower = query.lower()
        else:
            query_lower = query
            
        if query_lower in title:
            results.append({
                'entry': entry,
                'path': ' > '.join(path + [entry['title']])
            })
            
        for child in entry.get('children', []):
            search_in_entry(child, path + [entry['title']])
    
    for entry in toc:
        search_in_entry(entry)
    
    return json.dumps(results, indent=2, ensure_ascii=False)

def get_toc_stats(epub_path: str) -> str:
    """
    Get statistics about the table of contents.
    
    Args:
        epub_path: Path to EPUB file
        
    Returns:
        JSON string with statistics:
        - total_entries: Total number of entries
        - max_depth: Maximum nesting level
        - chapters_by_level: Number of entries at each level
    """
    toc = json.loads(get_toc(epub_path))
    stats = {
        'total_entries': 0,
        'max_depth': 0,
        'chapters_by_level': {}
    }
    
    def analyze_entry(entry: Dict, current_depth: int = 0):
        stats['total_entries'] += 1
        stats['max_depth'] = max(stats['max_depth'], current_depth)
        stats['chapters_by_level'][current_depth] = stats['chapters_by_level'].get(current_depth, 0) + 1
        
        for child in entry.get('children', []):
            analyze_entry(child, current_depth + 1)
    
    for entry in toc:
        analyze_entry(entry)
    
    return json.dumps(stats, indent=2, ensure_ascii=False)

def compare_tocs(epub1_path: str, epub2_path: str) -> str:
    """
    Compare table of contents of two EPUB files.
    
    Args:
        epub1_path: Path to first EPUB file
        epub2_path: Path to second EPUB file
        
    Returns:
        JSON string with comparison results:
        - common_entries: Entries present in both TOCs
        - unique_to_first: Entries only in first TOC
        - unique_to_second: Entries only in second TOC
        - structure_differences: Structural differences
    """
    toc1 = json.loads(get_toc(epub1_path))
    toc2 = json.loads(get_toc(epub2_path))
    
    def get_titles(toc):
        titles = set()
        def collect_titles(entry):
            titles.add(entry['title'])
            for child in entry.get('children', []):
                collect_titles(child)
        for entry in toc:
            collect_titles(entry)
        return titles
    
    titles1 = get_titles(toc1)
    titles2 = get_titles(toc2)
    
    result = {
        'common_entries': list(titles1 & titles2),
        'unique_to_first': list(titles1 - titles2),
        'unique_to_second': list(titles2 - titles1),
        'structure_differences': {
            'first_total': len(titles1),
            'second_total': len(titles2),
            'common_count': len(titles1 & titles2)
        }
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

__all__ = [
    "get_toc",
    "search_toc",
    "get_toc_stats",
    "compare_tocs",
    "EPUBTOCParser",
    "TOCItem",
    "EPUBTOCError",
    "ValidationError",
    "ExtractionError",
    "StructureError",
    "ParsingError",
    "ConversionError",
    "OutputError"
] 