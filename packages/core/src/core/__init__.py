from __future__ import annotations

from pathlib import Path
from core.base import BaseDoclingConverter, PdfConversionMode, get_pdf_conversion_mode

# Read version from VERSION file at repository root
_version_file = Path(__file__).parent.parent.parent.parent.parent / "VERSION"
__version__ = _version_file.read_text().strip() if _version_file.exists() else "0.0.0"

__all__ = [
    "__version__",
    "BaseDoclingConverter",
    "PdfConversionMode",
    "get_pdf_conversion_mode",
]