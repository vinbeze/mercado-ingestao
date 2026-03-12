"""
Testes unitários para DictionaryProductNormalizer.

Nenhuma dependência externa. O normalizador usa dicionários/regras internas.
"""
from decimal import Decimal

import pytest

from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.ports.product_normalizer import ProductNormalizer
from src.infrastructure.normalization.dictionary_product_normalizer import (
    DictionaryProductNormalizer,
)


@pytest.fixture
def normalizer() -> ProductNormalizer:
    return DictionaryProductNormalizer()


# ---------------------------------------------------------------------------
# normalize_description
# ---------------------------------------------------------------------------

class TestDictionaryProductNormalizerNormalizeDescription:
    def test_normalize_description_cleans_extra_whitespace(
        self, normalizer: ProductNormalizer
    ) -> None:
        result = normalizer.normalize_description("  LEITE   INTEGRAL   1L  ")

        assert "  " not in result.canonical_name
        assert result.canonical_name == result.canonical_name.strip()

    def test_normalize_description_standardizes_casing(
        self, normalizer: ProductNormalizer
    ) -> None:
        result = normalizer.normalize_description("LEITE INTEGRAL ITALAC 1L")

        # Deve retornar em Title Case ou lower, não tudo em maiúsculas
        assert result.canonical_name != result.canonical_name.upper() or len(result.canonical_name) == 0

    def test_normalize_description_identifies_brand_when_present(
        self, normalizer: ProductNormalizer
    ) -> None:
        result = normalizer.normalize_description("LEITE INTEGRAL ITALAC 1L")

        assert result.brand == "Italac"

    def test_normalize_description_identifies_basic_category_when_rule_matches(
        self, normalizer: ProductNormalizer
    ) -> None:
        result = normalizer.normalize_description("LEITE INTEGRAL ITALAC 1L")

        assert result.category is not None
        assert len(result.category) > 0

    def test_normalize_description_returns_low_confidence_for_ambiguous_description(
        self, normalizer: ProductNormalizer
    ) -> None:
        result = normalizer.normalize_description("PROD XYZ 123 ABC")

        assert result.confidence < 0.5

    def test_normalize_description_indicates_which_rule_was_applied(
        self, normalizer: ProductNormalizer
    ) -> None:
        result = normalizer.normalize_description("LEITE INTEGRAL ITALAC 1L")

        assert result.normalization_rule_applied is not None


# ---------------------------------------------------------------------------
# normalize_item
# ---------------------------------------------------------------------------

class TestDictionaryProductNormalizerNormalizeItem:
    def test_normalize_item_converts_textual_quantity_to_numeric(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=1,
            raw_description="FRANGO INTEIRO KG",
            raw_quantity="1,350",
            raw_unit="KG",
            unit_price=Decimal("12.99"),
            total_price=Decimal("17.54"),
        )

        result = normalizer.normalize_item(raw_item)

        assert result.quantity == Decimal("1.350")

    def test_normalize_item_standardizes_unit(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=1,
            raw_description="LEITE INTEGRAL 1L",
            raw_quantity="2",
            raw_unit="un",
            unit_price=Decimal("4.99"),
            total_price=Decimal("9.98"),
        )

        result = normalizer.normalize_item(raw_item)

        assert result.unit == "UN"

    def test_normalize_item_uses_description_normalization_for_canonical_name(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=1,
            raw_description="LEITE INTEGRAL ITALAC 1L",
            raw_quantity="1",
            raw_unit="UN",
            unit_price=Decimal("4.99"),
            total_price=Decimal("4.99"),
        )

        result = normalizer.normalize_item(raw_item)

        assert result.canonical_name != "LEITE INTEGRAL ITALAC 1L"
        assert len(result.canonical_name) > 0

    def test_normalize_item_preserves_valid_prices(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=1,
            raw_description="ITEM TESTE",
            raw_quantity="1",
            raw_unit="UN",
            unit_price=Decimal("9.99"),
            total_price=Decimal("9.99"),
        )

        result = normalizer.normalize_item(raw_item)

        assert result.unit_price == Decimal("9.99")
        assert result.total_price == Decimal("9.99")

    def test_normalize_item_handles_missing_fields_without_crashing(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=1,
            raw_description="ITEM SEM CAMPOS",
            raw_quantity=None,
            raw_unit=None,
            unit_price=None,
            total_price=None,
        )

        result = normalizer.normalize_item(raw_item)

        assert result is not None
        assert result.quantity is None
        assert result.unit is None

    def test_normalize_item_works_with_incomplete_item(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=5,
            raw_description="X",
            raw_quantity=None,
            raw_unit=None,
            unit_price=None,
            total_price=None,
        )

        result = normalizer.normalize_item(raw_item)

        assert result is not None

    def test_normalize_item_returns_valid_object_even_when_content_cannot_be_normalized(
        self, normalizer: ProductNormalizer
    ) -> None:
        raw_item = RawReceiptItem(
            line_number=1,
            raw_description="%%%@@@###!!!",
            raw_quantity="??",
            raw_unit="??",
            unit_price=None,
            total_price=None,
        )

        result = normalizer.normalize_item(raw_item)

        assert result is not None
        assert isinstance(result.canonical_name, str)
