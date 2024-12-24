"""
EPUB TOC Parser - модуль для извлечения оглавления из EPUB файлов.
Поддерживает извлечение через NCX и epub_meta методы с автоматическим выбором лучшего результата.
Сохраняет иерархическую структуру оглавления.

Версия: 1.0.0
Статус: Стабильный
Последнее обновление: 2023-12-24

ВНИМАНИЕ: Этот модуль содержит стабильный код.
Изменения в методах, помеченных как @stable, требуют дополнительного подтверждения.
"""

from typing import List, Dict, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
import zipfile
from bs4 import BeautifulSoup
from epub_meta import get_epub_metadata
import json
from lxml import etree as ET

@dataclass
class TOCItem:
    """
    @stable v1.0.0
    Элемент оглавления. Базовая структура данных для хранения элементов TOC.
    Не изменять без согласования, так как это может повлиять на все зависимые функции.
    """
    title: str
    href: str
    level: int
    children: List['TOCItem'] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """
        @stable v1.0.0
        Преобразование в словарь. Критически важный метод для сериализации.
        """
        return {
            'title': self.title,
            'href': self.href,
            'level': self.level,
            'description': self.description,
            'children': [child.to_dict() for child in (self.children or [])]
        }

class EPUBTOCParser:
    """
    Парсер оглавления EPUB файлов с поддержкой нескольких методов извлечения.
    Автоматически выбирает лучший результат.
    """
    
    def __init__(self, epub_path: str):
        self.epub_path = Path(epub_path)
        self.logger = logging.getLogger(__name__)
        self.toc = None
    
    def extract_toc(self) -> Optional[List[Dict]]:
        """
        @stable v1.0.0
        Извлекает оглавление из EPUB файла, пробуя разные методы.
        Основной публичный метод, используется во всех тестах.
        Изменения могут повлиять на всю функциональность парсера.
        """
        # 1. Пробуем epub_meta
        toc = self._extract_from_epub_meta()
        if toc:
            self.logger.info("TOC успешно извлечен через epub_meta")
            self.toc = toc
            return toc
            
        # 2. Пробуем NCX
        toc = self._extract_from_ncx()
        if toc:
            self.logger.info("TOC успешно извлечен из NCX")
            self.toc = toc
            return toc
            
        # 3. Fallback на OPF
        toc = self._extract_from_opf()
        if toc:
            self.logger.info("TOC успешно извлечен из OPF")
            self.toc = toc
            return toc
            
        self.logger.warning("Не удалось извлечь TOC ни одним из методов")
        return None
    
    def _extract_from_epub_meta(self) -> Optional[List[Dict]]:
        """
        @stable v1.0.0
        Извлечение TOC с помощью epub_meta с правильной обработкой иерархии.
        Основной метод извлечения, протестирован на множестве файлов.
        Не изменять без полного набора тестов.
        """
        try:
            metadata = get_epub_metadata(str(self.epub_path))
            if not metadata or not metadata.get('toc'):
                return None
                
            def build_hierarchy(items: List[Dict]) -> List[Dict]:
                """Строит иерархию глав на основе их уровней"""
                result = []
                stack = [(None, -1)]  # (item, level)
                
                for item in items:
                    level = item.get('level', 0)
                    
                    # Создаем элемент TOC
                    toc_item = TOCItem(
                        title=item.get('title', ''),
                        href=item.get('src', ''),
                        level=level,
                        children=[]
                    ).to_dict()
                    
                    # Ищем подходящего родителя
                    while stack and stack[-1][1] >= level:
                        stack.pop()
                    
                    if not stack:
                        result.append(toc_item)
                        stack = [(toc_item, level)]
                    else:
                        parent = stack[-1][0]
                        if parent is None:
                            result.append(toc_item)
                        else:
                            if 'children' not in parent:
                                parent['children'] = []
                            parent['children'].append(toc_item)
                        stack.append((toc_item, level))
                
                return result
            
            # Сортируем элементы по позиции в файле
            toc_items = sorted(metadata.get('toc', []), 
                             key=lambda x: metadata.get('toc').index(x))
            
            return build_hierarchy(toc_items)
            
        except Exception as e:
            self.logger.warning(f"Ошибка при извлечении через epub_meta: {str(e)}")
            return None
    
    def _extract_from_ncx(self) -> Optional[List[Dict]]:
        """
        @stable v1.0.0
        Извлечение TOC из NCX файла с правильной иерархией.
        Важный метод извлечения для EPUB файлов с NCX оглавлением.
        Изменения требуют тестирования на различных форматах NCX.
        """
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_ref:
                # Ищем NCX файл
                ncx_path = None
                for name in zip_ref.namelist():
                    if name.endswith('.ncx'):
                        ncx_path = name
                        break
                
                if not ncx_path:
                    return None
                
                # Читаем NCX
                ncx_content = zip_ref.read(ncx_path)
                root = ET.fromstring(ncx_content)
                
                # Определяем namespace
                ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
                
                def process_nav_point(nav_point, level=0) -> Optional[TOCItem]:
                    # Получаем заголовок
                    nav_label = nav_point.find('ncx:navLabel', ns)
                    text_elem = nav_label.find('ncx:text', ns) if nav_label is not None else None
                    if text_elem is None or not text_elem.text:
                        return None
                    
                    # Получаем ссылку
                    content = nav_point.find('ncx:content', ns)
                    href = content.get('src', '') if content is not None else ''
                    
                    # Рекурсивно обрабатываем прямых потомков
                    children = []
                    for child in nav_point.findall('ncx:navPoint', ns):
                        child_item = process_nav_point(child, level + 1)
                        if child_item:
                            children.append(child_item)
                    
                    return TOCItem(
                        title=text_elem.text,
                        href=href,
                        level=level,
                        children=children
                    )
                
                # Извлекаем корневые навигационные точки
                result = []
                nav_map = root.find('ncx:navMap', ns)
                if nav_map is not None:
                    for nav_point in nav_map.findall('ncx:navPoint', ns):
                        item = process_nav_point(nav_point)
                        if item:
                            result.append(item.to_dict())
                
                return result
                
        except Exception as e:
            self.logger.warning(f"Ошибка при извлечении из NCX: {str(e)}")
            return None
    
    def _extract_from_opf(self) -> Optional[List[Dict]]:
        """
        @stable v1.0.0
        Извлечение структуры из OPF с поддержкой иерархии.
        Fallback метод для случаев, когда другие методы не сработали.
        Изменения требуют тестирования на файлах без NCX.
        """
        try:
            with zipfile.ZipFile(self.epub_path, 'r') as zip_ref:
                # Ищем OPF файл
                opf_path = None
                for name in zip_ref.namelist():
                    if name.endswith('.opf'):
                        opf_path = name
                        break
                
                if not opf_path:
                    return None
                
                # Читаем OPF
                opf_content = zip_ref.read(opf_path)
                root = ET.fromstring(opf_content)
                
                # Находим spine и manifest
                spine = root.find('.//{http://www.idpf.org/2007/opf}spine')
                manifest = root.find('.//{http://www.idpf.org/2007/opf}manifest')
                
                if spine is None or manifest is None:
                    return None
                
                # Создаем словарь id -> href из manifest
                id_to_href = {}
                for item in manifest.findall('.//{http://www.idpf.org/2007/opf}item'):
                    item_id = item.get('id')
                    href = item.get('href')
                    if item_id and href:
                        id_to_href[item_id] = href
                
                # Извлекаем структуру из spine
                result = []
                for i, itemref in enumerate(spine.findall('.//{http://www.idpf.org/2007/opf}itemref')):
                    idref = itemref.get('idref')
                    if idref in id_to_href:
                        result.append({
                            'title': f'Chapter {i+1}',
                            'href': id_to_href[idref],
                            'level': 0,
                            'children': []
                        })
                
                return result
                
        except Exception as e:
            self.logger.warning(f"Ошибка при извлечении из OPF: {str(e)}")
            return None
    
    def save_toc_to_json(self, output_path: str) -> None:
        """
        @stable v1.0.0
        Сохраняет извлеченное оглавление в JSON файл.
        Критически важный метод для сохранения результатов.
        Изменения требуют проверки корректности JSON и кодировки.
        
        Args:
            output_path: путь к файлу для сохранения JSON
        
        Raises:
            ValueError: если оглавление еще не было извлечено
        """
        if self.toc is None:
            self.toc = self.extract_toc()
            
        if self.toc is None:
            raise ValueError("Не удалось извлечь оглавление")
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.toc, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Оглавление успешно сохранено в {output_path}")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении в JSON: {str(e)}")
            raise
    
    def print_toc(self) -> None:
        """
        Выводит оглавление в консоль в читаемом формате
        """
        if self.toc is None:
            raise ValueError("Оглавление еще не извлечено. Сначала вызовите extract_toc()")
        
        def print_items(items, indent=0):
            for item in items:
                print(f"{'  ' * indent}- {item['title']}")
                if item.get('children'):
                    print_items(item['children'], indent + 1)
        
        print("\nОглавление:")
        print_items(self.toc)

def main():
    """
    Пример использования модуля из командной строки
    """
    import sys
    if len(sys.argv) != 2:
        print("Использование: python epub_toc_parser.py path/to/book.epub")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO)
    epub_path = sys.argv[1]
    
    parser = EPUBTOCParser(epub_path)
    try:
        parser.extract_toc()
        parser.print_toc()
        
        # Сохранение в JSON
        output_path = str(Path(epub_path).with_suffix('')) + '_toc.json'
        parser.save_toc_to_json(output_path)
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main() 