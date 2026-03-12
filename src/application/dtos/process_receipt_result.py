from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class ProcessReceiptResult:
    success: bool
    items_count: int
    errors: list[str] = field(default_factory=list)
    document_id: UUID | int | None = None
    receipt_id: UUID | int | None = None
