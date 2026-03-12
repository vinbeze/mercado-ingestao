import re
from decimal import Decimal, InvalidOperation

from bs4 import BeautifulSoup

from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.receipt_parser import ReceiptParser


def _parse_currency(text: str) -> Decimal | None:
    if not text:
        return None
    try:
        cleaned = text.replace("R$", "").strip()
        cleaned = cleaned.replace(".", "").replace(",", ".")
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


class HtmlReceiptParser(ReceiptParser):
    def extract_header(self, html: str) -> ReceiptHeader:
        soup = BeautifulSoup(html, "html.parser")

        store_name_tag = soup.find("div", class_="txtTopo")
        store_name = store_name_tag.get_text(strip=True) if store_name_tag else None

        store_document = None
        doc_tag = soup.find("div", class_="text")
        if doc_tag:
            text = doc_tag.get_text(strip=True)
            match = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", text)
            if match:
                store_document = match.group()

        purchase_date = None
        date_tag = soup.find("span", class_="txt")
        if date_tag:
            text = date_tag.get_text(strip=True)
            match = re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}", text)
            if match:
                purchase_date = match.group()

        receipt_number = None
        nf_tag = soup.find("span", class_="nNF")
        if nf_tag:
            text = nf_tag.get_text(strip=True)
            match = re.search(r"\d+", text)
            if match:
                receipt_number = match.group()

        total_amount = None
        total_tag = soup.find("span", id="totalNota")
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
        if not table:
            return []

        items: list[RawReceiptItem] = []
        rows = table.select("tbody tr")
        for line_number, row in enumerate(rows, start=1):
            desc_td = row.find("td", class_="txtTit")
            if not desc_td:
                continue
            raw_description = desc_td.get_text(strip=True)

            raw_quantity = None
            raw_unit = None
            rqtd_td = row.find("td", class_="Rqtd")
            if rqtd_td:
                parts = rqtd_td.get_text(strip=True).split()
                raw_quantity = parts[0] if parts else None
                raw_unit = parts[1] if len(parts) > 1 else None

            unit_price = None
            unit_td = row.find("td", class_="RvlUnit")
            if unit_td:
                unit_price = _parse_currency(unit_td.get_text(strip=True))

            total_price = None
            valor_td = row.find("td", class_="valor")
            if valor_td:
                total_price = _parse_currency(valor_td.get_text(strip=True))

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
