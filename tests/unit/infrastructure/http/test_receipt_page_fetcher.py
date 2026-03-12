"""
Testes unitários para HttpxReceiptPageFetcher.

httpx.Client é mockado para evitar acesso real à rede.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.domain.ports.receipt_page_fetcher import ReceiptPageFetcher
from src.infrastructure.http.httpx_receipt_page_fetcher import HttpxReceiptPageFetcher


@pytest.fixture
def fetcher() -> ReceiptPageFetcher:
    return HttpxReceiptPageFetcher()


class TestHttpxReceiptPageFetcherFetch:
    def test_fetch_returns_success_on_http_200(self, fetcher: ReceiptPageFetcher) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>nota</html>"
        mock_response.url = "https://sefaz.rs.gov.br/nfce?chNFe=1"

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   return_value=mock_response):
            result = fetcher.fetch("https://sefaz.rs.gov.br/nfce?chNFe=1", timeout_seconds=10)

        assert result.success is True

    def test_fetch_returns_html_on_success(self, fetcher: ReceiptPageFetcher) -> None:
        html_content = "<html><body>Nota Fiscal</body></html>"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.url = "https://sefaz.rs.gov.br/nfce?chNFe=1"

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   return_value=mock_response):
            result = fetcher.fetch("https://sefaz.rs.gov.br/nfce?chNFe=1", timeout_seconds=10)

        assert result.html == html_content

    def test_fetch_handles_timeout_without_raising_unhandled_exception(
        self, fetcher: ReceiptPageFetcher
    ) -> None:
        import httpx as httpx_lib

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   side_effect=httpx_lib.TimeoutException("timeout")):
            result = fetcher.fetch("https://sefaz.rs.gov.br/nfce?chNFe=1", timeout_seconds=1)

        assert result.success is False
        assert result.error is not None

    def test_fetch_handles_404_response(self, fetcher: ReceiptPageFetcher) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.url = "https://sefaz.rs.gov.br/nfce?chNFe=1"

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   return_value=mock_response):
            result = fetcher.fetch("https://sefaz.rs.gov.br/nfce?chNFe=1", timeout_seconds=10)

        assert result.success is False
        assert result.status_code == 404

    def test_fetch_handles_500_response(self, fetcher: ReceiptPageFetcher) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.url = "https://sefaz.rs.gov.br/nfce?chNFe=1"

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   return_value=mock_response):
            result = fetcher.fetch("https://sefaz.rs.gov.br/nfce?chNFe=1", timeout_seconds=10)

        assert result.success is False
        assert result.status_code == 500

    def test_fetch_captures_redirect_and_fills_final_url(
        self, fetcher: ReceiptPageFetcher
    ) -> None:
        original_url = "http://sefaz.rs.gov.br/nfce?chNFe=1"
        redirected_url = "https://sefaz.rs.gov.br/nfce?chNFe=1"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>nota</html>"
        mock_response.url = redirected_url

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   return_value=mock_response):
            result = fetcher.fetch(original_url, timeout_seconds=10)

        assert result.final_url == redirected_url

    def test_fetch_fails_gracefully_for_invalid_url(
        self, fetcher: ReceiptPageFetcher
    ) -> None:
        import httpx as httpx_lib

        with patch("src.infrastructure.http.httpx_receipt_page_fetcher.httpx.get",
                   side_effect=httpx_lib.InvalidURL("URL inválida")):
            result = fetcher.fetch("nao_e_uma_url", timeout_seconds=10)

        assert result.success is False
        assert result.error is not None
