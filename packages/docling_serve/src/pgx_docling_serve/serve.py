import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
import httpx
from docling_core.types.doc.document import DoclingDocument

from pgx_docling import BaseDoclingConverter, get_pdf_conversion_mode

# Configure logging
logger = logging.getLogger(__name__)

# Reduce httpx logging verbosity
logging.getLogger("httpx").setLevel(logging.WARNING)

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
PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS = "PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS"
PAPERLESS_DOCLING_POLL_INTERVAL = "PAPERLESS_DOCLING_POLL_INTERVAL"

# Default conversion options
DEFAULT_OPTIONS = {
    "to_formats": "json",  # We need JSON format to get DoclingDocument
    "image_export_mode": "placeholder",
    "force_ocr": True
}


def get_docling_serve_url() -> str:
    """Get the docling-serve URL from environment variable."""
    return os.environ.get(PAPERLESS_DOCLING_SERVE_URL, "http://docling-serve:5000")


def get_docling_serve_timeout() -> float:
    """Get the docling-serve timeout from environment variable."""
    try:
        return float(os.environ.get(PAPERLESS_DOCLING_SERVE_TIMEOUT, "300.0"))
    except ValueError:
        return 300.0


def get_poll_max_attempts() -> int:
    """Get the maximum number of polling attempts from environment variable."""
    try:
        return int(os.environ.get(PAPERLESS_DOCLING_POLL_MAX_ATTEMPTS, "60"))
    except ValueError:
        return 60


def get_poll_interval() -> float:
    """Get the polling interval in seconds from environment variable."""
    try:
        return float(os.environ.get(PAPERLESS_DOCLING_POLL_INTERVAL, "5.0"))
    except ValueError:
        return 5.0


class DoclingRemoteConverter(BaseDoclingConverter):
    """Converter that uses docling-serve API for document conversion."""

    def __init__(self, **kwargs):
        """Initialize the converter with configuration from environment variables."""
        self.pdf_conversion_mode = get_pdf_conversion_mode()
        self.base_url = get_docling_serve_url()
        self.timeout = get_docling_serve_timeout()
        self.poll_max_attempts = get_poll_max_attempts()
        self.poll_interval = get_poll_interval()
        
        logger.info(
            f"DoclingConverter initialized: mode={self.pdf_conversion_mode.value}, "
            f"url={self.base_url}, timeout={self.timeout}s"
        )
    
    def _extract_docling_document(self, result: Dict[str, Any]) -> DoclingDocument:
        """
        Extract and validate DoclingDocument from API result.
        
        Args:
            result: API response containing the document
            
        Returns:
            DoclingDocument: The validated document object
            
        Raises:
            ParseError: If the response structure is invalid
        """
        if "document" not in result or "json_content" not in result["document"]:
            raise ParseError("Invalid response structure from docling-serve: missing json_content")
        
        json_content = result["document"]["json_content"]
        return DoclingDocument.model_validate(json_content)
    
    async def convert_async(self, document_path: Path, options: Dict[str, Any]) -> DoclingDocument:
        """
        Convert a document using docling-serve API.
        
        Workflow:
        1. POST to /v1/convert/file/async to create conversion task
        2. Poll /v1/status/poll/{task_id} until task completes
        3. GET /v1/result/{task_id} to fetch the result
        
        Args:
            document_path: Path to the document to convert
            options: Conversion options (ocr_preset, ocr_lang, pipeline, etc.)
            
        Returns:
            DoclingDocument: The converted document
            
        Raises:
            ParseError: If conversion fails
        """
        logger.info(f"Starting conversion for document: {document_path}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Step 1: Create conversion task
                with open(document_path, "rb") as f:
                    files = {"files": (document_path.name, f, "application/pdf")}
                    data = {**DEFAULT_OPTIONS, **options}
                    
                    logger.debug(f"Posting to {self.base_url}/v1/convert/file/async with options: {data}")
                    response = await client.post(
                        f"{self.base_url}/v1/convert/file/async",
                        files=files,
                        data=data,
                    )
                    response.raise_for_status()
                    
                    task_id = response.json().get("task_id")
                    if not task_id:
                        raise ParseError("No task_id returned from async conversion endpoint")
                    
                    logger.info(f"Conversion task created with ID: {task_id}")
                
                # Step 2: Poll for completion
                for attempt in range(self.poll_max_attempts):
                    response = await client.get(f"{self.base_url}/v1/status/poll/{task_id}")
                    response.raise_for_status()
                    
                    status_data = response.json()
                    task_status = status_data.get("task_status")
                    
                    logger.debug(f"Poll {attempt + 1}/{self.poll_max_attempts} - Task {task_id} status: {task_status}")
                    
                    if task_status == "success":
                        logger.info(f"Task {task_id} completed successfully")
                        break
                    elif task_status == "failure":
                        error_msg = str(status_data.get("task_meta", "Unknown error"))
                        logger.error(f"Task {task_id} failed: {error_msg}")
                        raise ParseError(f"Conversion failed: {error_msg}")
                    
                    # Still processing, wait before next poll
                    await asyncio.sleep(self.poll_interval)
                else:
                    # Loop completed without break (timeout)
                    raise TimeoutError(f"Conversion timed out after {self.poll_max_attempts} polling attempts")
                
                # Step 3: Fetch result
                logger.debug(f"Fetching result for task: {task_id}")
                response = await client.get(f"{self.base_url}/v1/result/{task_id}")
                response.raise_for_status()
                result = response.json()
                
                # Extract and validate DoclingDocument
                doc = self._extract_docling_document(result)
                logger.info(f"Successfully converted document: {document_path}")
                return doc
                
        except ParseError:
            raise
        except Exception as e:
            logger.error(f"Failed to parse {document_path}: {e}", exc_info=True)
            raise ParseError(f"Failed to parse {document_path}") from e
    
    def convert_easyocr(self, document_path: Path) -> DoclingDocument:
        """Convert using EasyOCR preset."""
        return self._convert(document_path, {
            "ocr_preset": "easyocr",
            "ocr_lang": ["en", "de"]
        })
    
    def convert_tesseract(self, document_path: Path) -> DoclingDocument:
        """Convert using Tesseract OCR preset."""
        return self._convert(document_path, {
            "ocr_preset": "tesseract",
            "ocr_lang": ["eng", "deu"]
        })
    
    def convert_granite_docling(self, document_path: Path) -> DoclingDocument:
        """Convert using Granite Docling VLM pipeline."""
        return self._convert(document_path, {
            "pipeline": "vlm"
        })
    
    def _convert(self, document_path: Path, options: Dict[str, Any]) -> DoclingDocument:
        """
        Synchronous wrapper for async conversion.
        
        Args:
            document_path: Path to the document to convert
            options: Conversion options
            
        Returns:
            DoclingDocument: The converted document
        """
        return asyncio.run(self.convert_async(document_path, options))

