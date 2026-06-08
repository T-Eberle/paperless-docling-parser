from pgx_docling_serve.serve import DoclingRemoteConverter
from pgx_docling.parsers import DoclingParser


class DoclingRemoteParser(DoclingParser):

    def __init__(self) -> None:
        super().__init__(converter=DoclingRemoteConverter())