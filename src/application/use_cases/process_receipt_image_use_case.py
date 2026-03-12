from src.application.dtos.process_receipt_command import ProcessReceiptCommand
from src.application.dtos.process_receipt_result import ProcessReceiptResult
from src.domain.ports.qr_code_reader import QRCodeReader
from src.domain.ports.receipt_url_validator import ReceiptURLValidator
from src.domain.ports.receipt_page_fetcher import ReceiptPageFetcher
from src.domain.ports.receipt_parser import ReceiptParser
from src.domain.ports.product_normalizer import ProductNormalizer
from src.domain.ports.raw_document_repository import RawDocumentRepository
from src.domain.ports.processed_receipt_repository import ProcessedReceiptRepository


class ProcessReceiptImageUseCase:
    def __init__(
        self,
        qr_reader: QRCodeReader,
        url_validator: ReceiptURLValidator,
        page_fetcher: ReceiptPageFetcher,
        parser: ReceiptParser,
        normalizer: ProductNormalizer,
        raw_doc_repository: RawDocumentRepository,
        processed_repository: ProcessedReceiptRepository,
    ) -> None:
        self._qr_reader = qr_reader
        self._url_validator = url_validator
        self._page_fetcher = page_fetcher
        self._parser = parser
        self._normalizer = normalizer
        self._raw_doc_repository = raw_doc_repository
        self._processed_repository = processed_repository

    def execute(self, command: ProcessReceiptCommand) -> ProcessReceiptResult:
        raise NotImplementedError
