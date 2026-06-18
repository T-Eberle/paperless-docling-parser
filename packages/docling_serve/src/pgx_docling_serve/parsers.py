from pathlib import Path
from pgx_docling_serve.serve import DoclingRemoteConverter
from pgx_docling.parsers import DoclingParser


class DoclingRemoteParser(DoclingParser):

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

    def __init__(self) -> None:
        super().__init__(converter=DoclingRemoteConverter())