.PHONY: build-core build-docling-serve build-local build-all clean help

# Build targets
build-core:
	@echo "Building core package..."
	cd packages/core && uv build

build-docling-serve:
	@echo "Building docling-serve package..."
	cd packages/docling_serve && uv build

build-local:
	@echo "Building local package..."
	cd packages/local && uv build

build-all: build-core build-docling-serve build-local
	@echo "All packages built successfully!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf packages/core/dist packages/core/build packages/core/*.egg-info
	rm -rf packages/docling_serve/dist packages/docling_serve/build packages/docling_serve/*.egg-info
	rm -rf packages/local/dist packages/local/build packages/local/*.egg-info
	rm -rf dist build *.egg-info
	@echo "Clean completed!"

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Build targets:"
	@echo "  build-core              - Build the core package"
	@echo "  build-docling-serve     - Build the docling-serve package"
	@echo "  build-local             - Build the local package"
	@echo "  build-all               - Build all packages"
	@echo ""
	@echo "Utility targets:"
	@echo "  clean                   - Remove all build artifacts"
	@echo "  help                    - Show this help message"
	@echo ""
	@echo "Automated Release Process (PRs to main only):"
	@echo "  1. Add exactly ONE version label to your PR to main:"
	@echo "     - version:patch (bug fixes: v0.1.0 → v0.1.1)"
	@echo "     - version:minor (new features: v0.1.0 → v0.2.0)"
	@echo "     - version:major (breaking changes: v0.1.0 → v1.0.0)"
	@echo "  2. Merge PR to main branch"
	@echo "  3. GitHub Actions automatically:"
	@echo "     - Reads the version label"
	@echo "     - Creates appropriate version tag"
	@echo "     - Builds and publishes packages to PyPI"
	@echo "     - Creates GitHub Release with artifacts"
	@echo ""
	@echo "Note: Version labels only required for PRs targeting main branch"

# Made with Bob
