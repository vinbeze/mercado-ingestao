import httpx

from src.application.dtos.fetch_receipt_result import FetchReceiptResult
from src.domain.ports.receipt_page_fetcher import ReceiptPageFetcher


class HttpxReceiptPageFetcher(ReceiptPageFetcher):
    def fetch(self, url: str, timeout_seconds: int) -> FetchReceiptResult:
        try:
            response = httpx.get(url, timeout=timeout_seconds, follow_redirects=True)
            success = response.status_code == 200
            return FetchReceiptResult(
                success=success,
                status_code=response.status_code,
                html=response.text if success else None,
                final_url=str(response.url),
                error=None if success else f"HTTP {response.status_code}",
            )
        except httpx.TimeoutException as exc:
            return FetchReceiptResult(success=False, error=f"Timeout: {exc}")
        except httpx.InvalidURL as exc:
            return FetchReceiptResult(success=False, error=f"URL inválida: {exc}")
        except Exception as exc:
            return FetchReceiptResult(success=False, error=str(exc))
