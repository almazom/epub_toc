"""Custom exceptions for EPUB TOC extraction."""

class EPUBTOCError(Exception):
    """Base exception for all EPUB TOC related errors."""
    pass

class ValidationError(EPUBTOCError):
    """Raised when EPUB file validation fails."""
    pass

class ExtractionError(EPUBTOCError):
    """Raised when TOC extraction fails."""
    pass

class StructureError(EPUBTOCError):
    """Raised when EPUB internal structure is invalid."""
    pass

class ParsingError(EPUBTOCError):
    """Raised when parsing specific TOC format fails."""
    pass

class ConversionError(EPUBTOCError):
    """Raised when converting between TOC formats fails."""
    pass

class OutputError(EPUBTOCError):
    """Raised when saving or outputting TOC fails."""
    pass 