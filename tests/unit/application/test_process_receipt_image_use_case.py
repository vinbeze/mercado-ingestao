"""
Testes unitários para ProcessReceiptImageUseCase.

Todos os ports são mockados via pytest-mock.
Valida-se a orquestração do fluxo, a ordem de chamadas e a composição do resultado.
"""

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

from src.application.dtos.fetch_receipt_result import FetchReceiptResult
from src.application.dtos.process_receipt_command import ProcessReceiptCommand
from src.application.dtos.qr_decode_result import QRDecodeResult
from src.application.dtos.save_processed_receipt_result import (
    SaveProcessedReceiptResult,
)
from src.application.dtos.save_raw_document_result import SaveRawDocumentResult
from src.application.dtos.url_validation_result import URLValidationResult
from src.application.use_cases.process_receipt_image_use_case import (
    ProcessReceiptImageUseCase,
)
from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.entities.receipt import ReceiptHeader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_use_case(
    qr_reader: Any = None,
    url_validator: Any = None,
    page_fetcher: Any = None,
    parser: Any = None,
    normalizer: Any = None,
    raw_doc_repo: Any = None,
    processed_repo: Any = None,
) -> ProcessReceiptImageUseCase:
    return ProcessReceiptImageUseCase(
        qr_reader=qr_reader or MagicMock(),
        url_validator=url_validator or MagicMock(),
        page_fetcher=page_fetcher or MagicMock(),
        parser=parser or MagicMock(),
        normalizer=normalizer or MagicMock(),
        raw_doc_repository=raw_doc_repo or MagicMock(),
        processed_repository=processed_repo or MagicMock(),
    )


def _default_command() -> ProcessReceiptCommand:
    return ProcessReceiptCommand(
        image_bytes=b"\xff\xd8\xff\xe0fake_image",
        content_type="image/jpeg",
    )


def _valid_raw_items() -> list[RawReceiptItem]:
    return [
        RawReceiptItem(
            line_number=1,
            raw_description="LEITE INTEGRAL 1L",
            raw_quantity="2",
            raw_unit="UN",
            unit_price=Decimal("4.99"),
            total_price=Decimal("9.98"),
        )
    ]


def _valid_normalized_items() -> list[NormalizedReceiptItem]:
    return [
        NormalizedReceiptItem(
            canonical_name="Leite Integral",
            brand="Italac",
            category="Laticínios",
            quantity=Decimal("2"),
            unit="UN",
            unit_price=Decimal("4.99"),
            total_price=Decimal("9.98"),
        )
    ]


def _valid_header() -> ReceiptHeader:
    return ReceiptHeader(
        store_name="Supermercado Teste",
        store_document="12.345.678/0001-90",
        purchase_date="01/03/2026",
        total_amount=Decimal("9.98"),
        receipt_number="000001",
    )


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestProcessReceiptImageUseCaseExecute:
    def test_execute_completes_full_flow_when_all_steps_succeed(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=True, raw_value="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )

        url_validator = MagicMock()
        url_validator.validate.return_value = URLValidationResult(
            is_valid=True, normalized_url="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )

        page_fetcher = MagicMock()
        page_fetcher.fetch.return_value = FetchReceiptResult(
            success=True,
            status_code=200,
            html="<html>nota</html>",
            final_url="https://sefaz.rs.gov.br/nfce?chNFe=1",
        )

        parser = MagicMock()
        parser.extract_header.return_value = _valid_header()
        parser.extract_items.return_value = _valid_raw_items()

        normalizer = MagicMock()
        normalizer.normalize_item.return_value = _valid_normalized_items()[0]

        raw_doc_repo = MagicMock()
        raw_doc_repo.save.return_value = SaveRawDocumentResult(
            success=True, document_id=1
        )

        processed_repo = MagicMock()
        processed_repo.save.return_value = SaveProcessedReceiptResult(
            success=True, receipt_id=10, items_saved=1
        )

        use_case = _make_use_case(
            qr_reader=qr_reader,
            url_validator=url_validator,
            page_fetcher=page_fetcher,
            parser=parser,
            normalizer=normalizer,
            raw_doc_repo=raw_doc_repo,
            processed_repo=processed_repo,
        )

        result = use_case.execute(_default_command())

        assert result.success is True
        assert result.items_count == 1
        assert result.document_id == 1
        assert result.receipt_id == 10
        assert result.errors == []

    def test_execute_stops_when_qr_not_found(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=False, error="QR Code não encontrado na imagem"
        )

        url_validator = MagicMock()
        page_fetcher = MagicMock()
        parser = MagicMock()
        raw_doc_repo = MagicMock()
        processed_repo = MagicMock()

        use_case = _make_use_case(
            qr_reader=qr_reader,
            url_validator=url_validator,
            page_fetcher=page_fetcher,
            parser=parser,
            raw_doc_repo=raw_doc_repo,
            processed_repo=processed_repo,
        )

        result = use_case.execute(_default_command())

        assert result.success is False
        assert len(result.errors) > 0
        url_validator.validate.assert_not_called()
        page_fetcher.fetch.assert_not_called()
        parser.extract_header.assert_not_called()

    def test_execute_stops_when_url_is_invalid(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=True, raw_value="TEXTO_NAO_URL"
        )

        url_validator = MagicMock()
        url_validator.validate.return_value = URLValidationResult(
            is_valid=False, error="Valor não é uma URL válida"
        )

        page_fetcher = MagicMock()
        parser = MagicMock()

        use_case = _make_use_case(
            qr_reader=qr_reader,
            url_validator=url_validator,
            page_fetcher=page_fetcher,
            parser=parser,
        )

        result = use_case.execute(_default_command())

        assert result.success is False
        assert len(result.errors) > 0
        page_fetcher.fetch.assert_not_called()
        parser.extract_header.assert_not_called()

    def test_execute_stops_when_html_fetch_fails(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=True, raw_value="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )

        url_validator = MagicMock()
        url_validator.validate.return_value = URLValidationResult(
            is_valid=True, normalized_url="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )

        page_fetcher = MagicMock()
        page_fetcher.fetch.return_value = FetchReceiptResult(
            success=False, status_code=404, error="Página não encontrada"
        )

        parser = MagicMock()

        use_case = _make_use_case(
            qr_reader=qr_reader,
            url_validator=url_validator,
            page_fetcher=page_fetcher,
            parser=parser,
        )

        result = use_case.execute(_default_command())

        assert result.success is False
        assert len(result.errors) > 0
        parser.extract_header.assert_not_called()

    def test_execute_handles_individual_item_normalization_error(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=True, raw_value="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )
        url_validator = MagicMock()
        url_validator.validate.return_value = URLValidationResult(
            is_valid=True, normalized_url="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )
        page_fetcher = MagicMock()
        page_fetcher.fetch.return_value = FetchReceiptResult(
            success=True,
            status_code=200,
            html="<html>nota</html>",
            final_url="https://sefaz.rs.gov.br/nfce?chNFe=1",
        )
        parser = MagicMock()
        parser.extract_header.return_value = _valid_header()
        parser.extract_items.return_value = _valid_raw_items()

        normalizer = MagicMock()
        normalizer.normalize_item.side_effect = ValueError("Falha ao normalizar item")

        raw_doc_repo = MagicMock()
        raw_doc_repo.save.return_value = SaveRawDocumentResult(
            success=True, document_id=1
        )
        processed_repo = MagicMock()
        processed_repo.save.return_value = SaveProcessedReceiptResult(
            success=True, receipt_id=10, items_saved=0
        )

        use_case = _make_use_case(
            qr_reader=qr_reader,
            url_validator=url_validator,
            page_fetcher=page_fetcher,
            parser=parser,
            normalizer=normalizer,
            raw_doc_repo=raw_doc_repo,
            processed_repo=processed_repo,
        )

        result = use_case.execute(_default_command())

        # O fluxo pode continuar mesmo com erro em item individual,
        # mas o erro deve ser registrado
        assert len(result.errors) > 0

    def test_execute_consolidates_error_messages_in_errors_field(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=False, error="Imagem sem QR Code"
        )

        use_case = _make_use_case(qr_reader=qr_reader)
        result = use_case.execute(_default_command())

        assert isinstance(result.errors, list)
        assert any(
            "QR" in e or "qr" in e.lower() or "imagem" in e.lower()
            for e in result.errors
        )

    def test_execute_returns_items_count_consistent_with_processed_items(self) -> None:
        qr_reader = MagicMock()
        qr_reader.decode.return_value = QRDecodeResult(
            found=True, raw_value="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )
        url_validator = MagicMock()
        url_validator.validate.return_value = URLValidationResult(
            is_valid=True, normalized_url="https://sefaz.rs.gov.br/nfce?chNFe=1"
        )
        page_fetcher = MagicMock()
        page_fetcher.fetch.return_value = FetchReceiptResult(
            success=True,
            status_code=200,
            html="<html>nota</html>",
            final_url="https://sefaz.rs.gov.br/nfce?chNFe=1",
        )

        two_raw_items = [
            RawReceiptItem(
                line_number=1,
                raw_description="ITEM A",
                raw_quantity="1",
                raw_unit="UN",
                unit_price=Decimal("1.00"),
                total_price=Decimal("1.00"),
            ),
            RawReceiptItem(
                line_number=2,
                raw_description="ITEM B",
                raw_quantity="2",
                raw_unit="UN",
                unit_price=Decimal("2.00"),
                total_price=Decimal("4.00"),
            ),
        ]
        parser = MagicMock()
        parser.extract_header.return_value = _valid_header()
        parser.extract_items.return_value = two_raw_items

        normalizer = MagicMock()
        normalizer.normalize_item.return_value = NormalizedReceiptItem(
            canonical_name="Item Genérico",
            quantity=Decimal("1"),
            unit="UN",
            unit_price=Decimal("1.00"),
            total_price=Decimal("1.00"),
        )

        raw_doc_repo = MagicMock()
        raw_doc_repo.save.return_value = SaveRawDocumentResult(
            success=True, document_id=1
        )
        processed_repo = MagicMock()
        processed_repo.save.return_value = SaveProcessedReceiptResult(
            success=True, receipt_id=10, items_saved=2
        )

        use_case = _make_use_case(
            qr_reader=qr_reader,
            url_validator=url_validator,
            page_fetcher=page_fetcher,
            parser=parser,
            normalizer=normalizer,
            raw_doc_repo=raw_doc_repo,
            processed_repo=processed_repo,
        )

        result = use_case.execute(_default_command())

        assert result.items_count == 2
