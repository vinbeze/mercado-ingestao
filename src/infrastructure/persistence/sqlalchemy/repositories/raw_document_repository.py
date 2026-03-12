from sqlalchemy.orm import Session

from src.application.dtos.save_raw_document_result import SaveRawDocumentResult
from src.domain.ports.raw_document_repository import RawDocumentRepository


class RawDocumentModel:
    """Placeholder do modelo ORM — será definido com SQLAlchemy Base na implementação real."""
    id: int | None = None
    image_reference: str = ""
    qr_url: str = ""
    html: str = ""
    status: str = ""


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
        raise NotImplementedError
