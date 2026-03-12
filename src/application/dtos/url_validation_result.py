from dataclasses import dataclass


@dataclass
class URLValidationResult:
    is_valid: bool
    normalized_url: str | None = None
    error: str | None = None
