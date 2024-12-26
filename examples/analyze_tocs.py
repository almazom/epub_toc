#!/usr/bin/env python3
"""
Example of using advanced TOC analysis features.
"""

from epub_toc import get_toc, search_toc, get_toc_stats, compare_tocs

# Path to test files
BOOK1 = 'tests/data/epub_samples/Quick Start Guide - John Schember.epub'
BOOK2 = 'tests/data/epub_samples/syuzen_zontag-o_fotografii-1489340408 2.epub'

# Get TOC statistics
print("\n=== TOC Statistics ===")
stats = get_toc_stats(BOOK1)
print(f"Total entries: {stats['total_entries']}")
print(f"Maximum depth: {stats['max_depth']}")
print("Entries by level:")
for level, count in stats['chapters_by_level'].items():
    print(f"  Level {level}: {count} entries")

# Search in TOC
print("\n=== Search Results ===")
results = search_toc(BOOK1, "chapter", case_sensitive=False)
for result in results:
    print(f"Found: {result['path']}")

# Compare two books
print("\n=== TOC Comparison ===")
diff = compare_tocs(BOOK1, BOOK2)
print(f"Common entries: {len(diff['common_entries'])}")
print(f"Unique to first book: {len(diff['unique_to_first'])}")
print(f"Unique to second book: {len(diff['unique_to_second'])}")
print("\nStructure differences:")
print(f"  First book total: {diff['structure_differences']['first_total']}")
print(f"  Second book total: {diff['structure_differences']['second_total']}")
print(f"  Common entries: {diff['structure_differences']['common_count']}") 