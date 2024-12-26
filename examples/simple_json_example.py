#!/usr/bin/env python3
"""
Simple example showing how to get TOC as JSON with just one line of code.
Examples use both online and local EPUB files.
"""

from epub_toc import EPubTOC
import json

def print_json(data):
    """Helper function to print JSON in a readable format"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

# Example 1: Online EPUB from Project Gutenberg
print("\n=== Pride and Prejudice (Project Gutenberg) ===")
toc_json = EPubTOC().get_toc_json_from_url("https://www.gutenberg.org/ebooks/1342.epub.images")
print_json(toc_json)

# Example 2: Local EPUB files from our test data
print("\n=== Quick Start Guide (Local file) ===")
toc_json = EPubTOC().get_toc_json_from_file("tests/data/epub_samples/Quick Start Guide - John Schember.epub")
print_json(toc_json)

print("\n=== О фотографии - Сьюзен Зонтаг (Local file) ===")
toc_json = EPubTOC().get_toc_json_from_file("tests/data/epub_samples/syuzen_zontag-o_fotografii-1489340408 2.epub")
print_json(toc_json)

print("\n=== Краткая история кураторства - Ханс Ульрих Обрист (Local file) ===")
toc_json = EPubTOC().get_toc_json_from_file("tests/data/epub_samples/hans_ulrih_obrist-kratkaya_istoriya_kuratorstva-1494765847 2.epub")
print_json(toc_json)

# Example 3: One-liner for any EPUB
print("\n=== One-liner example ===")
print_json(EPubTOC().get_toc_json_from_file("tests/data/epub_samples/Quick Start Guide - John Schember.epub")) 