from sqlalchemy.orm import Session

from src.application.dtos.save_processed_receipt_result import (
    SaveProcessedReceiptResult,
)
from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.processed_receipt_repository import ProcessedReceiptRepository
from src.infrastructure.persistence.sqlalchemy.models.models import (
    PurchaseItemNormalizedModel,
    PurchaseReceiptModel,
)


class SqlAlchemyProcessedReceiptRepository(ProcessedReceiptRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        header: ReceiptHeader,
        items: list[NormalizedReceiptItem],
    ) -> SaveProcessedReceiptResult:
        try:
            receipt = PurchaseReceiptModel(
                store_name=header.store_name,
                store_document=header.store_document,
                purchase_date=header.purchase_date,
                total_amount=header.total_amount,
                receipt_number=header.receipt_number,
            )
            self._session.add(receipt)
            self._session.flush()

            for item in items:
                item_obj = PurchaseItemNormalizedModel(
                    receipt_id=receipt.id,
                    canonical_name=item.canonical_name,
                    brand=item.brand,
                    category=item.category,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                )
                self._session.add(item_obj)

            self._session.commit()
            self._session.refresh(receipt)
            return SaveProcessedReceiptResult(
                success=True, receipt_id=receipt.id, items_saved=len(items)
            )
        except Exception:
            self._session.rollback()
            return SaveProcessedReceiptResult(success=False, items_saved=0)
