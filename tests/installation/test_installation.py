"""Test package installation and imports."""

import importlib
import pkg_resources
import sys
import unittest


class TestInstallation(unittest.TestCase):
    """Test suite for package installation verification."""

    def test_package_installed(self):
        """Verify that epub_toc is installed."""
        # Check if package is in sys.modules
        self.assertIn('epub_toc', sys.modules)
        
        # Check if package can be found by pkg_resources
        dist = pkg_resources.get_distribution('epub_toc')
        self.assertIsNotNone(dist)
    
    def test_version(self):
        """Verify version is accessible and correct format."""
        import epub_toc
        version = epub_toc.__version__
        self.assertIsNotNone(version)
        self.assertRegex(version, r'^\d+\.\d+\.\d+')
    
    def test_public_interface(self):
        """Verify all public interfaces are importable."""
        # List of public interfaces
        public_interfaces = [
            'EPUBTOCParser',
            'TOCItem',
            'EPUBTOCError',
            'ValidationError',
            'ExtractionError',
            'StructureError',
            'ParsingError',
            'ConversionError',
            'OutputError'
        ]
        
        # Try importing each interface
        import epub_toc
        for interface in public_interfaces:
            self.assertTrue(
                hasattr(epub_toc, interface),
                f"Public interface '{interface}' not found"
            )
    
    def test_dependencies_installed(self):
        """Verify all required dependencies are installed."""
        with open('requirements.txt') as f:
            requirements = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith('#')
            ]
        
        for req in requirements:
            # Remove version specifiers
            package = req.split('>=')[0].split('==')[0].split('>')[0].strip()
            # Handle special cases for package names
            if package == 'beautifulsoup4':
                package = 'bs4'
            try:
                importlib.import_module(package)
            except ImportError as e:
                self.fail(f"Required dependency '{package}' not installed: {e}")
    
    def test_package_metadata(self):
        """Verify package metadata is correct."""
        dist = pkg_resources.get_distribution('epub_toc')
        
        # Check basic metadata
        self.assertIsNotNone(dist.version)
        self.assertIsNotNone(dist.project_name)
        self.assertEqual(dist.project_name, 'epub-toc')
        
        # Check package requirements
        requirements = [str(r) for r in dist.requires()]
        self.assertTrue(len(requirements) > 0, "No requirements found")
        
        # Verify Python version requirement through classifiers
        classifiers = dist.get_metadata_lines('PKG-INFO')
        python_version_classifiers = [c for c in classifiers if c.startswith('Classifier: Programming Language :: Python ::')]
        self.assertTrue(len(python_version_classifiers) > 0, "Python version classifiers not found")


if __name__ == '__main__':
    unittest.main() 