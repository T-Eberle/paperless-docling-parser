from __future__ import annotations

from pathlib import Path

# Read version from VERSION file at repository root
_version_file = Path(__file__).parent.parent.parent.parent.parent / "VERSION"
__version__ = _version_file.read_text().strip() if _version_file.exists() else "0.0.0"

__all__ = ["__version__"]
