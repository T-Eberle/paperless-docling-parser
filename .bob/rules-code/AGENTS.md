# Project Coding Rules (Non-Obvious Only)

## Monorepo Package Structure
- Packages in `packages/` use editable installs via `[tool.uv.sources]` in root `pyproject.toml`
- Version comes from root `VERSION` file, not individual package `pyproject.toml` files
- Build commands MUST be run from package directories: `cd packages/core && uv build`

## Converter Implementation Pattern
- All converters inherit from `BaseDoclingConverter` in `packages/core/src/core/base.py`
- Must implement 3 abstract methods: `convert_easyocr()`, `convert_tesseract()`, `convert_granite_docling()`
- Base class `convert()` routes to mode-specific methods based on `PAPERLESS_DOCLING_PDF_CONVERSION_MODE`

## Async-to-Sync Wrapper
- `DoclingRemoteConverter._convert()` wraps async with `asyncio.run()` for sync usage
- Never call `convert_async()` directly from sync code - use `_convert()` or base `convert()`
- Each mode-specific method calls `_convert()` with appropriate options dict

## Docling-Serve API Integration
- API workflow is 3-step: POST async task → poll status → fetch result
- Must extract `result["document"]["json_content"]` and use `DoclingDocument.model_validate()`
- Polling uses `/v1/status/poll/{task_id}` (not standard REST patterns)
- Status values: "success", "failure", or in-progress (poll again)

## Environment Variables
- ALL config uses `PAPERLESS_DOCLING_*` prefix (not `DOCLING_*`)
- `PAPERLESS_DOCLING_PDF_CONVERSION_MODE` must be lowercase: "easyocr", "tesseract", or "granite_docling"
- Defaults defined in `packages/docling_serve/src/docling_serve/serve.py` functions, not config files

## Temp Directory Management
- Parser uses `_make_tempdir()` which tries Django's `SCRATCH_DIR` first, falls back to system temp
- Temp dir cleanup happens in `__exit__` context manager (not `__del__`)
- Never manually delete temp dirs - let context manager handle it

## Paperless-ngx Parser Interface
- Entry point in root `pyproject.toml`: `[project.entry-points."paperless_ngx.parsers"]`
- `score()` must return 100 to prioritize over other PDF parsers
- `parse()` receives `document_path` and `mime_type`, stores result in `self._text`
- `get_text()` returns stored `self._text` (not re-parsing)

## Testing with uv
- ALWAYS use `uv run pytest` (not plain `pytest`) to ensure correct environment
- Integration tests require `@pytest.mark.integration` marker
- Sample PDF path: `tests/sample_lorem_ipsum.pdf`
- Tests verify `DoclingDocument` structure, not string output