"""
Testes unitários para OpenCVQRReader.

OpenCV e pyzbar são mockados para isolar a lógica do adaptador.
"""

from unittest.mock import patch

import pytest

from src.domain.ports.qr_code_reader import QRCodeReader
from src.infrastructure.qr.opencv_qr_reader import OpenCVQRReader


@pytest.fixture
def reader() -> QRCodeReader:
    return OpenCVQRReader()


class TestOpenCVQRReaderDecode:
    def test_decode_returns_found_true_when_image_has_valid_qr(
        self, reader: QRCodeReader
    ) -> None:
        fake_qr_data = b"https://sefaz.rs.gov.br/nfce?chNFe=123"

        with patch(
            "src.infrastructure.qr.opencv_qr_reader.decode_qr_from_bytes",
            return_value=fake_qr_data,
        ):
            result = reader.decode(b"\xff\xd8\xff\xe0valid", "image/jpeg")

        assert result.found is True

    def test_decode_returns_raw_value_when_qr_read_successfully(
        self, reader: QRCodeReader
    ) -> None:
        expected_url = "https://sefaz.rs.gov.br/nfce?chNFe=123"

        with patch(
            "src.infrastructure.qr.opencv_qr_reader.decode_qr_from_bytes",
            return_value=expected_url.encode(),
        ):
            result = reader.decode(b"\xff\xd8\xff\xe0valid", "image/jpeg")

        assert result.raw_value == expected_url

    def test_decode_returns_found_false_when_image_has_no_qr_code(
        self, reader: QRCodeReader
    ) -> None:
        with patch(
            "src.infrastructure.qr.opencv_qr_reader.decode_qr_from_bytes",
            return_value=None,
        ):
            result = reader.decode(b"\xff\xd8\xff\xe0no_qr", "image/jpeg")

        assert result.found is False
        assert result.raw_value is None

    def test_decode_returns_error_when_image_is_corrupted(
        self, reader: QRCodeReader
    ) -> None:
        with patch(
            "src.infrastructure.qr.opencv_qr_reader.decode_qr_from_bytes",
            side_effect=ValueError("Bytes de imagem inválidos"),
        ):
            result = reader.decode(b"not_an_image", "image/jpeg")

        assert result.found is False
        assert result.error is not None

    def test_decode_works_with_jpeg_format(self, reader: QRCodeReader) -> None:
        with patch(
            "src.infrastructure.qr.opencv_qr_reader.decode_qr_from_bytes",
            return_value=b"https://sefaz.sp.gov.br/nfce?chNFe=1",
        ):
            result = reader.decode(b"\xff\xd8\xff\xe0jpeg_bytes", "image/jpeg")

        assert result.found is True

    def test_decode_works_with_png_format(self, reader: QRCodeReader) -> None:
        with patch(
            "src.infrastructure.qr.opencv_qr_reader.decode_qr_from_bytes",
            return_value=b"https://sefaz.sp.gov.br/nfce?chNFe=2",
        ):
            result = reader.decode(b"\x89PNG\r\n\x1a\npng_bytes", "image/png")

        assert result.found is True

    def test_decode_rejects_incompatible_content_type(
        self, reader: QRCodeReader
    ) -> None:
        result = reader.decode(b"some_bytes", "application/pdf")

        assert result.found is False
        assert result.error is not None
