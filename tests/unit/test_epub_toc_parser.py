import os
import pytest
import json
import tempfile
from epub_toc_parser import EPUBTOCParser, TOCItem

# Путь к тестовым EPUB файлам
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'epub_samples')

def get_test_epub_path(filename):
    """Получение полного пути к тестовому EPUB файлу"""
    return os.path.join(SAMPLES_DIR, filename)

class TestEPUBTOCParser:
    """Тесты для парсера оглавления EPUB"""
    
    @pytest.fixture
    def sample_epub_files(self):
        """Фикстура с тестовыми файлами"""
        return [
            'syuzen_zontag-o_fotografii-1489340408.epub',  # Небольшой файл
            'stiven_pinker_enlightenment_now_.epub',  # Большой файл
            'umberto_eko-pyat_esse_na_temi_etiki-65ca8c508dead.epub'  # Средний файл
        ]
    
    def test_init(self):
        """Тест инициализации парсера"""
        epub_path = get_test_epub_path('syuzen_zontag-o_fotografii-1489340408.epub')
        parser = EPUBTOCParser(epub_path)
        assert parser.epub_path.name == 'syuzen_zontag-o_fotografii-1489340408.epub'
        
    def test_toc_item_to_dict(self):
        """Тест преобразования TOCItem в словарь"""
        item = TOCItem(
            title="Chapter 1",
            href="chapter1.xhtml",
            level=1,
            children=[],
            description="First chapter"
        )
        dict_item = item.to_dict()
        assert dict_item['title'] == "Chapter 1"
        assert dict_item['href'] == "chapter1.xhtml"
        assert dict_item['level'] == 1
        assert dict_item['children'] == []
        assert dict_item['description'] == "First chapter"
    
    @pytest.mark.parametrize('epub_file', [
        'syuzen_zontag-o_fotografii-1489340408.epub',
        'stiven_pinker_enlightenment_now_.epub',
        'umberto_eko-pyat_esse_na_temi_etiki-65ca8c508dead.epub'
    ])
    def test_extract_toc(self, epub_file):
        """Тест извлечения оглавления из разных EPUB файлов"""
        parser = EPUBTOCParser(get_test_epub_path(epub_file))
        toc = parser.extract_toc()
        
        # Проверяем базовую структуру
        assert toc is not None
        assert isinstance(toc, list)
        assert len(toc) > 0
        
        # Проверяем структуру первого элемента
        first_item = toc[0]
        assert 'title' in first_item
        assert 'href' in first_item
        assert 'level' in first_item
        assert 'children' in first_item
        
        # Проверяем типы данных
        assert isinstance(first_item['title'], str)
        assert isinstance(first_item['href'], str)
        assert isinstance(first_item['level'], int)
        assert isinstance(first_item['children'], list)
    
    def test_extract_methods(self):
        """Тест методов извлечения оглавления"""
        parser = EPUBTOCParser(get_test_epub_path('syuzen_zontag-o_fotografii-1489340408.epub'))
        
        # Проверяем, что хотя бы один из методов возвращает результат
        toc_meta = parser._extract_from_epub_meta()
        toc_ncx = parser._extract_from_ncx()
        toc_opf = parser._extract_from_opf()
        
        assert any([toc_meta, toc_ncx, toc_opf]), "Ни один метод не вернул результат"
        
        # Проверяем типы для непустых результатов
        if toc_meta:
            assert isinstance(toc_meta, list)
        if toc_ncx:
            assert isinstance(toc_ncx, list)
        if toc_opf:
            assert isinstance(toc_opf, list)
    
    def test_file_not_found(self):
        """Тест обработки отсутствующего файла"""
        with pytest.raises(Exception) as exc_info:
            parser = EPUBTOCParser(get_test_epub_path('nonexistent.epub'))
            parser.extract_toc()
        assert str(exc_info.value) != ""  # Проверяем, что есть сообщение об ошибке
    
    def test_toc_structure(self):
        """Тест структуры оглавления"""
        # Проверяем на нескольких файлах
        test_files = [
            'stiven_pinker_enlightenment_now_.epub',
            'umberto_eko-pyat_esse_na_temi_etiki-65ca8c508dead.epub'
        ]
        
        for epub_file in test_files:
            parser = EPUBTOCParser(get_test_epub_path(epub_file))
            toc = parser.extract_toc()
            
            # Проверяем базовую структуру
            assert isinstance(toc, list)
            assert len(toc) > 0
            
            # Проверяем структуру элементов
            def check_toc_item(item):
                assert isinstance(item, dict)
                assert 'title' in item
                assert 'href' in item
                assert 'level' in item
                assert 'children' in item
                
                # Рекурсивно проверяем дочерние элементы
                for child in item['children']:
                    check_toc_item(child)
            
            # Проверяем все элементы
            for item in toc:
                check_toc_item(item) 
    
    def test_save_toc_to_json(self):
        """Тест сохранения оглавления в JSON"""
        parser = EPUBTOCParser(get_test_epub_path('syuzen_zontag-o_fotografii-1489340408.epub'))
        toc = parser.extract_toc()
        
        # Создаем временный файл для теста
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            # Сохраняем TOC в JSON
            parser.save_toc_to_json(tmp_file.name)
            
            # Читаем сохраненный JSON
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                saved_toc = json.load(f)
            
            # Проверяем структуру
            assert isinstance(saved_toc, list)
            assert len(saved_toc) > 0
            assert saved_toc == toc
            
        # Удаляем временный файл
        os.unlink(tmp_file.name) 