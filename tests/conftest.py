"""Configuration and shared fixtures for tests."""

import pytest
import logging
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )

@pytest.fixture
def data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def epub_samples_dir(data_dir):
    """Return path to EPUB samples directory."""
    samples_dir = data_dir / "epub_samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    return samples_dir

@pytest.fixture
def temp_epub(tmp_path):
    """Create a temporary EPUB file for testing."""
    epub_path = tmp_path / "test.epub"
    epub_path.touch()
    return epub_path 