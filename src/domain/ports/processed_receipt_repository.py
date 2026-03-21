from abc import ABC, abstractmethod

from src.application.dtos.save_processed_receipt_result import (
    SaveProcessedReceiptResult,
)
from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.receipt import ReceiptHeader


class ProcessedReceiptRepository(ABC):
    @abstractmethod
    def save(
        self,
        header: ReceiptHeader,
        items: list[NormalizedReceiptItem],
    ) -> SaveProcessedReceiptResult: ...
