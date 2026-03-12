from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class RawDocument:
    image_reference: str
    qr_url: str
    html: str
    status: str
    id: UUID | int | None = field(default=None)
