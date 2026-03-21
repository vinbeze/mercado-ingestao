"""
Testes unitários para SqlAlchemyRawDocumentRepository.

A sessão do SQLAlchemy é mockada — nenhum banco real é utilizado.
"""

from unittest.mock import MagicMock

import pytest

from src.domain.ports.raw_document_repository import RawDocumentRepository
from src.infrastructure.persistence.sqlalchemy.repositories.raw_document_repository import (
    SqlAlchemyRawDocumentRepository,
)


@pytest.fixture
def mock_session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def repository(mock_session: MagicMock) -> RawDocumentRepository:
    return SqlAlchemyRawDocumentRepository(session=mock_session)


class TestSqlAlchemyRawDocumentRepositorySave:
    def test_save_persists_data_when_repository_responds_correctly(
        self, repository: RawDocumentRepository, mock_session: MagicMock
    ) -> None:
        result = repository.save(
            image_reference="uploads/nota_001.jpg",
            qr_url="https://sefaz.rs.gov.br/nfce?chNFe=123",
            html="<html>nota</html>",
            status="processed",
        )

        assert result.success is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_save_returns_document_id(
        self, repository: RawDocumentRepository, mock_session: MagicMock
    ) -> None:
        # Simular que o ORM atribui um ID ao objeto após commit
        def set_id(obj):
            obj.id = 42

        mock_session.add.side_effect = set_id

        result = repository.save(
            image_reference="uploads/nota_001.jpg",
            qr_url="https://sefaz.rs.gov.br/nfce?chNFe=123",
            html="<html>nota</html>",
            status="processed",
        )

        assert result.document_id is not None

    def test_save_handles_repository_failure_gracefully(
        self, repository: RawDocumentRepository, mock_session: MagicMock
    ) -> None:
        mock_session.commit.side_effect = Exception("Falha na conexão com o banco")

        result = repository.save(
            image_reference="uploads/nota_001.jpg",
            qr_url="https://sefaz.rs.gov.br/nfce?chNFe=123",
            html="<html>nota</html>",
            status="error",
        )

        assert result.success is False

    def test_save_calls_repository_with_expected_arguments(
        self, repository: RawDocumentRepository, mock_session: MagicMock
    ) -> None:
        repository.save(
            image_reference="uploads/nota_002.jpg",
            qr_url="https://sefaz.sp.gov.br/nfce?chNFe=999",
            html="<html>conteudo</html>",
            status="pending",
        )

        added_obj = mock_session.add.call_args[0][0]
        assert added_obj.image_reference == "uploads/nota_002.jpg"
        assert added_obj.qr_url == "https://sefaz.sp.gov.br/nfce?chNFe=999"
        assert added_obj.html == "<html>conteudo</html>"
        assert added_obj.status == "pending"

    def test_save_validates_required_fields(
        self, repository: RawDocumentRepository
    ) -> None:
        with pytest.raises((ValueError, TypeError)):
            repository.save(
                image_reference="",
                qr_url="",
                html="",
                status="",
            )
