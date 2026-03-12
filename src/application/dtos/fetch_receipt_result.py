from dataclasses import dataclass


@dataclass
class FetchReceiptResult:
    success: bool
    status_code: int | None = None
    html: str | None = None
    final_url: str | None = None
    error: str | None = None
