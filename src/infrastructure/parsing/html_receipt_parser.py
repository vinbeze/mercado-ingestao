import re
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup, Tag

from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.receipt_parser import ReceiptParser


def _parse_currency(text: str) -> Decimal | None:
    if not text:
        return None
    try:
        cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def _after_colon(text: str) -> str:
    """Retorna o trecho após o último ':' com espaços removidos."""
    parts = text.split(":")
    return parts[-1].strip() if len(parts) > 1 else text.strip()


class HtmlReceiptParser(ReceiptParser):
    def extract_header(self, html: str) -> ReceiptHeader:
        soup = BeautifulSoup(html, "html.parser")

        # Nome da loja: <div class="txtTopo"> ou <div id="u20" class="txtTopo">
        store_name_tag = soup.find("div", class_="txtTopo")
        store_name = store_name_tag.get_text(strip=True) if store_name_tag else None

        # CNPJ: primeiro div.text que contenha padrão de CNPJ
        store_document = None
        for doc_tag in soup.find_all("div", class_="text"):
            text = doc_tag.get_text(strip=True)
            match = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", text)
            if match:
                store_document = match.group()
                break

        # Data de emissão: dentro de <li> que contém "Emissão:"
        purchase_date = None
        for li in soup.find_all("li"):
            text = li.get_text(" ", strip=True)
            match = re.search(
                r"Emiss[aã]o:\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})", text
            )
            if match:
                purchase_date = match.group(1)
                break

        # Número da nota: dentro de <li> que contém "Número:"
        receipt_number = None
        for li in soup.find_all("li"):
            text = li.get_text(" ", strip=True)
            match = re.search(r"N[uú]mero:\s*(\d+)", text)
            if match:
                receipt_number = match.group(1)
                break

        # Total: span com classe "txtMax" (ex: <span class="totalNumb txtMax">22,98</span>)
        total_amount = None
        total_tag = soup.find("span", class_="txtMax")
        if total_tag:
            total_amount = _parse_currency(total_tag.get_text(strip=True))

        return ReceiptHeader(
            store_name=store_name,
            store_document=store_document,
            purchase_date=purchase_date,
            total_amount=total_amount,
            receipt_number=receipt_number,
        )

    def extract_items(self, html: str) -> list[RawReceiptItem]:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="tabResult")
        if not table or not isinstance(table, Tag):
            return []

        items: list[RawReceiptItem] = []
        for line_number, row in enumerate(table.find_all("tr"), start=1):
            # Descrição: <span class="txtTit">
            desc_span = row.find("span", class_="txtTit")
            if not desc_span:
                continue
            raw_description = desc_span.get_text(strip=True)

            # Quantidade: <span class="Rqtd"> → "Qtde.:1" ou "Qtde.: 1,500"
            raw_quantity = None
            rqtd_span = row.find("span", class_="Rqtd")
            if rqtd_span:
                after = _after_colon(rqtd_span.get_text(strip=True))
                raw_quantity = after or None

            # Unidade: <span class="RUN"> → "UN: UN" ou "UN: KG"
            raw_unit = None
            run_span = row.find("span", class_="RUN")
            if run_span:
                raw_unit = _after_colon(run_span.get_text(strip=True)) or None

            # Preço unitário: <span class="RvlUnit"> → "Vl. Unit.:22,98"
            unit_price = None
            unit_span = row.find("span", class_="RvlUnit")
            if unit_span:
                unit_price = _parse_currency(
                    _after_colon(unit_span.get_text(strip=True))
                )

            # Preço total: <span class="valor">
            total_price = None
            valor_span = row.find("span", class_="valor")
            if valor_span:
                total_price = _parse_currency(valor_span.get_text(strip=True))

            items.append(
                RawReceiptItem(
                    line_number=line_number,
                    raw_description=raw_description,
                    raw_quantity=raw_quantity,
                    raw_unit=raw_unit,
                    unit_price=unit_price,
                    total_price=total_price,
                )
            )
        return items
