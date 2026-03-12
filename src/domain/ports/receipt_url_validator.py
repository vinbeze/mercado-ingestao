from abc import ABC, abstractmethod

from src.application.dtos.url_validation_result import URLValidationResult


class ReceiptURLValidator(ABC):
    @abstractmethod
    def validate(self, raw_value: str) -> URLValidationResult:
        ...
