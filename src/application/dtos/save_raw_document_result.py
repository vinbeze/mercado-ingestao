from dataclasses import dataclass
from uuid import UUID


@dataclass
class SaveRawDocumentResult:
    success: bool
    document_id: UUID | int | None = None
