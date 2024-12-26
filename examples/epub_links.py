#!/usr/bin/env python3
"""
List of available EPUB files in our test data.
You can use any of these links with EPubTOC().get_toc_json_from_file()
"""

AVAILABLE_EPUBS = {
    "Quick Start Guide": 
        "tests/data/epub_samples/Quick Start Guide - John Schember.epub",
    
    "О фотографии (Сьюзен Зонтаг)": 
        "tests/data/epub_samples/syuzen_zontag-o_fotografii-1489340408 2.epub",
    
    "Краткая история кураторства (Ханс Ульрих Обрист)": 
        "tests/data/epub_samples/hans_ulrih_obrist-kratkaya_istoriya_kuratorstva-1494765847 2.epub",
    
    "Naked Lunch (William S. Burroughs)":
        "tests/data/epub_samples/uilyam_syuard_berrouz-naked_lunch-1490097759.epub",
    
    "Пять эссе на темы этики (Умберто Эко)":
        "tests/data/epub_samples/umberto_eko-pyat_esse_na_temi_etiki-65ca8c508dead.epub",
    
    "Московский дневник (Вальтер Беньямин)":
        "tests/data/epub_samples/valter_benyamin-moskovskij_dnevnik-1490536162.epub",
    
    "Символический обмен и смерть (Жан Бодрийяр)":
        "tests/data/epub_samples/zhan_bodrijyar-simvolicheskij_obmen_i_smert-1490299811.epub",
    
    "Язык как инстинкт (Стивен Пинкер)":
        "tests/data/epub_samples/stiven_pinker-yazik_kak_instinkt-1489079159 2.epub"
}

# Example of usage:
if __name__ == "__main__":
    from epub_toc import EPubTOC
    import json
    
    def print_json(data):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # Print all available books
    print("Available EPUB files:")
    for title, path in AVAILABLE_EPUBS.items():
        print(f"\n=== {title} ===")
        print(f"Path: {path}")
        print("\nTable of Contents:")
        toc_json = EPubTOC().get_toc_json_from_file(path)
        print_json(toc_json)
        print("\n" + "="*50) 