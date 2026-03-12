from abc import ABC, abstractmethod

from src.application.dtos.save_raw_document_result import SaveRawDocumentResult


class RawDocumentRepository(ABC):
    @abstractmethod
    def save(
        self,
        image_reference: str,
        qr_url: str,
        html: str,
        status: str,
    ) -> SaveRawDocumentResult:
        ...
