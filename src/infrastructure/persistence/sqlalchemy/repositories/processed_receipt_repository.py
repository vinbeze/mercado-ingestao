from sqlalchemy.orm import Session

from src.application.dtos.save_processed_receipt_result import SaveProcessedReceiptResult
from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.processed_receipt_repository import ProcessedReceiptRepository


class SqlAlchemyProcessedReceiptRepository(ProcessedReceiptRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        header: ReceiptHeader,
        items: list[NormalizedReceiptItem],
    ) -> SaveProcessedReceiptResult:
        raise NotImplementedError
