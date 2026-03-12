from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ReceiptHeader:
    store_name: str | None = None
    store_document: str | None = None
    purchase_date: str | None = None
    total_amount: Decimal | None = None
    receipt_number: str | None = None
