"""
Unit tests for the DoclingConverter.

These tests require a running docling-serve instance.
Set the PAPERLESS_DOCLING_SERVE_URL environment variable to point to your instance.
Default: http://docling-serve:5000

To run the tests:
    uv run pytest

To run with a custom docling-serve URL:
    PAPERLESS_DOCLING_SERVE_URL=http://localhost:5000 uv run pytest
"""

import os
import pytest
from pathlib import Path

from pgx_docling import PdfConversionMode
from pgx_docling_serve.serve import DoclingRemoteConverter
from docling_core.types.doc.document import DoclingDocument


@pytest.fixture
def sample_pdf():
    """Get the path to the sample PDF file."""
    pdf_path = Path(__file__).parent / "sample_lorem_ipsum.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")

    return pdf_path


@pytest.fixture
def converter():
    """Create a DoclingRemoteConverter instance."""
    return DoclingRemoteConverter()


class TestDoclingConverter:
    """Unit tests for DoclingConverter — no server required."""

    def test_converter_initialization(self, converter):
        """Test that the converter initializes correctly."""
        assert converter is not None
        assert converter.base_url is not None
        assert converter.timeout > 0
        assert isinstance(converter.pdf_conversion_mode, PdfConversionMode)

    def test_environment_variables(self):
        """Test that environment variables are read correctly."""
        converter = DoclingRemoteConverter()
        assert converter.base_url == os.environ.get(
            "PAPERLESS_DOCLING_SERVE_URL",
            "http://docling-serve:5000"
        )
        assert converter.timeout == float(os.environ.get(
            "PAPERLESS_DOCLING_SERVE_TIMEOUT",
            "300.0"
        ))

    def test_conversion_mode_initialization(self, converter):
        """Test that conversion mode is initialized correctly."""
        assert isinstance(converter.pdf_conversion_mode, PdfConversionMode)
        assert converter.pdf_conversion_mode in [
            PdfConversionMode.EASYOCR,
            PdfConversionMode.TESSERACT,
            PdfConversionMode.GRANITE_DOCLING,
        ]
        print(f"\nConverter initialized with mode: {converter.pdf_conversion_mode.value}")


class TestDoclingConverterIntegration:
    """Integration tests that require a running docling-serve instance."""

    @pytest.mark.integration
    def test_full_conversion_workflow(self, converter, sample_pdf):
        """Test the complete conversion workflow using the default (easyocr) mode."""
        result = converter.convert(sample_pdf)

        assert isinstance(result, DoclingDocument)
        assert result.name is not None
        assert hasattr(result, 'body')
        assert hasattr(result, 'pages')

        print(f"\nFull workflow test completed successfully")
        print(f"Document: {result.name}")
        print(f"Original file: {sample_pdf.name}")
        print(f"Pages: {len(result.pages) if result.pages else 0}")

    @pytest.mark.integration
    def test_tesseract_conversion(self, sample_pdf):
        """Test conversion using the Tesseract OCR preset."""
        os.environ["PAPERLESS_DOCLING_PDF_CONVERSION_MODE"] = "tesseract"
        # Tesseract uses 3-letter ISO 639-2 language codes (e.g. "eng")
        os.environ["PAPERLESS_DOCLING_OCR_LANGUAGE"] = "eng"

        converter = DoclingRemoteConverter()
        assert converter.pdf_conversion_mode == PdfConversionMode.TESSERACT

        result = converter.convert(sample_pdf)

        assert isinstance(result, DoclingDocument)
        assert result.name is not None

        print(f"\nTesseract conversion test completed successfully")
        print(f"Document: {result.name}")
        print(f"Pages: {len(result.pages) if result.pages else 0}")

    @pytest.mark.integration
    def test_granite_docling_conversion(self, sample_pdf):
        """Test conversion using the Granite Docling VLM pipeline."""
        os.environ["PAPERLESS_DOCLING_PDF_CONVERSION_MODE"] = "granite_docling"

        converter = DoclingRemoteConverter()
        assert converter.pdf_conversion_mode == PdfConversionMode.GRANITE_DOCLING

        result = converter.convert(sample_pdf)

        assert isinstance(result, DoclingDocument)
        assert result.name is not None
        assert hasattr(result, 'body')
        assert hasattr(result, 'pages')

        print(f"\nGranite Docling VLM conversion test completed successfully")
        print(f"Document: {result.name}")
        print(f"Pages: {len(result.pages) if result.pages else 0}")
        print(f"Pipeline used: VLM (Vision-Language Model)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
