# Tests for paperless-ngx-docling

This directory contains unit and integration tests for the DoclingConverter.

## Prerequisites

1. **Running docling-serve instance**: The tests require a running docling-serve API server.
2. **Test dependencies**: Automatically managed by uv.

## Installation

Install the project with dev dependencies using uv:

```bash
uv sync --extra dev
```

This will install all required dependencies including pytest, pytest-asyncio, and reportlab.

## Running Tests

### Basic Test Run

Run all tests using uv:

```bash
uv run pytest
```

### Run Specific Test File

```bash
uv run pytest tests/test_converter.py
```

### Run with Custom docling-serve URL

If your docling-serve is running on a different URL:

```bash
PAPERLESS_DOCLING_SERVE_URL=http://localhost:5000 uv run pytest
```

### Run Only Integration Tests

```bash
uv run pytest -m integration
```

### Run with Detailed Output

To see print statements and more details:

```bash
uv run pytest -s
```

### Run Specific Test

```bash
uv run pytest tests/test_converter.py::TestDoclingConverter::test_convert_sync
```

## Test Structure

- `test_converter.py`: Main test file for DoclingConverter
  - `TestDoclingConverter`: Basic unit tests
  - `TestDoclingConverterIntegration`: Integration tests requiring docling-serve

## Environment Variables

The tests respect the following environment variables:

- `PAPERLESS_DOCLING_SERVE_URL`: URL of the docling-serve instance (default: `http://docling-serve:5000`)
- `PAPERLESS_DOCLING_SERVE_TIMEOUT`: Timeout for API calls in seconds (default: `300.0`)
- `PAPERLESS_DOCLING_SERVE_MAX_RETRIES`: Maximum number of retries (default: `3`)
- `PAPERLESS_DOCLING_PDF_CONVERSION_MODE`: Conversion mode (`easyocr`, `tesseract`, or `granite_docling`)

## Example Test Session

```bash
# Start docling-serve (if using Docker)
docker-compose up -d docling-serve

# Wait for service to be ready
sleep 10

# Install dev dependencies
uv sync --extra dev

# Run tests
PAPERLESS_DOCLING_SERVE_URL=http://localhost:5000 uv run pytest

# Or run with more details
PAPERLESS_DOCLING_SERVE_URL=http://localhost:5000 uv run pytest -s
```

## Test Coverage

The test suite covers:

1. **Initialization**: Converter setup and configuration
2. **Environment Variables**: Reading and applying configuration
3. **Async Conversion**: Testing the async `convert()` method
4. **Sync Conversion**: Testing the synchronous `convert_sync()` method
5. **Conversion Modes**: Testing different PDF conversion modes
6. **Conversion Options**: Verifying correct API parameters
7. **Full Workflow**: End-to-end integration test

## Troubleshooting

### Connection Errors

If you get connection errors:
- Ensure docling-serve is running and accessible
- Check the URL with `curl http://localhost:5000/health`
- Verify firewall/network settings

### Timeout Errors

If tests timeout:
- Increase the timeout: `PAPERLESS_DOCLING_SERVE_TIMEOUT=600 pytest ...`
- Check docling-serve logs for processing issues
- Ensure sufficient resources for docling-serve

### Import Errors

If you get import errors:
- Ensure the package is installed: `pip install -e .`
- Check that all dependencies are installed