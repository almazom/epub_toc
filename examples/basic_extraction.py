#!/usr/bin/env python3
"""Basic example of TOC extraction from an EPUB file."""

from epub_toc import EPUBTOCParser

def main():
    # Initialize parser with an EPUB file
    parser = EPUBTOCParser('sample_books/book.epub')
    
    # Extract the table of contents
    toc = parser.extract_toc()
    
    # Print the TOC structure
    print("\nTable of Contents Structure:")
    parser.print_toc()
    
    # Save TOC to JSON
    parser.save_toc_to_json('output/book_toc.json')
    
    # Access TOC data programmatically
    print("\nAccessing first chapter:")
    first_chapter = toc[0]
    print(f"Title: {first_chapter['title']}")
    print(f"Link: {first_chapter['href']}")
    
    # Access nested sections if any
    if first_chapter['children']:
        print("\nFirst chapter sections:")
        for section in first_chapter['children']:
            print(f"- {section['title']}")

if __name__ == '__main__':
    main() 