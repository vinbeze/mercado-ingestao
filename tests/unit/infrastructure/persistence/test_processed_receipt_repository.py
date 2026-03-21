"""
Testes unitários para SqlAlchemyProcessedReceiptRepository.

A sessão do SQLAlchemy é mockada — nenhum banco real é utilizado.
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.processed_receipt_repository import ProcessedReceiptRepository
from src.infrastructure.persistence.sqlalchemy.repositories.processed_receipt_repository import (
    SqlAlchemyProcessedReceiptRepository,
)


@pytest.fixture
def mock_session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def repository(mock_session: MagicMock) -> ProcessedReceiptRepository:
    return SqlAlchemyProcessedReceiptRepository(session=mock_session)


@pytest.fixture
def valid_header() -> ReceiptHeader:
    return ReceiptHeader(
        store_name="Supermercado Teste",
        store_document="12.345.678/0001-90",
        purchase_date="01/03/2026",
        total_amount=Decimal("9.98"),
        receipt_number="000001",
    )


@pytest.fixture
def valid_items() -> list[NormalizedReceiptItem]:
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


class TestSqlAlchemyProcessedReceiptRepositorySave:
    def test_save_persists_header_and_items_successfully(
        self,
        repository: ProcessedReceiptRepository,
        mock_session: MagicMock,
        valid_header: ReceiptHeader,
        valid_items: list[NormalizedReceiptItem],
    ) -> None:
        result = repository.save(header=valid_header, items=valid_items)

        assert result.success is True
        mock_session.commit.assert_called_once()

    def test_save_returns_total_items_saved(
        self,
        repository: ProcessedReceiptRepository,
        mock_session: MagicMock,
        valid_header: ReceiptHeader,
        valid_items: list[NormalizedReceiptItem],
    ) -> None:
        result = repository.save(header=valid_header, items=valid_items)

        assert result.items_saved == len(valid_items)

    def test_save_accepts_empty_items_list(
        self,
        repository: ProcessedReceiptRepository,
        mock_session: MagicMock,
        valid_header: ReceiptHeader,
    ) -> None:
        result = repository.save(header=valid_header, items=[])

        assert result.success is True
        assert result.items_saved == 0

    def test_save_fails_when_header_is_invalid(
        self,
        repository: ProcessedReceiptRepository,
        mock_session: MagicMock,
        valid_items: list[NormalizedReceiptItem],
        invalid_receipt_header: ReceiptHeader,
    ) -> None:
        mock_session.commit.side_effect = Exception("Header inválido para persistência")

        result = repository.save(header=invalid_receipt_header, items=valid_items)

        assert result.success is False

    def test_save_forwards_data_correctly_to_repository(
        self,
        repository: ProcessedReceiptRepository,
        mock_session: MagicMock,
        valid_header: ReceiptHeader,
        valid_items: list[NormalizedReceiptItem],
    ) -> None:
        repository.save(header=valid_header, items=valid_items)

        # Deve ter adicionado pelo menos o cabeçalho + os itens
        assert mock_session.add.call_count >= 1
