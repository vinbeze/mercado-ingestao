from abc import ABC, abstractmethod

from src.domain.entities.receipt import ReceiptHeader
from src.domain.entities.raw_receipt_item import RawReceiptItem


class ReceiptParser(ABC):
    @abstractmethod
    def extract_header(self, html: str) -> ReceiptHeader:
        ...

    @abstractmethod
    def extract_items(self, html: str) -> list[RawReceiptItem]:
        ...
