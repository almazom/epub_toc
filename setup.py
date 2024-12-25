"""Setup configuration for epub_toc package."""

from setuptools import setup, find_packages
import os

# Read README.md for long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="epub_toc",
    version="1.0.0",
    description="A Python tool for extracting table of contents from EPUB files with hierarchical structure support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Almaz Ilaletdinov",
    author_email="a.ilaletdinov@yandex.ru",
    url="https://github.com/almazilaletdinov/epub_toc",
    project_urls={
        "Documentation": "https://github.com/almazilaletdinov/epub_toc/docs",
        "Source": "https://github.com/almazilaletdinov/epub_toc",
        "Tracker": "https://github.com/almazilaletdinov/epub_toc/issues",
    },
    packages=find_packages(),
    install_requires=[
        "epub_meta>=0.0.7",
        "lxml>=4.9.3",
        "beautifulsoup4>=4.12.2",
        "ebooklib>=0.18",
        "tika>=2.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "types-beautifulsoup4>=4.12.0.7",
            "types-lxml>=2023.10.21",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    keywords="epub, ebook, toc, table of contents, parser, ebook-tools",
    entry_points={
        "console_scripts": [
            "epub_toc=epub_toc.cli:main",
        ],
    },
) 