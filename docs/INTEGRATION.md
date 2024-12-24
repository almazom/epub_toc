# Руководство по интеграции EPUB TOC Parser

## Содержание
1. [Требования](#требования)
2. [Установка](#установка)
3. [Базовое использование](#базовое-использование)
4. [Расширенные возможности](#расширенные-возможности)
5. [Обработка ошибок](#обработка-ошибок)
6. [Примеры интеграции](#примеры-интеграции)
7. [Лучшие практики](#лучшие-практики)

## Требования

### Системные требования
- Python 3.8 или выше
- Установленные зависимости из requirements.txt

### Зависимости
```bash
pip install -r requirements.txt
```

## Установка

1. Клонируйте репозиторий:
```bash
git clone [url-репозитория]
cd [директория-проекта]
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Импортируйте модуль в ваш проект:
```python
from epub_toc_parser import EPUBTOCParser
```

## Базовое использование

### Инициализация парсера

```python
from epub_toc_parser import EPUBTOCParser

# Создание экземпляра парсера
parser = EPUBTOCParser()

# Парсинг EPUB файла
toc = parser.parse('path/to/your/book.epub')
```

### Получение оглавления

```python
# Получение структурированного оглавления
toc_structure = toc.get_structure()

# Получение плоского списка
flat_toc = toc.get_flat_list()
```

## Расширенные возможности

### Настройка парсера

```python
parser = EPUBTOCParser(
    max_depth=5,  # Максимальная глубина оглавления
    ignore_empty=True,  # Игнорировать пустые элементы
    validate_links=True  # Проверять корректность ссылок
)
```

### Работа с метаданными

```python
# Получение метаданных книги
metadata = toc.get_metadata()

# Доступ к конкретным полям
title = metadata.get('title')
author = metadata.get('author')
```

## Обработка ошибок

```python
from epub_toc_parser.exceptions import EPUBParserError

try:
    toc = parser.parse('book.epub')
except EPUBParserError as e:
    print(f"Ошибка парсинга: {e}")
except FileNotFoundError:
    print("Файл не найден")
```

## Примеры интеграции

### Интеграция с веб-приложением (Flask)

```python
from flask import Flask, jsonify
from epub_toc_parser import EPUBTOCParser

app = Flask(__name__)
parser = EPUBTOCParser()

@app.route('/parse-epub', methods=['POST'])
def parse_epub():
    try:
        epub_file = request.files['epub']
        toc = parser.parse(epub_file)
        return jsonify({
            'structure': toc.get_structure(),
            'metadata': toc.get_metadata()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

### Интеграция с Django

```python
from django.views import View
from django.http import JsonResponse
from epub_toc_parser import EPUBTOCParser

class EPUBParserView(View):
    def post(self, request):
        parser = EPUBTOCParser()
        epub_file = request.FILES.get('epub')
        
        try:
            toc = parser.parse(epub_file)
            return JsonResponse({
                'structure': toc.get_structure(),
                'metadata': toc.get_metadata()
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
```

## Лучшие практики

1. **Обработка больших файлов**
   - Используйте асинхронную обработку для больших файлов
   - Реализуйте механизм кэширования результатов
   - Добавьте индикацию прогресса для длительных операций

```python
async def process_large_epub(file_path):
    parser = EPUBTOCParser()
    toc = await parser.parse_async(file_path)
    return toc
```

2. **Валидация входных данных**
   - Проверяйте формат файла перед обработкой
   - Валидируйте размер файла
   - Используйте таймауты для операций

```python
def validate_epub(file_path):
    if not file_path.endswith('.epub'):
        raise ValueError("Неверный формат файла")
    
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError("Файл слишком большой")
```

3. **Кэширование**
   - Реализуйте кэширование для часто используемых данных
   - Используйте механизм инвалидации кэша

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_toc(file_path):
    parser = EPUBTOCParser()
    return parser.parse(file_path)
```

4. **Логирование**
   - Настройте подробное логирование операций
   - Отслеживайте ошибки и предупреждения

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_with_logging(file_path):
    logger.info(f"Начало парсинга файла: {file_path}")
    try:
        parser = EPUBTOCParser()
        toc = parser.parse(file_path)
        logger.info("Парсинг успешно завершен")
        return toc
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        raise
```

5. **Безопасность**
   - Проверяйте права доступа к файлам
   - Санитизируйте входные данные
   - Ограничивайте доступ к API

6. **Производительность**
   - Используйте пулы потоков для параллельной обработки
   - Оптимизируйте использование памяти
   - Реализуйте постраничную загрузку для больших структур

```python
from concurrent.futures import ThreadPoolExecutor

def process_multiple_epubs(file_paths):
    with ThreadPoolExecutor() as executor:
        results = executor.map(parser.parse, file_paths)
    return list(results)
``` 