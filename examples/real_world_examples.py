#!/usr/bin/env python3
"""
Real-world examples of using epub-toc-extractor with actual EPUB files.
These examples demonstrate practical usage with publicly available books from Project Gutenberg.
"""

import os
from epub_toc import EPubTOC

def example_pride_and_prejudice():
    """
    Extract TOC from Pride and Prejudice by Jane Austen
    Source: https://www.gutenberg.org/ebooks/1342
    """
    # URL to the EPUB file
    epub_url = "https://www.gutenberg.org/ebooks/1342.epub.images"
    
    # Create EPubTOC instance
    extractor = EPubTOC()
    
    # Download and process the EPUB
    toc = extractor.extract_from_url(epub_url)
    
    # Print the table of contents
    print("=== Pride and Prejudice TOC ===")
    for entry in toc:
        print(f"{entry.level * '  '}- {entry.title}")

def example_alice_in_wonderland():
    """
    Extract TOC from Alice's Adventures in Wonderland by Lewis Carroll
    Source: https://www.gutenberg.org/ebooks/11
    """
    epub_url = "https://www.gutenberg.org/ebooks/11.epub.images"
    
    extractor = EPubTOC()
    toc = extractor.extract_from_url(epub_url)
    
    print("\n=== Alice in Wonderland TOC ===")
    for entry in toc:
        print(f"{entry.level * '  '}- {entry.title}")

def example_sherlock_holmes():
    """
    Extract TOC from The Adventures of Sherlock Holmes by Arthur Conan Doyle
    Source: https://www.gutenberg.org/ebooks/1661
    """
    epub_url = "https://www.gutenberg.org/ebooks/1661.epub.images"
    
    extractor = EPubTOC()
    toc = extractor.extract_from_url(epub_url)
    
    print("\n=== The Adventures of Sherlock Holmes TOC ===")
    for entry in toc:
        print(f"{entry.level * '  '}- {entry.title}")

if __name__ == "__main__":
    # Run all examples
    example_pride_and_prejudice()
    example_alice_in_wonderland()
    example_sherlock_holmes() 