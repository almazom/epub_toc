import os
import json
import time
from datetime import datetime
from pathlib import Path
from epub_toc_parser import EPUBTOCParser

# Путь к тестовым EPUB файлам
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'epub_samples')
# Путь к директории с отчетами (в корне проекта)
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
# Путь к директории с извлеченными TOC
TOC_DIR = os.path.join(REPORT_DIR, 'toc')

def analyze_epub_file(file_path: str) -> dict:
    """Анализ одного EPUB файла"""
    start_time = time.time()
    parser = EPUBTOCParser(file_path)
    
    result = {
        'file_name': os.path.basename(file_path),
        'file_size': os.path.getsize(file_path) / 1024,  # KB
        'extraction_methods': {
            'epub_meta': False,
            'ncx': False,
            'opf': False
        },
        'success': False,
        'toc_items': 0,
        'max_depth': 0,
        'processing_time': 0,
        'error': None,
        'toc_file': None  # Путь к файлу с TOC
    }
    
    try:
        # Проверяем каждый метод извлечения
        toc_meta = parser._extract_from_epub_meta()
        toc_ncx = parser._extract_from_ncx()
        toc_opf = parser._extract_from_opf()
        
        result['extraction_methods']['epub_meta'] = toc_meta is not None
        result['extraction_methods']['ncx'] = toc_ncx is not None
        result['extraction_methods']['opf'] = toc_opf is not None
        
        # Получаем полное оглавление
        toc = parser.extract_toc()
        if toc:
            result['success'] = True
            result['toc_items'] = len(toc)
            
            # Вычисляем максимальную глубину
            def get_depth(items, current_depth=0):
                if not items:
                    return current_depth
                return max(get_depth(item.get('children', []), current_depth + 1) for item in items)
            
            result['max_depth'] = get_depth(toc)
            
            # Сохраняем TOC в отдельный файл
            if not os.path.exists(TOC_DIR):
                os.makedirs(TOC_DIR)
            
            # Создаем имя файла из имени EPUB, убирая расширение
            base_name = Path(result['file_name']).stem
            toc_file = os.path.join(TOC_DIR, f"{base_name}_toc.json")
            
            with open(toc_file, 'w', encoding='utf-8') as f:
                json.dump(toc, f, ensure_ascii=False, indent=2)
            
            result['toc_file'] = os.path.relpath(toc_file, REPORT_DIR)
            
    except Exception as e:
        result['error'] = str(e)
    
    result['processing_time'] = time.time() - start_time
    return result

def generate_report():
    """Генерация подробного отчета по всем EPUB файлам"""
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
    
    epub_files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith('.epub')]
    results = []
    
    total_start_time = time.time()
    
    for epub_file in epub_files:
        file_path = os.path.join(SAMPLES_DIR, epub_file)
        result = analyze_epub_file(file_path)
        results.append(result)
    
    total_time = time.time() - total_start_time
    
    # Формируем статистику
    stats = {
        'total_files': len(results),
        'successful_extractions': sum(1 for r in results if r['success']),
        'failed_extractions': sum(1 for r in results if not r['success']),
        'total_processing_time': total_time,
        'average_processing_time': total_time / len(results) if results else 0,
        'method_success_rate': {
            'epub_meta': sum(1 for r in results if r['extraction_methods']['epub_meta']),
            'ncx': sum(1 for r in results if r['extraction_methods']['ncx']),
            'opf': sum(1 for r in results if r['extraction_methods']['opf'])
        },
        'timestamp': datetime.now().isoformat()
    }
    
    # Сохраняем подробный отчет
    report = {
        'statistics': stats,
        'file_results': results
    }
    
    report_path = os.path.join(REPORT_DIR, f'epub_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Создаем текстовый отчет для быстрого просмотра
    txt_report_path = os.path.join(REPORT_DIR, f'epub_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(txt_report_path, 'w', encoding='utf-8') as f:
        f.write("=== Отчет по анализу EPUB файлов ===\n\n")
        f.write(f"Всего файлов: {stats['total_files']}\n")
        f.write(f"Успешно обработано: {stats['successful_extractions']}\n")
        f.write(f"Ошибок обработки: {stats['failed_extractions']}\n")
        f.write(f"Общее время обработки: {stats['total_processing_time']:.2f} сек\n")
        f.write(f"Среднее время на файл: {stats['average_processing_time']:.2f} сек\n\n")
        
        f.write("Успешность методов извлечения:\n")
        f.write(f"- epub_meta: {stats['method_success_rate']['epub_meta']}\n")
        f.write(f"- NCX: {stats['method_success_rate']['ncx']}\n")
        f.write(f"- OPF: {stats['method_success_rate']['opf']}\n\n")
        
        f.write("Подробности по файлам:\n")
        for result in sorted(results, key=lambda x: x['file_name']):
            f.write(f"\n{result['file_name']}:\n")
            f.write(f"  Размер: {result['file_size']:.1f} KB\n")
            f.write(f"  Успех: {'Да' if result['success'] else 'Нет'}\n")
            if result['success']:
                f.write(f"  Элементов TOC: {result['toc_items']}\n")
                f.write(f"  Макс. глубина: {result['max_depth']}\n")
                f.write(f"  TOC файл: {result['toc_file']}\n")
            if result['error']:
                f.write(f"  Ошибка: {result['error']}\n")
            f.write(f"  Время обработки: {result['processing_time']:.2f} сек\n")
    
    return report_path, txt_report_path

if __name__ == '__main__':
    json_report, txt_report = generate_report()
    print(f"Отчеты сохранены:\n- JSON: {json_report}\n- TXT: {txt_report}")
    print(f"\nTOC файлы сохранены в: {TOC_DIR}") 