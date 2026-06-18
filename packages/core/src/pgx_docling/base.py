from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path


import os 

from docling_core.types.doc.document import DoclingDocument

PAPERLESS_DOCLING_PDF_CONVERSION_MODE = "PAPERLESS_DOCLING_PDF_CONVERSION_MODE"

class PdfConversionMode(Enum):
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    GRANITE_DOCLING = "granite_docling"


def get_pdf_conversion_mode() -> PdfConversionMode:
    """
    Get the PDF conversion mode from environment variable.
    
    Returns:
        PdfConversionMode: The conversion mode, defaults to EASYOCR if not set or invalid.
    """
    env_value = os.environ.get(PAPERLESS_DOCLING_PDF_CONVERSION_MODE, "").lower()
    
    # Try to match the environment variable value to an enum member
    for mode in PdfConversionMode:
        if mode.value == env_value:
            return mode
    
    # Default to EASYOCR if not set or invalid value
    return PdfConversionMode.EASYOCR

class BaseDoclingConverter(ABC):
    """Base class for all docling converters."""

    def __init__(self) -> None:
        self.pdf_conversion_mode = get_pdf_conversion_mode()
    
    def convert(self, document_path: Path) -> DoclingDocument | None:
        """Convert a document to a DoclingDocument."""
        doc = None
        if self.pdf_conversion_mode == PdfConversionMode.EASYOCR:
            doc= self.convert_easyocr(document_path)
        elif self.pdf_conversion_mode == PdfConversionMode.TESSERACT:
            doc = self.convert_tesseract(document_path)
        elif self.pdf_conversion_mode == PdfConversionMode.GRANITE_DOCLING:
            doc = self.convert_granite_docling(document_path)
        return doc

    def ocr_language(self) -> list[str]:
        """
        Get the OCR language(s) from environment variable.
        
        Returns:
            list[str]: List of language codes, defaults to ['eng'] if not set.
        
        Example:
            PAPERLESS_DOCLING_OCR_LANGUAGE="eng,deu,fra" -> ['eng', 'deu', 'fra']
        """
        env_value = os.environ.get("PAPERLESS_DOCLING_OCR_LANGUAGE", "eng")
        
        # Split by comma and strip whitespace from each language code
        languages = [lang.strip() for lang in env_value.split(",") if lang.strip()]
        
        # Return default if empty after processing
        return languages if languages else ["eng"]



    @abstractmethod
    def convert_easyocr(self, document_path: Path) -> DoclingDocument:
        pass

    @abstractmethod
    def convert_tesseract(self, document_path: Path) -> DoclingDocument:
        pass

    @abstractmethod
    def convert_granite_docling(self, document_path: Path) -> DoclingDocument:
        pass
    

    