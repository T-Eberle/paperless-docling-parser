# paperless-docling-parser

A Paperless-ngx parser plugin that uses [Docling](https://github.com/DS4SD/docling) to parse PDF files and convert them to Markdown format, making documents "AI ready" for agents and RAG (Retrieval-Augmented Generation) use cases.

## What is this package for?

This plugin integrates Docling's advanced document parsing capabilities into Paperless-ngx. It:

- **Parses PDF files** using Docling
- **Converts content to Markdown** with proper structure preservation (headings, lists, tables, etc.)
- **Makes documents AI-ready** for use with LLM agents and RAG systems
- **Preserves document structure** including tables, images, and formatting
- **Supports multiple OCR backends** (EasyOCR, Tesseract, Vision Language Models)

The Markdown output is optimized for semantic search and AI processing, making your document archive queryable and usable by modern AI systems.

## Installation

### Option 1: Install via pip (Recommended for existing Paperless-ngx instances)

If you already have a Paperless-ngx instance running, you can install the `docling_serve` version of the package:

```bash
pip install pgx-docling-parser-serve
```

**Prerequisites:**
- A running [docling-serve](https://github.com/docling-project/docling-serve) instance (see below)
- Python 3.10 or higher

**Configure environment variables:**

```bash
export PAPERLESS_DOCLING_SERVE_URL="http://localhost:5000"
export PAPERLESS_DOCLING_SERVE_TIMEOUT="300.0"
export PAPERLESS_DOCLING_SERVE_MAX_RETRIES="3"
export PAPERLESS_DOCLING_PDF_CONVERSION_MODE="easyocr"
```

The plugin will be automatically discovered by Paperless-ngx through its entry point system.

### Option 2: Docker Installation

#### Using Dockerfile

Add this to your Paperless-ngx Dockerfile:

```dockerfile
# Use the official Paperless-ngx image as base
FROM ghcr.io/paperless-ngx/paperless-ngx:latest

# Switch to root to install packages
USER root

# Install minimal system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the plugin with docling-serve variant
RUN pip install --no-cache-dir pgx-docling-parser-serve

# Switch back to paperless user
USER paperless
```

#### Using Docker Compose

This repository includes a complete Docker Compose setup with Paperless-ngx and Docling-Serve pre-configured:

```bash
git clone https://github.com/T-Eberle/paperless-docling-parser.git
cd paperless-docling-parser
docker-compose up -d
```

Access Paperless-ngx at `http://localhost:8000` (default credentials: admin/admin - change after first login!)

## Setting up Docling-Serve

The `docling_serve` version requires a separate Docling-Serve instance for document processing.

### Run Docling-Serve with Docker

```bash
docker run -d -p 5000:5000 ds4sd/docling-serve:latest
```

### Run Docling-Serve with GPU support

```bash
docker run -d -p 5000:5000 \
  --gpus all \
  ds4sd/docling-serve:latest
```

### Verify Docling-Serve is running

```bash
curl http://localhost:5000/health
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PAPERLESS_DOCLING_SERVE_URL` | URL of the docling-serve API | `http://localhost:5000` |
| `PAPERLESS_DOCLING_SERVE_TIMEOUT` | Timeout for API calls (seconds) | `300.0` |
| `PAPERLESS_DOCLING_SERVE_MAX_RETRIES` | Maximum retry attempts | `3` |
| `PAPERLESS_DOCLING_PDF_CONVERSION_MODE` | OCR backend to use | `easyocr` |

### PDF Conversion Modes

- **easyocr** (default): Good balance of speed and accuracy, supports multiple languages
- **tesseract**: Fast and reliable for standard documents, but lacks on accuracy
- **granite_docling**: Best accuracy for complex layouts using Vision Language Models (requires far more resources)

## Troubleshooting

### Check if the plugin is installed

```bash
pip list | grep pgx-docling-parser
```

### Test Docling-Serve connection

```bash
curl http://localhost:5000/health
```

### Common Issues

**Connection refused to docling-serve:**
- Ensure docling-serve is running
- Verify the URL in `PAPERLESS_DOCLING_SERVE_URL` is correct
- Check network connectivity

**Timeout errors:**
- Increase `PAPERLESS_DOCLING_SERVE_TIMEOUT` for large documents
- Consider enabling GPU support for faster processing

## Links

- [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx)
- [Docling](https://github.com/DS4SD/docling)
- [Issues](https://github.com/T-Eberle/paperless-docling-parser/issues)

## License

MIT License - see LICENSE file for details