# paperless-docling-parser

A [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) parser plugin that uses [Docling](https://github.com/DS4SD/docling) to convert PDF files into richly-structured Markdown — making your document archive **AI-ready** for LLM agents and RAG pipelines.

---

## How it works

When Paperless-ngx ingests a PDF, this plugin intercepts it and sends it to a running [docling-serve](https://github.com/docling-project/docling-serve) instance. Docling performs layout-aware OCR and returns a structured [`DoclingDocument`](https://github.com/docling-project/docling-core), which is then exported to Markdown and stored as the document's full-text content.

```
PDF → docling-serve → DoclingDocument → Markdown → Paperless-ngx full-text
```

**Why Markdown?** Markdown preserves headings, lists, and tables in a format that semantic search engines and LLMs consume far better than raw OCR text.

---

## Packages

The plugin ships as two installable PyPI packages:

| Package | PyPI name | Purpose |
|---|---|---|
| **serve** | `pgx-docling-parser-serve` | Connects to an external docling-serve API — recommended for production |
| **core** | `pgx-docling-parser-core` | Shared base classes, installed automatically as a dependency |

> A `local` package (bundling Docling directly, no server needed) is planned but not yet available.

---

## Quick start — Docker Compose

The fastest way to get a complete, working stack (Paperless-ngx + PostgreSQL + Redis + the plugin):

```bash
git clone https://github.com/T-Eberle/paperless-docling-parser.git
cd paperless-docling-parser
docker compose up -d
```

Then open **http://localhost:8000** and log in with `admin` / `admin`.

> ⚠️ Change the default credentials and the `PAPERLESS_SECRET_KEY` value in [`docker-compose.yaml`](docker-compose.yaml) before exposing the instance to a network.

The compose file uses [`Dockerfile.docling_serve`](Dockerfile.docling_serve) to build a Paperless-ngx image with the plugin pre-installed. You need to supply your own docling-serve instance and point `PAPERLESS_DOCLING_SERVE_URL` at it (see [Configuration](#configuration)).

---

## Installation on an existing Paperless-ngx instance

### 1. Install the plugin

#### Via pip

```bash
pip install pgx-docling-parser-serve
```

#### Via Dockerfile (extend the official image)

```dockerfile
FROM ghcr.io/paperless-ngx/paperless-ngx:latest

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pgx-docling-parser-serve

USER paperless
```

Paperless-ngx discovers the plugin automatically via the `paperless_ngx.parsers` entry point — no extra registration is needed.

### 2. Start docling-serve

The plugin requires a running docling-serve instance to perform the actual conversion.

**CPU only:**
```bash
docker run -d -p 5000:5000 ds4sd/docling-serve:latest
```

**With GPU (strongly recommended for granite_docling mode):**
```bash
docker run -d -p 5000:5000 --gpus all ds4sd/docling-serve:latest
```

Verify it is up:
```bash
curl http://localhost:5000/health
```

### 3. Configure environment variables

Set these on your Paperless-ngx container (e.g. in `docker-compose.yaml` or your systemd unit):

```bash
PAPERLESS_DOCLING_SERVE_URL=http://docling-serve:5000
PAPERLESS_DOCLING_PDF_CONVERSION_MODE=easyocr
```

See the full reference below.

---

## Configuration

### Environment variables

| Variable | Description | Default |
|---|---|---|
| `PAPERLESS_DOCLING_SERVE_URL` | Base URL of the docling-serve API | `http://docling-serve:5000` |
| `PAPERLESS_DOCLING_SERVE_TIMEOUT` | HTTP request timeout in seconds | `300.0` |
| `PAPERLESS_DOCLING_PDF_CONVERSION_MODE` | OCR/pipeline mode (see below) | `easyocr` |
| `PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS` | Maximum status-poll retries | `60` |
| `PAPERLESS_DOCLING_POLL_INTERVAL` | Seconds between status polls | `5.0` |
| `PAPERLESS_DOCLING_OCR_LANGUAGE` | Comma-separated OCR language codes | `eng` |

### Conversion modes

| Mode | Speed | Accuracy | Notes |
|---|---|---|---|
| `easyocr` *(default)* | Medium | Good | Solid multi-language support |
| `tesseract` | Fast | Moderate | Best for clean, simple layouts |
| `granite_docling` | Slow | Excellent | Vision-Language Model pipeline; requires significant GPU resources |

**Example — German + English OCR with Tesseract:**
```bash
PAPERLESS_DOCLING_PDF_CONVERSION_MODE=tesseract
PAPERLESS_DOCLING_OCR_LANGUAGE=deu,eng
```

---

## How the conversion works

Each document goes through a three-step async workflow inside docling-serve:

1. **Submit** — `POST /v1/convert/file/async` uploads the PDF and returns a `task_id`.
2. **Poll** — `GET /v1/status/poll/{task_id}` is called repeatedly (up to `PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS` times, spaced `PAPERLESS_DOCLING_POLL_INTERVAL` seconds apart) until the task succeeds or fails.
3. **Fetch** — `GET /v1/result/{task_id}` retrieves the `DoclingDocument` JSON, which is exported to Markdown and stored in Paperless-ngx.

---

## Troubleshooting

### Verify the plugin is loaded

```bash
pip show pgx-docling-parser-serve
```

### Check docling-serve health

```bash
curl http://<PAPERLESS_DOCLING_SERVE_URL>/health
```

### Common issues

**Connection refused**
- Confirm docling-serve is running and `PAPERLESS_DOCLING_SERVE_URL` is correct.
- If using Docker Compose, make sure both services are on the same network.

**Timeout / polling exhausted**
- Large or complex PDFs take longer. Increase `PAPERLESS_DOCLING_SERVE_TIMEOUT` and `PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS`.
- GPU acceleration significantly reduces processing time.

**Poor OCR quality**
- Switch to `granite_docling` mode for complex layouts, scanned documents, or mixed-script content (requires GPU).
- Make sure `PAPERLESS_DOCLING_OCR_LANGUAGE` includes all languages present in your documents.

---

## Requirements

- Python 3.10 – 3.13
- A running [docling-serve](https://github.com/docling-project/docling-serve) instance
- Paperless-ngx (any recent version)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, branching strategy, coding standards, and the release process.

---

## Links

- [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx)
- [Docling](https://github.com/DS4SD/docling)
- [docling-serve](https://github.com/docling-project/docling-serve)
- [Bug reports & feature requests](https://github.com/T-Eberle/paperless-docling-parser/issues)

---

## License

[MIT](LICENSE)
