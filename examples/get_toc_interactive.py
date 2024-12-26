#!/usr/bin/env python3
"""
Interactive script to get TOC from EPUB file.
Just run it and follow the prompts.
"""

import json
from epub_toc import EPUBTOCParser
from epub_links import AVAILABLE_EPUBS

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def get_toc(path_or_url):
    try:
        # Create parser with the file path
        parser = EPUBTOCParser(path_or_url)
        # Extract TOC
        return parser.extract_toc()
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return None

def show_menu():
    print("\n=== EPUB TOC Extractor ===")
    print("1. Choose from test files")
    print("2. Enter custom path/URL")
    print("3. Exit")
    return input("\nChoose option (1-3): ")

def show_test_files():
    print("\nAvailable test files:")
    for i, (title, path) in enumerate(AVAILABLE_EPUBS.items(), 1):
        print(f"{i}. {title}")
        print(f"   Path: {path}")
    
    while True:
        try:
            choice = int(input("\nChoose file number (or 0 to go back): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(AVAILABLE_EPUBS):
                return list(AVAILABLE_EPUBS.values())[choice - 1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def main():
    while True:
        choice = show_menu()
        
        if choice == "1":
            path = show_test_files()
            if path:
                try:
                    print("\nExtracting TOC...")
                    toc = get_toc(path)
                    if toc:
                        print("\nTable of Contents:")
                        print_json(toc)
                except Exception as e:
                    print(f"\nError: {str(e)}")
                input("\nPress Enter to continue...")
        
        elif choice == "2":
            path = input("\nEnter path or URL: ").strip()
            if path:
                try:
                    print("\nExtracting TOC...")
                    toc = get_toc(path)
                    if toc:
                        print("\nTable of Contents:")
                        print_json(toc)
                except Exception as e:
                    print(f"\nError: {str(e)}")
                input("\nPress Enter to continue...")
        
        elif choice == "3":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Goodbye!") 