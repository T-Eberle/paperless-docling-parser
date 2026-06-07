import os
import asyncio
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from docling_core.types.doc.document import DoclingDocument

from core import BaseDoclingConverter, PdfConversionMode, get_pdf_conversion_mode

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





PAPERLESS_DOCLING_SERVE_URL = "PAPERLESS_DOCLING_SERVE_URL"
PAPERLESS_DOCLING_SERVE_TIMEOUT = "PAPERLESS_DOCLING_SERVE_TIMEOUT"
PAPERLESS_DOCLING_SERVE_MAX_RETRIES = "PAPERLESS_DOCLING_SERVE_MAX_RETRIES"



DEFAULT_OPTIONS = {
            "to_formats": "json", # We need JSON format to get DoclingDocument
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


def get_docling_serve_max_retries() -> int:
    """Get the maximum number of retries for docling-serve API calls."""
    try:
        return int(os.environ.get(PAPERLESS_DOCLING_SERVE_MAX_RETRIES, "3"))
    except ValueError:
        return 3


class DoclingRemoteConverter(BaseDoclingConverter):
    """Async converter that uses docling-serve API."""

    def __init__(self, **kwargs):
        # Get conversion mode from environment variable
        self.pdf_conversion_mode = get_pdf_conversion_mode()
        self.base_url = get_docling_serve_url()
        self.timeout = get_docling_serve_timeout()
        self.max_retries = get_docling_serve_max_retries()
        
        logger.info(
            f"DoclingConverter initialized: mode={self.pdf_conversion_mode.value}, "
            f"url={self.base_url}, timeout={self.timeout}s, max_retries={self.max_retries}"
        )
        
    async def convert_async(self, document_path: Path,options: Dict[str,Any]) -> DoclingDocument:
        """
        Convert a document using docling-serve API.
        
        Args:
            document_path: Path to the document to convert
            
        Returns:
            DoclingDocument: The converted document as a DoclingDocument object
            
        Raises:
            ParseError: If conversion fails after retries
        """
        logger.info(f"Starting conversion for document: {document_path}")
        try:
            # Get the task result which contains the document
            result = await self._convert_with_retry(document_path,options)
            
            # Extract json_content from the result and convert to DoclingDocument
            # The result structure is: {"document": {"json_content": {...}, ...}, ...}
            if "document" in result and "json_content" in result["document"]:
                json_content = result["document"]["json_content"]
                # Convert dict to DoclingDocument using Pydantic's model_validate
                doc = DoclingDocument.model_validate(json_content)
                logger.info(f"Successfully converted document: {document_path}")
                return doc
            else:
                logger.error(f"Invalid response structure from docling-serve: missing json_content")
                raise ParseError(f"Invalid response structure from docling-serve: missing json_content")
                
        except Exception as e:
            logger.error(f"Failed to parse {document_path}: {e}", exc_info=True)
            raise ParseError(f"Failed to parse {document_path}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _convert_with_retry(self, document_path: Path, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert document with automatic retry on network errors.
        Uses the async API endpoint and polls for completion.
        
        Args:
            document_path: Path to the document to convert
            
        Returns:
            Dict containing the conversion result
        """
        logger.debug(f"Starting conversion with retry for: {document_path}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Step 1: Trigger async conversion task using /v1/convert/file/async
            with open(document_path, "rb") as f:
                files = {"files": (document_path.name, f, "application/pdf")}
                
                # Prepare conversion options based on mode
                # Merge DEFAULT_OPTIONS with options, options will override defaults
                data = {**DEFAULT_OPTIONS, **options}
                logger.debug(f"Conversion options: {data}")
                
                # Make the API call to docling-serve async endpoint
                logger.debug(f"Posting to {self.base_url}/v1/convert/file/async")
                response = await client.post(
                    f"{self.base_url}/v1/convert/file/async",
                    files=files,
                    data=data,
                )
                
                response.raise_for_status()
                
                # Parse the response to get task_id
                task_response = response.json()
                task_id = task_response.get("task_id")
                
                if not task_id:
                    logger.error("No task_id returned from async conversion endpoint")
                    raise Exception("No task_id returned from async conversion endpoint")
                
                logger.info(f"Conversion task created with ID: {task_id}")
            
            # Step 2: Poll for task completion
            await self._poll_for_result(client, task_id)
            
            # Step 3: Fetch the result
            result = await self._fetch_task_result(client, task_id)
            
            logger.debug(f"Conversion completed for task: {task_id}")
            return result
    
    async def _poll_for_result(self, client: httpx.AsyncClient, task_id: str) -> None:
        """
        Poll for task completion using /v1/status/poll/{task_id}.
        
        Args:
            client: HTTP client to use
            task_id: Task ID to poll for
            
        Raises:
            Exception: If task fails or times out
        """
        max_polls = 60  # Maximum number of polls (5 minutes with 5 second intervals)
        poll_interval = 5  # seconds
        
        logger.debug(f"Starting to poll for task: {task_id}")
        for poll_count in range(max_polls):
            response = await client.get(
                f"{self.base_url}/v1/status/poll/{task_id}"
            )
            response.raise_for_status()
            
            status_data = response.json()
            task_status = status_data.get("task_status")
            
            logger.debug(f"Poll {poll_count + 1}/{max_polls} - Task {task_id} status: {task_status}")
            
            if task_status == "success":
                # Task completed successfully
                logger.info(f"Task {task_id} completed successfully")
                return
            elif task_status == "failure":
                # Extract error information from task metadata if available
                error_msg = "Unknown error"
                if "task_meta" in status_data:
                    error_msg = str(status_data["task_meta"])
                logger.error(f"Task {task_id} failed: {error_msg}")
                raise Exception(f"Conversion failed: {error_msg}")
            
            # If status is still pending/processing, continue polling
            # Client-side sleep between poll requests
            await asyncio.sleep(poll_interval)
        
        logger.error(f"Task {task_id} timed out after {max_polls} polls")
        raise TimeoutError(f"Conversion timed out after polling for task {task_id}")
    
    async def _fetch_task_result(self, client: httpx.AsyncClient, task_id: str) -> Dict[str, Any]:
        """
        Fetch the task result using /v1/result/{task_id}.
        
        Args:
            client: HTTP client to use
            task_id: Task ID to fetch result for
            
        Returns:
            Dict containing the conversion result
        """
        logger.debug(f"Fetching result for task: {task_id}")
        response = await client.get(f"{self.base_url}/v1/result/{task_id}")
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"Successfully fetched result for task: {task_id}")
        return result
    
    def convert_easyocr(self, document_path: Path) -> DoclingDocument:
        options: Dict[str, Any] = {}
        options["ocr_preset"] = "easyocr"
        options["ocr_lang"] = ["en", "de"]
        return self._convert(document_path, options)
    
    def convert_tesseract(self, document_path: Path) -> DoclingDocument:
        options: Dict[str, Any] = {}
        options["ocr_preset"] = "tesseract"
        options["ocr_lang"] = ["eng","deu"]
        return self._convert(document_path, options)
    
    def convert_granite_docling(self, document_path: Path) -> DoclingDocument:
        options: Dict[str, Any] = {}
        options["pipeline"] = "vlm"
        return self._convert(document_path, options)
    
    def _convert(self, document_path: Path, options: Dict[str, Any]) -> DoclingDocument:
        """
        Synchronous wrapper for convert method.
        
        Args:
            document_path: Path to the document to convert
            
        Returns:
            DoclingDocument: The converted document
        """
        logger.debug(f"Starting synchronous conversion for: {document_path}")
        # Use asyncio.run which creates a new event loop
        return asyncio.run(self.convert_async(document_path, options))

