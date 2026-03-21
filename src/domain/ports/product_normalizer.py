from abc import ABC, abstractmethod

from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.product_normalization_result import ProductNormalizationResult
from src.domain.entities.raw_receipt_item import RawReceiptItem


class ProductNormalizer(ABC):
    @abstractmethod
    def normalize_description(
        self, raw_description: str
    ) -> ProductNormalizationResult: ...

    @abstractmethod
    def normalize_item(self, raw_item: RawReceiptItem) -> NormalizedReceiptItem: ...
