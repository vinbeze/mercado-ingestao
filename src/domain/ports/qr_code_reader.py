from abc import ABC, abstractmethod

from src.application.dtos.qr_decode_result import QRDecodeResult


class QRCodeReader(ABC):
    @abstractmethod
    def decode(self, image_bytes: bytes, content_type: str) -> QRDecodeResult: ...
