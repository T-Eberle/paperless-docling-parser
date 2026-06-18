from __future__ import annotations

from pgx_docling.base import BaseDoclingConverter, PdfConversionMode, get_pdf_conversion_mode

# Read version from package metadata
def _get_version() -> str:
    """Read version from package metadata."""
    try:
        from importlib.metadata import version
        return version("pgx-docling-parser-core")
    except Exception:
        # Fallback for development or if package not installed
        return "0.0.0"

__version__ = _get_version()

__all__ = [
    "__version__",
    "BaseDoclingConverter",
    "PdfConversionMode",
    "get_pdf_conversion_mode",
]