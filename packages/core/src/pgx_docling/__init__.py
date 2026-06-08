from __future__ import annotations

from pathlib import Path
from pgx_docling.base import BaseDoclingConverter, PdfConversionMode, get_pdf_conversion_mode

# Read version from pyproject.toml
def _get_version() -> str:
    """Read version from pyproject.toml file."""
    try:
        import tomllib
    except ImportError:
        # Python < 3.11
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return "0.0.0"
    
    pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        return "0.0.0"
    
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"

__version__ = _get_version()

__all__ = [
    "__version__",
    "BaseDoclingConverter",
    "PdfConversionMode",
    "get_pdf_conversion_mode",
]