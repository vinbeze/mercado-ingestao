from dataclasses import dataclass
from decimal import Decimal


@dataclass
class NormalizedReceiptItem:
    canonical_name: str
    brand: str | None = None
    category: str | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    unit_price: Decimal | None = None
    total_price: Decimal | None = None
