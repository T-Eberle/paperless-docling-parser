# Project Documentation Rules (Non-Obvious Only)

## Project Structure Context
- `packages/` contains 3 separate packages: core, docling_serve, local (local not yet implemented)
- Root `src/paperless_ngx_docling/` is the main parser plugin that imports from packages
- Packages are linked via editable installs in root `pyproject.toml` `[tool.uv.sources]`

## Converter Architecture (Hidden Complexity)
- `BaseDoclingConverter` defines interface but actual implementation is in `DoclingRemoteConverter`
- Async methods are wrapped with `asyncio.run()` for sync usage (not obvious from signatures)
- Three conversion modes route through single `convert()` method that dispatches internally

## API Integration (Non-Standard Pattern)
- Docling-Serve uses 3-step async workflow (POST → poll → fetch) instead of standard REST
- Polling endpoint is `/v1/status/poll/{task_id}` (not `/v1/tasks/{task_id}/status`)
- Result extraction requires nested dict access: `result["document"]["json_content"]`

## Environment Variable Naming
- All variables use `PAPERLESS_DOCLING_*` prefix (not `DOCLING_*` or `PAPERLESS_*`)
- Mode values are lowercase strings ("easyocr") not uppercase ("EASYOCR")
- Defaults are in Python code, not in config files or environment

## Testing Setup (Non-Obvious Requirements)
- Must use `uv run pytest` (plain `pytest` won't work correctly)
- Integration tests need running docling-serve instance (not mocked)
- Tests verify `DoclingDocument` object structure, not markdown string output

## Package Publishing Workflow
- Build must happen from package directories, not root
- Requires `.env` file with tokens (not environment variables)
- Packages published separately in order: core first, then docling_serve

## Temp Directory Strategy
- Parser tries Django's `SCRATCH_DIR` first (for production)
- Falls back to system temp (for standalone testing)
- Cleanup is automatic via context manager (not manual)