from sqlalchemy.orm import Session

from src.application.dtos.save_raw_document_result import SaveRawDocumentResult
from src.domain.ports.raw_document_repository import RawDocumentRepository


class RawDocumentModel:
    """Placeholder do modelo ORM — será substituído por SQLAlchemy declarativo."""

    def __init__(self) -> None:
        self.id: int | None = None
        self.image_reference: str = ""
        self.qr_url: str = ""
        self.html: str = ""
        self.status: str = ""


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

        obj = RawDocumentModel()
        obj.image_reference = image_reference
        obj.qr_url = qr_url
        obj.html = html
        obj.status = status

        try:
            self._session.add(obj)
            self._session.commit()
            return SaveRawDocumentResult(success=True, document_id=obj.id)
        except Exception:
            self._session.rollback()
            return SaveRawDocumentResult(success=False)
