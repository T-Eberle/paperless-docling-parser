# pgx-docling-parser-serve

Remote converter for pgx-docling-parser using docling-serve API.

This package provides a remote document converter that uses the docling-serve API for document processing.

## Installation

Install this package directly from PyPI:

```bash
pip install pgx-docling-parser-serve
```

This will automatically install `pgx-docling-parser-core` as a dependency.

## Configuration

Configure the converter using environment variables:

- `PAPERLESS_DOCLING_SERVE_URL`: URL of the docling-serve instance (default: `http://docling-serve:5000`)
- `PAPERLESS_DOCLING_SERVE_TIMEOUT`: Request timeout in seconds (default: `300.0`)
- `PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS`: Maximum number of polling attempts (default: `60`)
- `PAPERLESS_DOCLING_POLL_INTERVAL`: Polling interval in seconds (default: `5.0`)
- `PAPERLESS_DOCLING_PDF_CONVERSION_MODE`: Conversion mode - `easyocr`, `tesseract`, or `granite_docling` (default: `easyocr`)

## How It Works

The converter uses a simple 3-step workflow:

1. **Create Task**: POST to `/v1/convert/file/async` to create an async conversion task
2. **Poll Status**: Repeatedly GET `/v1/status/poll/{task_id}` until task completes (success/failure)
3. **Fetch Result**: GET `/v1/result/{task_id}` to retrieve the converted document

The polling mechanism will retry up to `PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS` times with `PAPERLESS_DOCLING_POLL_INTERVAL` seconds between attempts.