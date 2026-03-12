from src.application.dtos.url_validation_result import URLValidationResult
from src.domain.ports.receipt_url_validator import ReceiptURLValidator


class SimpleReceiptURLValidator(ReceiptURLValidator):
    def validate(self, raw_value: str) -> URLValidationResult:
        raise NotImplementedError
