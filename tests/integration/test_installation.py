"""Tests for package installation and uninstallation."""

import subprocess
import sys
import importlib
import pytest
import time
import shutil
import site
import os
import glob
import tempfile


def run_command(command):
    """Run shell command and return output."""
    process = subprocess.run(
        command,
        shell=True,
        check=True,
        capture_output=True,
        text=True
    )
    return process.stdout


def clean_package_from_system():
    """Clean package from system completely."""
    # Uninstall package
    try:
        run_command("pip uninstall -y epub_toc")
    except subprocess.CalledProcessError:
        pass

    # Remove from sys.modules
    for module in list(sys.modules.keys()):
        if module.startswith("epub_toc"):
            del sys.modules[module]

    # Remove from site-packages
    for site_dir in site.getsitepackages() + [site.getusersitepackages()]:
        for item in ["epub_toc.egg-link", "epub_toc", "epub_toc-*.dist-info"]:
            pattern = os.path.join(site_dir, item)
            try:
                for path in glob.glob(pattern):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
            except Exception:
                pass

    # Wait for filesystem operations to complete
    time.sleep(2)


def test_package_installation():
    """Test that package can be installed via pip."""
    clean_package_from_system()
    
    # Install package
    output = run_command("pip install epub_toc")
    assert "Successfully installed epub_toc" in output
    
    # Check that package can be imported
    epub_toc = importlib.import_module("epub_toc")
    assert hasattr(epub_toc, "EPUBTOCParser")
    
    # Check version
    assert hasattr(epub_toc, "__version__")
    
    # Check that all required modules are installed
    required_modules = [
        "epub_meta",
        "bs4",  # beautifulsoup4 импортируется как bs4
        "lxml",
        "ebooklib",
        "tika"
    ]
    
    for module in required_modules:
        importlib.import_module(module)


@pytest.mark.trylast
def test_package_uninstallation():
    """Test that package can be uninstalled via pip."""
    # Create a temporary virtual environment for isolation
    with tempfile.TemporaryDirectory() as tmp_dir:
        venv_dir = os.path.join(tmp_dir, "venv")
        run_command(f"python -m venv {venv_dir}")
        
        # Get path to python and pip in new venv
        if sys.platform == "win32":
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
        else:
            venv_python = os.path.join(venv_dir, "bin", "python")
            venv_pip = os.path.join(venv_dir, "bin", "pip")
        
        # Install package
        subprocess.run([venv_pip, "install", "epub_toc"], check=True)
        
        # Verify it's installed
        pip_list = subprocess.run(
            [venv_pip, "list"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout
        assert "epub_toc" in pip_list
        
        # Uninstall package
        subprocess.run([venv_pip, "uninstall", "-y", "epub_toc"], check=True)
        
        # Verify it's not in pip list anymore
        pip_list_after = subprocess.run(
            [venv_pip, "list"], 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout
        assert "epub_toc" not in pip_list_after


def test_development_installation():
    """Test that package can be installed in development mode."""
    clean_package_from_system()
    
    # Install in development mode
    output = run_command("pip install -e .")
    assert "Successfully installed" in output
    
    # Check that package can be imported
    epub_toc = importlib.import_module("epub_toc")
    assert hasattr(epub_toc, "EPUBTOCParser") 