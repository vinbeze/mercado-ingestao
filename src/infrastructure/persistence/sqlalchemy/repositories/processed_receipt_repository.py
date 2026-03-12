from sqlalchemy.orm import Session

from src.application.dtos.save_processed_receipt_result import SaveProcessedReceiptResult
from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.processed_receipt_repository import ProcessedReceiptRepository


class _ReceiptHeaderModel:
    def __init__(self, header: ReceiptHeader) -> None:
        self.store_name = header.store_name
        self.store_document = header.store_document
        self.purchase_date = header.purchase_date
        self.total_amount = header.total_amount
        self.receipt_number = header.receipt_number


class _NormalizedItemModel:
    def __init__(self, item: NormalizedReceiptItem) -> None:
        self.canonical_name = item.canonical_name
        self.brand = item.brand
        self.category = item.category
        self.quantity = item.quantity
        self.unit = item.unit
        self.unit_price = item.unit_price
        self.total_price = item.total_price


class SqlAlchemyProcessedReceiptRepository(ProcessedReceiptRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        header: ReceiptHeader,
        items: list[NormalizedReceiptItem],
    ) -> SaveProcessedReceiptResult:
        try:
            header_obj = _ReceiptHeaderModel(header)
            self._session.add(header_obj)

            for item in items:
                item_obj = _NormalizedItemModel(item)
                self._session.add(item_obj)

            self._session.commit()
            return SaveProcessedReceiptResult(success=True, items_saved=len(items))
        except Exception:
            self._session.rollback()
            return SaveProcessedReceiptResult(success=False, items_saved=0)
