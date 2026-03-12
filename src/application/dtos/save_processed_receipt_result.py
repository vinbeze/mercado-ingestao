from dataclasses import dataclass
from uuid import UUID


@dataclass
class SaveProcessedReceiptResult:
    success: bool
    items_saved: int
    receipt_id: UUID | int | None = None
