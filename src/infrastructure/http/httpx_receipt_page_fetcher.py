import httpx

from src.application.dtos.fetch_receipt_result import FetchReceiptResult
from src.domain.ports.receipt_page_fetcher import ReceiptPageFetcher


class HttpxReceiptPageFetcher(ReceiptPageFetcher):
    def fetch(self, url: str, timeout_seconds: int) -> FetchReceiptResult:
        raise NotImplementedError
