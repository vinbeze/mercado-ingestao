"""
Testes unitários para ReceiptURLValidator.

O validador é uma regra de domínio pura. Testa-se a implementação concreta
(SimpleReceiptURLValidator), que não possui dependências externas.
"""

import pytest

from src.domain.ports.receipt_url_validator import ReceiptURLValidator
from src.infrastructure.validation.simple_receipt_url_validator import (
    SimpleReceiptURLValidator,
)


@pytest.fixture
def validator() -> ReceiptURLValidator:
    return SimpleReceiptURLValidator()


class TestReceiptURLValidatorValidate:
    def test_validate_accepts_valid_http_url(
        self, validator: ReceiptURLValidator
    ) -> None:
        result = validator.validate(
            "http://www.sefaz.go.gov.br/nfeweb/consulta?chave=123"
        )

        assert result.is_valid is True

    def test_validate_accepts_valid_https_url(
        self, validator: ReceiptURLValidator
    ) -> None:
        result = validator.validate(
            "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?chNFe=999"
        )

        assert result.is_valid is True

    def test_validate_strips_leading_and_trailing_whitespace(
        self, validator: ReceiptURLValidator
    ) -> None:
        raw = "  https://www.nfce.fazenda.sp.gov.br/consulta?chave=abc  "
        result = validator.validate(raw)

        assert result.is_valid is True
        assert result.normalized_url == raw.strip()

    def test_validate_rejects_empty_string(
        self, validator: ReceiptURLValidator
    ) -> None:
        result = validator.validate("")

        assert result.is_valid is False
        assert result.error is not None

    def test_validate_rejects_text_that_is_not_a_url(
        self, validator: ReceiptURLValidator
    ) -> None:
        result = validator.validate("LEITE INTEGRAL ITALAC 1L")

        assert result.is_valid is False
        assert result.error is not None

    def test_validate_rejects_none_value(self, validator: ReceiptURLValidator) -> None:
        result = validator.validate(None)  # type: ignore[arg-type]

        assert result.is_valid is False
        assert result.error is not None

    def test_validate_returns_normalized_url_when_valid(
        self, validator: ReceiptURLValidator
    ) -> None:
        url = "https://www.nfce.fazenda.sp.gov.br/consulta?chave=123"
        result = validator.validate(url)

        assert result.is_valid is True
        assert result.normalized_url == url
