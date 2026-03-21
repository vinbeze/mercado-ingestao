from src.application.dtos.qr_decode_result import QRDecodeResult
from src.domain.ports.qr_code_reader import QRCodeReader

SUPPORTED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def decode_qr_from_bytes(image_bytes: bytes) -> bytes | None:
    """Função auxiliar que encapsula OpenCV/pyzbar — mockável em testes."""
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode as pyzbar_decode

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Não foi possível decodificar a imagem")

    decoded_objects = pyzbar_decode(img)
    if not decoded_objects:
        return None
    return decoded_objects[0].data


class OpenCVQRReader(QRCodeReader):
    def decode(self, image_bytes: bytes, content_type: str) -> QRDecodeResult:
        if content_type not in SUPPORTED_CONTENT_TYPES:
            return QRDecodeResult(
                found=False,
                error=f"Tipo de conteúdo não suportado: {content_type}",
            )

        try:
            raw = decode_qr_from_bytes(image_bytes)
            if raw is None:
                return QRDecodeResult(found=False)
            return QRDecodeResult(found=True, raw_value=raw.decode("utf-8"))
        except Exception as exc:
            return QRDecodeResult(found=False, error=str(exc))
