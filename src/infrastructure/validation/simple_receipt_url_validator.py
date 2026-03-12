from urllib.parse import urlparse

from src.application.dtos.url_validation_result import URLValidationResult
from src.domain.ports.receipt_url_validator import ReceiptURLValidator


class SimpleReceiptURLValidator(ReceiptURLValidator):
    def validate(self, raw_value: str) -> URLValidationResult:
        if raw_value is None:
            return URLValidationResult(is_valid=False, error="Valor não pode ser nulo")

        stripped = raw_value.strip()

        if not stripped:
            return URLValidationResult(is_valid=False, error="Valor não pode ser vazio")

        try:
            parsed = urlparse(stripped)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                return URLValidationResult(
                    is_valid=False, error="Valor não é uma URL HTTP/HTTPS válida"
                )
        except Exception as exc:
            return URLValidationResult(is_valid=False, error=str(exc))

        return URLValidationResult(is_valid=True, normalized_url=stripped)
