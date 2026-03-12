from src.domain.entities.raw_receipt_item import RawReceiptItem
from src.domain.entities.receipt import ReceiptHeader
from src.domain.ports.receipt_parser import ReceiptParser


class HtmlReceiptParser(ReceiptParser):
    def extract_header(self, html: str) -> ReceiptHeader:
        raise NotImplementedError

    def extract_items(self, html: str) -> list[RawReceiptItem]:
        raise NotImplementedError
