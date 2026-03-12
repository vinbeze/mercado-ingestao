from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.product_normalization_result import ProductNormalizationResult
from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.ports.product_normalizer import ProductNormalizer


class DictionaryProductNormalizer(ProductNormalizer):
    def normalize_description(self, raw_description: str) -> ProductNormalizationResult:
        raise NotImplementedError

    def normalize_item(self, raw_item: RawReceiptItem) -> NormalizedReceiptItem:
        raise NotImplementedError
