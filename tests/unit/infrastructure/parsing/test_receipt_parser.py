"""
Testes unitários para HtmlReceiptParser.

Testa extract_header e extract_items usando HTML simulado.
Nenhum acesso externo é necessário.
"""

from decimal import Decimal

import pytest

from src.domain.ports.receipt_parser import ReceiptParser
from src.infrastructure.parsing.html_receipt_parser import HtmlReceiptParser


@pytest.fixture
def parser() -> ReceiptParser:
    return HtmlReceiptParser()


# ---------------------------------------------------------------------------
# extract_header
# ---------------------------------------------------------------------------


class TestHtmlReceiptParserExtractHeader:
    def test_extract_header_returns_all_fields_when_html_is_complete(
        self, parser: ReceiptParser, receipt_html_complete: str
    ) -> None:
        header = parser.extract_header(receipt_html_complete)

        assert header.store_name is not None
        assert header.store_document is not None
        assert header.purchase_date is not None
        assert header.total_amount is not None
        assert header.receipt_number is not None

    def test_extract_header_returns_none_for_missing_optional_fields(
        self, parser: ReceiptParser, receipt_html_missing_fields: str
    ) -> None:
        header = parser.extract_header(receipt_html_missing_fields)

        assert header.purchase_date is None
        assert header.receipt_number is None

    def test_extract_header_parses_brazilian_currency_format(
        self, parser: ReceiptParser, receipt_html_complete: str
    ) -> None:
        header = parser.extract_header(receipt_html_complete)

        assert isinstance(header.total_amount, Decimal)
        assert header.total_amount == Decimal("157.83")

    def test_extract_header_handles_empty_html_without_crashing(
        self, parser: ReceiptParser
    ) -> None:
        header = parser.extract_header("")

        assert header.store_name is None
        assert header.total_amount is None

    def test_extract_header_handles_malformed_html_gracefully(
        self, parser: ReceiptParser
    ) -> None:
        malformed = "<html><body><div>Sem fechamento correto<span>abc"

        header = parser.extract_header(malformed)

        # Não deve lançar exceção; campos ausentes retornam None
        assert header is not None


# ---------------------------------------------------------------------------
# extract_items
# ---------------------------------------------------------------------------


class TestHtmlReceiptParserExtractItems:
    def test_extract_items_returns_all_items_correctly(
        self, parser: ReceiptParser, receipt_html_complete: str
    ) -> None:
        items = parser.extract_items(receipt_html_complete)

        assert len(items) == 2

    def test_extract_items_preserves_raw_description(
        self, parser: ReceiptParser, receipt_html_complete: str
    ) -> None:
        items = parser.extract_items(receipt_html_complete)

        descriptions = [i.raw_description for i in items]
        assert "LEITE INTEGRAL ITALAC 1L" in descriptions

    def test_extract_items_fills_line_numbers_correctly(
        self, parser: ReceiptParser, receipt_html_complete: str
    ) -> None:
        items = parser.extract_items(receipt_html_complete)

        line_numbers = [i.line_number for i in items]
        assert line_numbers == sorted(line_numbers)
        assert line_numbers[0] == 1

    def test_extract_items_handles_item_without_unit(
        self, parser: ReceiptParser
    ) -> None:
        html = """
        <html><body>
          <table id="tabResult">
            <tr>
              <td>
                <span class="txtTit">ITEM SEM UNIDADE</span>
                <span class="Rqtd"><strong>Qtde.:</strong>1</span>
                <span class="RvlUnit"><strong>Vl. Unit.:</strong>5,00</span>
              </td>
              <td><span class="valor">5,00</span></td>
            </tr>
          </table>
        </body></html>
        """
        items = parser.extract_items(html)

        assert len(items) == 1
        assert items[0].raw_unit is None

    def test_extract_items_handles_item_without_quantity(
        self, parser: ReceiptParser
    ) -> None:
        html = """
        <html><body>
          <table id="tabResult">
            <tr>
              <td>
                <span class="txtTit">ITEM SEM QUANTIDADE</span>
                <span class="RvlUnit"><strong>Vl. Unit.:</strong>3,50</span>
              </td>
              <td><span class="valor">3,50</span></td>
            </tr>
          </table>
        </body></html>
        """
        items = parser.extract_items(html)

        assert len(items) == 1
        assert items[0].raw_quantity is None

    def test_extract_items_returns_empty_list_when_no_items(
        self, parser: ReceiptParser, receipt_html_without_items: str
    ) -> None:
        items = parser.extract_items(receipt_html_without_items)

        assert items == []

    def test_extract_items_handles_incomplete_html_without_failure(
        self, parser: ReceiptParser
    ) -> None:
        html = "<html><body><p>Conteúdo sem tabela</p></body></html>"

        items = parser.extract_items(html)

        assert isinstance(items, list)
