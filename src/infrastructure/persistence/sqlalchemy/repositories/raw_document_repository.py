from typing import cast

from sqlalchemy.orm import Session

from src.application.dtos.save_raw_document_result import SaveRawDocumentResult
from src.domain.ports.raw_document_repository import RawDocumentRepository
from src.infrastructure.persistence.sqlalchemy.models.models import DocumentRawModel


class SqlAlchemyRawDocumentRepository(RawDocumentRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        image_reference: str,
        qr_url: str,
        html: str,
        status: str,
    ) -> SaveRawDocumentResult:
        if not all([image_reference, qr_url, html, status]):
            raise ValueError("Todos os campos são obrigatórios e não podem ser vazios")

        obj = DocumentRawModel(
            image_reference=image_reference,
            qr_url=qr_url,
            html=html,
            status=status,
        )

        try:
            self._session.add(obj)
            self._session.commit()
            self._session.refresh(obj)
            return SaveRawDocumentResult(success=True, document_id=cast(int, obj.id))
        except Exception:
            self._session.rollback()
            return SaveRawDocumentResult(success=False)
