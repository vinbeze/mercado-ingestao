from src.application.dtos.qr_decode_result import QRDecodeResult
from src.domain.ports.qr_code_reader import QRCodeReader


SUPPORTED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def decode_qr_from_bytes(image_bytes: bytes) -> bytes | None:
    """Função auxiliar que encapsula OpenCV/pyzbar — mockável em testes."""
    raise NotImplementedError


class OpenCVQRReader(QRCodeReader):
    def decode(self, image_bytes: bytes, content_type: str) -> QRDecodeResult:
        raise NotImplementedError
