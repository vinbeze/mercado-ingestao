from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RawReceiptItem:
    line_number: int
    raw_description: str
    raw_quantity: str | None = None
    raw_unit: str | None = None
    unit_price: Decimal | None = None
    total_price: Decimal | None = None
