from abc import ABC, abstractmethod

from src.domain.entities.receipt import ReceiptHeader
from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.application.dtos.save_processed_receipt_result import SaveProcessedReceiptResult


class ProcessedReceiptRepository(ABC):
    @abstractmethod
    def save(
        self,
        header: ReceiptHeader,
        items: list[NormalizedReceiptItem],
    ) -> SaveProcessedReceiptResult:
        ...
