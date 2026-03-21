from decimal import Decimal, InvalidOperation

from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.product_normalization_result import ProductNormalizationResult
from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.ports.product_normalizer import ProductNormalizer

_BRAND_RULES: dict[str, str] = {
    "ITALAC": "Italac",
    "WICKBOLD": "Wickbold",
    "SADIA": "Sadia",
    "PERDIGAO": "Perdigão",
    "NESTLE": "Nestlé",
    "FORNO DE MINAS": "Forno de Minas",
    "QUAKER": "Quaker",
    "DANONE": "Danone",
    "ACTIVIA": "Activia",
}

_CATEGORY_RULES: dict[str, str] = {
    "LEITE": "Laticínios",
    "QUEIJO": "Laticínios",
    "IOGURTE": "Laticínios",
    "MANTEIGA": "Laticínios",
    "REQUEIJAO": "Laticínios",
    "PAO": "Padaria",
    "PORCAO": "Padaria",
    "BISC": "Biscoitos",
    "BOLACHA": "Biscoitos",
    "FRANGO": "Carnes",
    "CARNE": "Carnes",
    "BIFE": "Carnes",
    "PEITO": "Carnes",
    "ARROZ": "Grãos",
    "FEIJAO": "Grãos",
    "LENTILHA": "Grãos",
    "OLEO": "Óleos",
    "AZEITE": "Óleos",
    "AGUA": "Bebidas",
    "SUCO": "Bebidas",
    "REFRIGERANTE": "Bebidas",
}


def _parse_quantity(raw_quantity: str | None) -> Decimal | None:
    if raw_quantity is None:
        return None
    try:
        normalized = raw_quantity.strip().replace(",", ".")
        return Decimal(normalized)
    except (InvalidOperation, ValueError):
        return None


class DictionaryProductNormalizer(ProductNormalizer):
    def normalize_description(self, raw_description: str) -> ProductNormalizationResult:
        cleaned = " ".join(raw_description.split())
        canonical_name = cleaned.title()

        words = cleaned.upper().split()

        brand: str | None = None
        for keyword, brand_name in _BRAND_RULES.items():
            if keyword in words or keyword in cleaned.upper():
                brand = brand_name
                break

        category: str | None = None
        for keyword, cat_name in _CATEGORY_RULES.items():
            if keyword in words or keyword in cleaned.upper():
                category = cat_name
                break

        rules_applied = []
        if brand:
            matching_key = next(k for k, v in _BRAND_RULES.items() if v == brand)
            rules_applied.append(f"brand:{matching_key}")
        if category:
            matching_key = next(k for k, v in _CATEGORY_RULES.items() if v == category)
            rules_applied.append(f"category:{matching_key}")

        normalization_rule_applied = "|".join(rules_applied) if rules_applied else None
        confidence = 0.9 if rules_applied else 0.1

        return ProductNormalizationResult(
            canonical_name=canonical_name,
            brand=brand,
            category=category,
            confidence=confidence,
            normalization_rule_applied=normalization_rule_applied,
        )

    def normalize_item(self, raw_item: RawReceiptItem) -> NormalizedReceiptItem:
        norm = self.normalize_description(raw_item.raw_description)

        quantity = _parse_quantity(raw_item.raw_quantity)
        unit = raw_item.raw_unit.strip().upper() if raw_item.raw_unit else None

        return NormalizedReceiptItem(
            canonical_name=norm.canonical_name,
            brand=norm.brand,
            category=norm.category,
            quantity=quantity,
            unit=unit,
            unit_price=raw_item.unit_price,
            total_price=raw_item.total_price,
        )
