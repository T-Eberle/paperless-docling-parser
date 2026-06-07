.PHONY: build-core build-docling-serve build-all upload-test-core upload-test-docling-serve upload-test-all clean

# Load environment variables from .env file
include .env
export

# Build targets
build-core:
	@echo "Building core package..."
	cd packages/core && uv build

build-docling-serve:
	@echo "Building docling-serve package..."
	cd packages/docling_serve && uv build

build-all: build-core build-docling-serve
	@echo "All packages built successfully!"

# Upload to Test PyPI targets
upload-test-core:
	@echo "Uploading core package to Test PyPI..."
	cd packages/core && UV_PUBLISH_TOKEN=$(TESTPYPI_TOKEN) uv publish --publish-url https://test.pypi.org/legacy/

upload-test-docling-serve:
	@echo "Uploading docling-serve package to Test PyPI..."
	cd packages/docling_serve && UV_PUBLISH_TOKEN=$(TESTPYPI_TOKEN) uv publish --publish-url https://test.pypi.org/legacy/

upload-test-all: upload-test-core upload-test-docling-serve
	@echo "All packages uploaded to Test PyPI successfully!"

# Combined build and upload for Test PyPI
build-and-upload-test: build-all upload-test-all
	@echo "Build and upload to Test PyPI completed!"

# Upload to Production PyPI targets
upload-prod-core:
	@echo "Uploading core package to Production PyPI..."
	cd packages/core && UV_PUBLISH_TOKEN=$(PYPI_TOKEN) uv publish

upload-prod-docling-serve:
	@echo "Uploading docling-serve package to Production PyPI..."
	cd packages/docling_serve && UV_PUBLISH_TOKEN=$(PYPI_TOKEN) uv publish

upload-prod-all: upload-prod-core upload-prod-docling-serve
	@echo "All packages uploaded to Production PyPI successfully!"

# Combined build and upload for Production PyPI
build-and-upload-prod: build-all upload-prod-all
	@echo "Build and upload to Production PyPI completed!"

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
	@echo "  build-all               - Build all packages"
	@echo ""
	@echo "Test PyPI targets:"
	@echo "  upload-test-core        - Upload core package to Test PyPI"
	@echo "  upload-test-docling-serve - Upload docling-serve package to Test PyPI"
	@echo "  upload-test-all         - Upload all packages to Test PyPI"
	@echo "  build-and-upload-test   - Build and upload all packages to Test PyPI"
	@echo ""
	@echo "Production PyPI targets:"
	@echo "  upload-prod-core        - Upload core package to Production PyPI"
	@echo "  upload-prod-docling-serve - Upload docling-serve package to Production PyPI"
	@echo "  upload-prod-all         - Upload all packages to Production PyPI"
	@echo "  build-and-upload-prod   - Build and upload all packages to Production PyPI"
	@echo ""
	@echo "Utility targets:"
	@echo "  clean                   - Remove all build artifacts"
	@echo "  help                    - Show this help message"

