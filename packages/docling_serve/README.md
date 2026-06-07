# paperless-docling-parser-docling-serve

Remote converter for paperless-docling-parser using docling-serve API.

This package provides a remote document converter that uses the docling-serve API for document processing.

## Installation

This package is automatically installed when you install the main package with the `docling-serve` extra:

```bash
pip install paperless-docling-parser[docling-serve]
```

## Configuration

Configure the converter using environment variables:

- `PAPERLESS_DOCLING_SERVE_URL`: URL of the docling-serve instance (default: `http://docling-serve:5000`)
- `PAPERLESS_DOCLING_SERVE_TIMEOUT`: Request timeout in seconds (default: `300.0`)
- `PAPERLESS_DOCLING_SERVE_MAX_RETRIES`: Maximum number of retries (default: `3`)
- `PAPERLESS_DOCLING_PDF_CONVERSION_MODE`: Conversion mode - `easyocr`, `tesseract`, or `granite_docling` (default: `easyocr`)