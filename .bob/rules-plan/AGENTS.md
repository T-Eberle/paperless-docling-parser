# Project Architecture Rules (Non-Obvious Only)

## Monorepo Architecture
- Three packages with circular dependency on core (intentional design)
- Editable installs via `[tool.uv.sources]` enable local development without reinstalls
- Version centralized in root `VERSION` file to maintain consistency across packages

## Converter Pattern (Hidden Abstraction)
- `BaseDoclingConverter` enforces 3-mode interface but doesn't implement conversion
- Mode selection happens at runtime via environment variable, not compile time
- Async implementation wrapped for sync usage (hidden from callers)

## API Integration Architecture
- Non-standard 3-step async workflow required by docling-serve API design
- Polling mechanism needed because conversion is long-running (not instant)
- Result structure deeply nested: must navigate to `["document"]["json_content"]`

## Parser Plugin Architecture
- Entry point system allows Paperless-ngx to discover parser automatically
- `score()` method determines parser priority (100 = highest for PDFs)
- Parser stores state between `parse()` and `get_text()` calls (not stateless)

## Temp Directory Strategy
- Django integration requires checking for `SCRATCH_DIR` setting
- Fallback to system temp enables standalone testing outside Paperless-ngx
- Context manager pattern ensures cleanup even on exceptions

## Testing Architecture
- Integration tests require external service (docling-serve) running
- Tests verify Pydantic model structure, not just string content
- `uv run` required to ensure correct package resolution in monorepo

## Package Publishing Constraints
- Build must happen in package directories due to relative path references
- Publishing order matters: core must be published before docling_serve
- Tokens stored in `.env` file (not CI environment) for local publishing