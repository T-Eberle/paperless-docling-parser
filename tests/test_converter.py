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

from core import PdfConversionMode
from docling_serve.serve import DoclingRemoteConverter
from docling_core.types.doc.document import DoclingDocument


@pytest.fixture
def sample_pdf():
    """Get the path to the sample PDF file."""
    pdf_path = Path(__file__).parent / "sample_lorem_ipsum.pdf"
    
    # Verify the file exists
    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")
    
    return pdf_path


@pytest.fixture
def converter():
    """Create a DoclingRemoteConverter instance."""
    return DoclingRemoteConverter()


class TestDoclingConverter:
    """Test suite for DoclingConverter."""
    
    def test_converter_initialization(self, converter):
        """Test that the converter initializes correctly."""
        assert converter is not None
        assert converter.base_url is not None
        assert converter.timeout > 0
        assert converter.max_retries > 0
        assert isinstance(converter.pdf_conversion_mode, PdfConversionMode)
    
    def test_environment_variables(self):
        """Test that environment variables are read correctly."""
        # Test default values
        converter = DoclingRemoteConverter()
        assert converter.base_url == os.environ.get(
            "PAPERLESS_DOCLING_SERVE_URL", 
            "http://docling-serve:5000"
        )
        assert converter.timeout == float(os.environ.get(
            "PAPERLESS_DOCLING_SERVE_TIMEOUT", 
            "300.0"
        ))
    
    @pytest.mark.asyncio
    async def test_convert_async(self, converter, sample_pdf):
        """Test async conversion of a PDF document."""
        # Prepare conversion options
        options = {}
        
        # Convert the document
        result = await converter.convert_async(sample_pdf, options)
        
        # Verify the result is a DoclingDocument
        assert isinstance(result, DoclingDocument)
        assert result is not None
        
        # Verify the document has expected attributes
        assert hasattr(result, 'name')
        assert hasattr(result, 'body')
        
        # The document should have some content
        assert result.name is not None
        print(f"\nConverted document name: {result.name}")
        print(f"Document has body: {result.body is not None}")
    
    def test_convert_sync(self, converter, sample_pdf):
        """Test synchronous conversion of a PDF document."""
        # Convert the document synchronously using the base class convert method
        result = converter.convert(sample_pdf)
        
        # Verify the result is a DoclingDocument
        assert isinstance(result, DoclingDocument)
        assert result is not None
        
        # Verify the document has expected attributes
        assert hasattr(result, 'name')
        assert hasattr(result, 'body')
        
        print(f"\nConverted document name: {result.name}")
        print(f"Document has body: {result.body is not None}")
    
    def test_conversion_modes(self, sample_pdf, tmp_path):
        """Test different conversion modes."""
        modes = [
            PdfConversionMode.EASYOCR,
            PdfConversionMode.TESSERACT,
            PdfConversionMode.GRANITE_DOCLING
        ]
        
        for mode in modes:
            # Set the mode via environment variable
            os.environ["PAPERLESS_DOCLING_PDF_CONVERSION_MODE"] = mode.value
            
            # Create a new converter with the mode
            converter = DoclingRemoteConverter()
            assert converter.pdf_conversion_mode == mode
            
            # Test conversion using the base class convert method
            result = converter.convert(sample_pdf)
            assert isinstance(result, DoclingDocument)
            
            print(f"\nMode {mode.value}: Successfully converted document")
    
    def test_conversion_mode_initialization(self, converter):
        """Test that conversion mode is initialized correctly."""
        # Verify the converter has a valid conversion mode
        assert isinstance(converter.pdf_conversion_mode, PdfConversionMode)
        
        # Verify the mode is one of the valid options
        assert converter.pdf_conversion_mode in [
            PdfConversionMode.EASYOCR,
            PdfConversionMode.TESSERACT,
            PdfConversionMode.GRANITE_DOCLING
        ]
        
        print(f"\nConverter initialized with mode: {converter.pdf_conversion_mode.value}")


class TestDoclingConverterIntegration:
    """Integration tests that require a running docling-serve instance."""
    
    @pytest.mark.integration
    def test_full_conversion_workflow(self, converter, sample_pdf):
        """
        Test the complete conversion workflow:
        1. Trigger async conversion
        2. Poll for status
        3. Fetch result
        4. Convert to DoclingDocument
        """
        # This test verifies the entire workflow
        result = converter.convert(sample_pdf)
        
        # Verify we got a valid DoclingDocument
        assert isinstance(result, DoclingDocument)
        # Note: The document name might be generic ("Document") rather than the filename
        assert result.name is not None
        
        # Verify the document structure
        assert hasattr(result, 'body')
        assert hasattr(result, 'pages')
        
        print(f"\nFull workflow test completed successfully")
        print(f"Document: {result.name}")
        print(f"Original file: {sample_pdf.name}")
        print(f"Pages: {len(result.pages) if result.pages else 0}")


    @pytest.mark.integration
    def test_granite_docling_conversion(self, sample_pdf):
        """
        Test conversion specifically with Granite Docling VLM pipeline.
        This uses the vision-language model for document understanding.
        """
        # Set the mode to GRANITE_DOCLING
        os.environ["PAPERLESS_DOCLING_PDF_CONVERSION_MODE"] = "granite_docling"
        
        # Create a new converter with the VLM mode
        converter = DoclingRemoteConverter()
        assert converter.pdf_conversion_mode == PdfConversionMode.GRANITE_DOCLING
        
        # Test conversion with VLM pipeline using the base class convert method
        result = converter.convert(sample_pdf)
        
        # Verify we got a valid DoclingDocument
        assert isinstance(result, DoclingDocument)
        assert result.name is not None
        
        # Verify the document structure
        assert hasattr(result, 'body')
        assert hasattr(result, 'pages')
        
        print(f"\nGranite Docling VLM conversion test completed successfully")
        print(f"Document: {result.name}")
        print(f"Pages: {len(result.pages) if result.pages else 0}")
        print(f"Pipeline used: VLM (Vision-Language Model)")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])