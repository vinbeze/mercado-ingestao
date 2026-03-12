from dataclasses import dataclass


@dataclass
class QRDecodeResult:
    found: bool
    raw_value: str | None = None
    error: str | None = None
