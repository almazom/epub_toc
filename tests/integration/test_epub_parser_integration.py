import os
import json
import tempfile
import pytest
from epub_toc_parser import EPUBTOCParser

# Путь к тестовым EPUB файлам
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'epub_samples')

def get_test_epub_path(filename):
    """Получение полного пути к тестовому EPUB файлу"""
    return os.path.join(SAMPLES_DIR, filename)

class TestEPUBParserIntegration:
    """Интеграционные тесты для парсера EPUB"""
    
    @pytest.mark.parametrize('epub_file', [
        'syuzen_zontag-o_fotografii-1489340408.epub',
        'stiven_pinker_enlightenment_now_.epub'
    ])
    def test_full_extraction_cycle(self, epub_file):
        """Тест полного цикла извлечения и сохранения оглавления"""
        # Инициализация парсера
        parser = EPUBTOCParser(get_test_epub_path(epub_file))
        
        # Извлечение оглавления
        toc = parser.extract_toc()
        assert toc is not None
        assert len(toc) > 0
        
        # Сохранение в JSON
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            parser.save_toc_to_json(tmp_file.name)
            
            # Проверка сохраненного файла
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                saved_toc = json.load(f)
            
            # Проверка структуры и содержимого
            assert saved_toc == toc
            
            # Проверка обязательных полей
            for item in saved_toc:
                assert 'title' in item
                assert 'href' in item
                assert 'level' in item
                assert 'children' in item
            
        # Очистка
        os.unlink(tmp_file.name)
    
    def test_batch_processing(self):
        """Тест пакетной обработки нескольких файлов"""
        results = []
        
        # Получаем список всех EPUB файлов
        epub_files = [f for f in os.listdir(SAMPLES_DIR) if f.endswith('.epub')]
        
        for epub_file in epub_files[:3]:  # Берем первые 3 файла для теста
            parser = EPUBTOCParser(get_test_epub_path(epub_file))
            toc = parser.extract_toc()
            
            results.append({
                'file': epub_file,
                'toc_items': len(toc) if toc else 0,
                'success': toc is not None
            })
        
        # Проверяем результаты
        assert len(results) > 0
        for result in results:
            assert result['success'], f"Не удалось обработать файл {result['file']}"
            assert result['toc_items'] > 0, f"Нет элементов TOC в файле {result['file']}" 