# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build & Test Commands

**Build packages (from package directories):**
```bash
cd packages/core && uv build
cd packages/docling_serve && uv build
```

**Run tests:**
```bash
uv run pytest                                    # All tests
uv run pytest tests/test_converter.py          # Specific file
uv run pytest -m integration                    # Integration tests only
uv run pytest tests/test_converter.py::TestDoclingConverter::test_convert_sync  # Single test
```

**Install with dev dependencies:**
```bash
uv sync --extra dev
```

## Non-Obvious Project Patterns

### Monorepo Structure with Editable Installs
- Root `pyproject.toml` uses `[tool.uv.sources]` to reference packages as editable paths
- Packages in `packages/` are separate but linked via editable installs
- Version is determined by git tags using `hatch-vcs`, not a VERSION file

### Versioning and Release Process
- Versions are determined by git tags in format `v{MAJOR}.{MINOR}.{PATCH}`
- All packages (core, docling_serve, local) share the same version from git tags
- Local development without tags uses `0.0.0.dev0+g{git_hash}` format
- Version detection uses `hatch-vcs` plugin with `source = "vcs"`

### Automated Release Workflow (PRs to main only)
1. Developer adds exactly ONE version label to PR targeting `main`: `version:patch`, `version:minor`, or `version:major`
2. `validate-version-label.yml` ensures exactly one version label exists (blocks merge if missing/multiple)
3. When PR is merged to `main`, `tag-and-release.yml` workflow runs with two separate jobs:
   - **Job 1: create-tag** - Reads the label, calculates new version, and creates git tag
   - **Job 2: build-and-publish** - Builds packages, publishes to PyPI, and creates GitHub Release
4. The workflow is idempotent: if a tag already exists, only the build-and-publish job runs
5. Manual reruns are supported via workflow_dispatch with a tag parameter (e.g., `v1.0.0`)

### Version Labels (Required on PRs to main only)
- **`version:patch`** - Bug fixes (v0.1.0 → v0.1.1)
- **`version:minor`** - New features (v0.1.0 → v0.2.0)
- **`version:major`** - Breaking changes (v0.1.0 → v1.0.0)

**Important**:
- Version labels are ONLY required for PRs targeting the `main` branch
- Exactly ONE version label must be present on every PR to main
- The validation workflow will fail if zero or multiple version labels are found
- PRs to other branches (e.g., `dev`) do not require version labels

### Local Development
- No manual version updates needed
- Build commands work without tags (uses fallback version)
- Version is automatically detected from git history

### Converter Architecture
- `BaseDoclingConverter` in `packages/core/src/core/base.py` defines abstract methods for 3 conversion modes
- `DoclingRemoteConverter` in `packages/docling_serve/src/docling_serve/serve.py` implements async HTTP client
- Parser in `src/paperless_ngx_docling/parsers.py` dynamically imports converter based on installed extras

### Async-to-Sync Wrapper Pattern
- `DoclingRemoteConverter.convert_async()` is the core async method containing the full 3-step workflow
- `_convert()` wraps it with `asyncio.run()` for synchronous usage
- Base class `convert()` method routes to mode-specific methods (easyocr/tesseract/granite_docling)

### Docling-Serve API Workflow
The entire workflow is contained in a single `convert_async()` method:
1. POST to `/v1/convert/file/async` returns `task_id`
2. Poll `/v1/status/poll/{task_id}` until status is "success" or "failure"
3. GET `/v1/result/{task_id}` to fetch final result
4. Extract and validate using `_extract_docling_document()` helper method

### Environment Variable Configuration
- All config uses `PAPERLESS_DOCLING_*` prefix (not just `DOCLING_*`)
- `PAPERLESS_DOCLING_PDF_CONVERSION_MODE` must be lowercase enum value: "easyocr", "tesseract", or "granite_docling"
- `PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS` controls maximum polling attempts (default: 60)
- `PAPERLESS_DOCLING_POLL_INTERVAL` controls polling interval in seconds (default: 5.0)
- Defaults are in `packages/docling_serve/src/docling_serve/serve.py` (not in pyproject.toml)

### Temp Directory Handling
- Parser creates temp dir under Django's `SCRATCH_DIR` if available (via `_make_tempdir()`)
- Falls back to system temp if Django settings unavailable (for standalone testing)
- Temp dir is cleaned up in `__exit__` context manager

### Paperless-ngx Integration
- Entry point defined in root `pyproject.toml`: `[project.entry-points."paperless_ngx.parsers"]`
- Parser must implement specific interface: `supported_mime_types()`, `score()`, `parse()`, `get_text()`, etc.
- `score()` returns 100 to prioritize this parser for PDFs

### Testing Requirements
- Integration tests marked with `@pytest.mark.integration` require running docling-serve instance
- Tests use `uv run pytest` (not plain `pytest`) to ensure correct environment
- Sample PDF is in `tests/sample_lorem_ipsum.pdf`
- Tests verify `DoclingDocument` structure, not just string output

### Package Publishing
- Publishing is automated via GitHub Actions in `tag-and-release.yml`
- Workflow has two separate jobs: tag creation and build/publish
- Build/publish job can be manually triggered via workflow_dispatch for existing tags
- This allows rebuilding/republishing without creating a new tag
- Manual publishing: Build commands must be run from package directories (not root)
- Packages are published separately: core first, then docling_serve, then local
- GitHub Actions uses `PYPI_TOKEN` secret for authentication

### Manual Rebuild from Existing Tag
To rebuild and republish an existing release:
1. Go to Actions → "Auto Tag and Publish Release" workflow
2. Click "Run workflow"
3. Enter the existing tag (e.g., `v1.0.0`)
4. The workflow will checkout that tag, build packages, and publish to PyPI