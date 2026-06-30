import os
import logging
from pathlib import Path
from docling.datamodel.base_models import OutputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import ProcessingPipeline
from docling.datamodel.service.options import ConvertDocumentsOptions
from docling_core.types.doc.document import DoclingDocument
from docling.service_client import DoclingServiceClient
from docling.service_client.client import StatusWatcherKind

from pgx_docling import BaseDoclingConverter, get_pdf_conversion_mode

# Configure logging
logger = logging.getLogger(__name__)

# Try to import ParseError from paperless-ngx, otherwise define our own
try:
    from documents.parsers import ParseError
except ImportError:
    class ParseError(Exception):
        """Exception raised when document parsing fails."""
        pass


# Environment variable names
PAPERLESS_DOCLING_SERVE_URL = "PAPERLESS_DOCLING_SERVE_URL"
PAPERLESS_DOCLING_SERVE_TIMEOUT = "PAPERLESS_DOCLING_SERVE_TIMEOUT"


def get_docling_serve_url() -> str:
    """Get the docling-serve URL from environment variable."""
    return os.environ.get(PAPERLESS_DOCLING_SERVE_URL, "http://docling-serve:5000")


def get_docling_serve_timeout() -> float:
    """Get the docling-serve timeout from environment variable."""
    try:
        return float(os.environ.get(PAPERLESS_DOCLING_SERVE_TIMEOUT, "300.0"))
    except ValueError:
        return 300.0


class DoclingRemoteConverter(BaseDoclingConverter):
    """Converter that uses docling-serve API for document conversion."""

    def __init__(self, **kwargs):
        """Initialize the converter with configuration from environment variables."""
        self.pdf_conversion_mode = get_pdf_conversion_mode()
        self.base_url = get_docling_serve_url()
        self.timeout = get_docling_serve_timeout()

        logger.info(
            f"DoclingConverter initialized: mode={self.pdf_conversion_mode.value}, "
            f"url={self.base_url}, timeout={self.timeout}s"
        )

    def convert_easyocr(self, document_path: Path) -> DoclingDocument:
        """Convert using EasyOCR preset."""
        return self._convert(document_path, ConvertDocumentsOptions(
            ocr_preset="easyocr",
            ocr_lang=self.ocr_language(),
        ))

    def convert_tesseract(self, document_path: Path) -> DoclingDocument:
        """Convert using Tesseract OCR preset."""
        return self._convert(document_path, ConvertDocumentsOptions(
            ocr_preset="tesseract",
            ocr_lang=self.ocr_language(),
        ))

    def convert_granite_docling(self, document_path: Path) -> DoclingDocument:
        """Convert using Granite Docling VLM pipeline."""
        return self._convert(document_path, ConvertDocumentsOptions(
            pipeline=ProcessingPipeline.VLM,
        ))

    def _convert(self, document_path: Path, options: ConvertDocumentsOptions) -> DoclingDocument:
        """Convert a document using DoclingServiceClient."""
        options.to_formats = [OutputFormat.JSON]
        result: ConversionResult | None = None
        with DoclingServiceClient(
            url=self.base_url,
            status_watcher=StatusWatcherKind.POLLING,
            job_timeout=self.timeout,
        ) as client:
            result = client.convert(source=document_path, options=options)
        if result:
            return result.document
        raise ParseError("Docling document could not be loaded.")
