from decimal import Decimal

import pytest

from src.domain.entities.normalized_receipt_item import NormalizedReceiptItem
from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.entities.receipt import ReceiptHeader


# ---------------------------------------------------------------------------
# Image fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def image_with_valid_qr() -> bytes:
    """Bytes representando uma imagem JPEG válida com QR Code presente (mock)."""
    return b"\xff\xd8\xff\xe0valid_qr_image_bytes"


@pytest.fixture
def image_without_qr() -> bytes:
    """Bytes representando uma imagem JPEG sem QR Code."""
    return b"\xff\xd8\xff\xe0no_qr_image_bytes"


@pytest.fixture
def invalid_image_bytes() -> bytes:
    """Bytes corrompidos / não representam imagem válida."""
    return b"not_an_image_at_all_xyzxyz"


# ---------------------------------------------------------------------------
# QR / URL fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def qr_raw_valid_url() -> str:
    """URL válida extraída de um QR Code de nota fiscal."""
    return "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?chNFe=12345"


@pytest.fixture
def qr_raw_invalid_text() -> str:
    """Texto que não é uma URL (não pode ser utilizado como URL de consulta)."""
    return "PRODUTO LEITE INTEGRAL 1L"


# ---------------------------------------------------------------------------
# HTML fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def receipt_html_complete() -> str:
    """HTML completo de uma página de nota fiscal com todos os campos.
    Estrutura baseada na resposta real do portal NFC-e (SEFAZ nfce_rj_v2.05).
    """
    return """
    <html>
    <body>
      <div id="u20" class="txtTopo">SUPERMERCADO EXEMPLO LTDA</div>
      <div class="text">CNPJ: 12.345.678/0001-90</div>
      <table id="tabResult">
        <tr>
          <td>
            <span class="txtTit">LEITE INTEGRAL ITALAC 1L</span>
            <span class="Rqtd"><strong>Qtde.:</strong>2</span>
            <span class="RUN"><strong>UN: </strong>UN</span>
            <span class="RvlUnit"><strong>Vl. Unit.:</strong>4,99</span>
          </td>
          <td><span class="valor">9,98</span></td>
        </tr>
        <tr>
          <td>
            <span class="txtTit">PAO FORMA WICKBOLD 500G</span>
            <span class="Rqtd"><strong>Qtde.:</strong>1</span>
            <span class="RUN"><strong>UN: </strong>UN</span>
            <span class="RvlUnit"><strong>Vl. Unit.:</strong>8,90</span>
          </td>
          <td><span class="valor">8,90</span></td>
        </tr>
      </table>
      <div id="totalNota">
        <span class="totalNumb txtMax">157,83</span>
      </div>
      <ul>
        <li>
          <strong>Número: </strong>000123456
          <strong>Emissão: </strong>01/03/2026 14:30:00
        </li>
      </ul>
    </body>
    </html>
    """


@pytest.fixture
def receipt_html_missing_fields() -> str:
    """HTML com campos opcionais ausentes (sem data, sem número da nota)."""
    return """
    <html>
    <body>
      <div class="txtTopo">MERCADO SEM DADOS LTDA</div>
      <div id="totalNota">
        <span class="totalNumb txtMax">50,00</span>
      </div>
      <table id="tabResult">
        <tr>
          <td>
            <span class="txtTit">PRODUTO GENERICO</span>
            <span class="Rqtd"><strong>Qtde.:</strong>1</span>
            <span class="RUN"><strong>UN: </strong>UN</span>
            <span class="RvlUnit"><strong>Vl. Unit.:</strong>50,00</span>
          </td>
          <td><span class="valor">50,00</span></td>
        </tr>
      </table>
    </body>
    </html>
    """


@pytest.fixture
def receipt_html_without_items() -> str:
    """HTML completo de cabeçalho mas sem itens na tabela."""
    return """
    <html>
    <body>
      <div class="txtTopo">SUPERMERCADO VAZIO LTDA</div>
      <div class="text">CNPJ: 99.999.999/0001-99</div>
      <div id="totalNota">
        <span class="totalNumb txtMax">0,00</span>
      </div>
      <ul>
        <li><strong>Emissão: </strong>10/02/2026 09:00:00</li>
      </ul>
      <table id="tabResult"></table>
    </body>
    </html>
    """


# ---------------------------------------------------------------------------
# Item fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_item_examples() -> list[RawReceiptItem]:
    return [
        RawReceiptItem(
            line_number=1,
            raw_description="LEITE INTEGRAL ITALAC 1L",
            raw_quantity="2",
            raw_unit="UN",
            unit_price=Decimal("4.99"),
            total_price=Decimal("9.98"),
        ),
        RawReceiptItem(
            line_number=2,
            raw_description="PAO FORMA WICKBOLD 500G",
            raw_quantity="1",
            raw_unit="UN",
            unit_price=Decimal("8.90"),
            total_price=Decimal("8.90"),
        ),
        RawReceiptItem(
            line_number=3,
            raw_description="FRANGO INTEIRO KG",
            raw_quantity="1,350",
            raw_unit="KG",
            unit_price=Decimal("12.99"),
            total_price=Decimal("17.54"),
        ),
    ]


@pytest.fixture
def normalized_item_examples() -> list[NormalizedReceiptItem]:
    return [
        NormalizedReceiptItem(
            canonical_name="Leite Integral",
            brand="Italac",
            category="Laticínios",
            quantity=Decimal("2"),
            unit="UN",
            unit_price=Decimal("4.99"),
            total_price=Decimal("9.98"),
        ),
        NormalizedReceiptItem(
            canonical_name="Pão de Forma",
            brand="Wickbold",
            category="Padaria",
            quantity=Decimal("1"),
            unit="UN",
            unit_price=Decimal("8.90"),
            total_price=Decimal("8.90"),
        ),
    ]


# ---------------------------------------------------------------------------
# Header fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_receipt_header() -> ReceiptHeader:
    return ReceiptHeader(
        store_name="Supermercado Exemplo Ltda",
        store_document="12.345.678/0001-90",
        purchase_date="01/03/2026 14:30:00",
        total_amount=Decimal("157.83"),
        receipt_number="000123456",
    )


@pytest.fixture
def invalid_receipt_header() -> ReceiptHeader:
    """Header com campos obrigatórios ausentes/inválidos."""
    return ReceiptHeader(
        store_name=None,
        store_document=None,
        purchase_date=None,
        total_amount=None,
        receipt_number=None,
    )
