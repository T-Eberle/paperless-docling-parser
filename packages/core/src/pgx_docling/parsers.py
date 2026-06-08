from __future__ import annotations

import shutil
import tempfile
import datetime
import logging

from pathlib import Path
from typing import Self
from types import TracebackType
from typing import TYPE_CHECKING

from docling_core.types.doc.document import DoclingDocument

from pgx_docling.base import BaseDoclingConverter

# Configure logging
logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from types import TracebackType
    #from paperless.parsers import MetadataEntry
    from paperless.parsers import ParserContext

def _make_tempdir() -> Path:
    """Allocate a temp working directory under SCRATCH_DIR if available.

    Falls back to the system temp directory when Django settings are not
    configured (i.e. when running unit tests outside Paperless-ngx).
    """
    parent: Path | None = None
    try:
        from django.conf import settings  # noqa: PLC0415
        scratch = getattr(settings, "SCRATCH_DIR", None)
        if scratch is not None:
            parent = Path(scratch)
            parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Using SCRATCH_DIR for temp directory: {parent}")
    except Exception as e:
        logger.debug(f"Django settings not available, using system temp directory: {e}")
        parent = None

    tempdir = Path(tempfile.mkdtemp(prefix="paperless-ngx-docling-", dir=parent))
    logger.debug(f"Created temp directory: {tempdir}")
    return tempdir

def _date_to_datetime(d: datetime.date | None) -> datetime.datetime | None:
    if d is None:
        return None
    return datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc)

class DoclingParser:
    name = "Docling Parser"
    version = "0.1.0"
    author = "Thomas Eberle"
    url = "https://github.com/T-Eberle/paperless-docling-parser/issues"

    @classmethod
    def supported_mime_types(cls) -> dict[str, str]:
        """Return mapping of supported MIME types to file extensions.
        
        Returns:
            dict[str, str]: Dictionary mapping MIME type strings to their
                corresponding file extensions (including the dot prefix).
        """
        return {
            "application/pdf": ".pdf",
        }

    @classmethod
    def score(cls, mime_type: str, filename: str, path: Path | None = None) -> int | None:
        return 100

    @property
    def can_produce_archive(self) -> bool:
        return False

    @property
    def requires_pdf_rendition(self) -> bool:
        return False


    def __init__(self, logging_group: object = None, converter: BaseDoclingConverter | None = None) -> None:
        logger.info("Initializing DoclingParser")
        self._tempdir = _make_tempdir()
        self._text: str | None = None
        self._archive_path: Path | None = None
        if converter is None:
            raise ValueError("converter parameter is required")
        self.converter = converter
        logger.debug(f"DoclingParser initialized with temp directory: {self._tempdir}")

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        logger.debug(f"Cleaning up temp directory: {self._tempdir}")
        shutil.rmtree(self._tempdir, ignore_errors=True)

    def configure(self, context: ParserContext) -> None:
        pass

    def get_thumbnail(self, document_path: Path, mime_type: str) -> Path:
        logger.debug(f"Generating thumbnail for: {document_path} (mime_type: {mime_type})")
        from PIL import Image, ImageDraw
        out = self._tempdir / "thumb.webp"
        # If it's a PDF, convert the first page to a thumbnail
        if mime_type == "application/pdf":
            try:
                import fitz  # PyMuPDF
                
                # Open the PDF
                pdf_document = fitz.open(document_path)
                
                # Get the first page
                if len(pdf_document) > 0:
                    first_page = pdf_document[0]
                    
                    # Calculate zoom factor to get desired dimensions
                    # Get page dimensions
                    page_rect = first_page.rect
                    page_width = page_rect.width
                    page_height = page_rect.height
                    
                    # Calculate zoom to fit 500x700
                    zoom_x = 500 / page_width
                    zoom_y = 700 / page_height
                    zoom = min(zoom_x, zoom_y)  # Use smaller zoom to fit within bounds
                    
                    # Create transformation matrix
                    mat = fitz.Matrix(zoom, zoom)
                    
                    # Render page to pixmap
                    pix = first_page.get_pixmap(matrix=mat)
                    
                    # Convert pixmap to PIL Image
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                    
                    # Create a new 500x700 white canvas
                    canvas = Image.new("RGB", (500, 700), color="white")
                    
                    # Calculate position to center the image
                    x_offset = (500 - img.width) // 2
                    y_offset = (700 - img.height) // 2
                    
                    # Paste the rendered page onto the canvas
                    canvas.paste(img, (x_offset, y_offset))
                    
                    # Save as WebP
                    canvas.save(out, format="WEBP")
                    
                    pdf_document.close()
                    logger.info(f"Successfully generated PDF thumbnail: {out}")
                    return out
                    
                pdf_document.close()
            except Exception as e:
                # Fall back to placeholder if PDF rendering fails
                logger.warning(f"Failed to generate PDF thumbnail, using placeholder: {e}")
                pass
        
        # Fallback: create a placeholder thumbnail
        logger.debug("Creating placeholder thumbnail")
        img = Image.new("RGB", (500, 700), color="white")
        ImageDraw.Draw(img).text((10, 10), "PDF Document", fill="black")
        img.save(out, format="WEBP")
        return out

    def parse(self, document_path: Path, mime_type: str, *, produce_archive: bool = True) -> None:
        """
        Parse a document using docling-serve API.
        
        Args:
            document_path: Path to the document to parse
            mime_type: MIME type of the document
            produce_archive: Whether to produce an archive (not supported)
        """
        logger.info(f"Parsing document: {document_path} (mime_type: {mime_type})")
        # Use the synchronous wrapper to call the async convert method
        result = self.converter.convert(document_path)
        
        if isinstance(result, DoclingDocument):
            self._text = result.export_to_markdown()
            logger.info(f"Successfully parsed document to markdown, length: {len(self._text)} characters")
        else:
            self._text = str(result)
            logger.warning(f"Result was not a DoclingDocument, converted to string: {type(result)}")


    def get_text(self) -> str | None:
        return self._text

    def get_date(self) -> datetime.datetime | None:
        return None

    def get_archive_path(self) -> Path | None:
        return self._archive_path

    def get_page_count(self, document_path: Path, mime_type: str) -> int | None:
        return None

    def extract_metadata(self, document_path: Path, mime_type: str) -> list:
        return []
