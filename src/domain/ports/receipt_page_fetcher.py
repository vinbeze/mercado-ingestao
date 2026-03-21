from abc import ABC, abstractmethod

from src.application.dtos.fetch_receipt_result import FetchReceiptResult


class ReceiptPageFetcher(ABC):
    @abstractmethod
    def fetch(self, url: str, timeout_seconds: int) -> FetchReceiptResult: ...
