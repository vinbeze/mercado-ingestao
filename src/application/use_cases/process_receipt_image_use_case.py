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
        errors: list[str] = []

        qr_result = self._qr_reader.decode(command.image_bytes, command.content_type)
        if not qr_result.found:
            errors.append(qr_result.error or "QR Code não encontrado na imagem")
            return ProcessReceiptResult(success=False, items_count=0, errors=errors)

        url_result = self._url_validator.validate(qr_result.raw_value)
        if not url_result.is_valid:
            errors.append(url_result.error or "URL extraída do QR Code é inválida")
            return ProcessReceiptResult(success=False, items_count=0, errors=errors)

        fetch_result = self._page_fetcher.fetch(url_result.normalized_url, timeout_seconds=30)
        if not fetch_result.success:
            errors.append(fetch_result.error or "Falha ao buscar página da nota fiscal")
            return ProcessReceiptResult(success=False, items_count=0, errors=errors)

        raw_save = self._raw_doc_repository.save(
            image_reference=f"upload:{command.content_type}",
            qr_url=url_result.normalized_url,
            html=fetch_result.html or "",
            status="processing",
        )

        header = self._parser.extract_header(fetch_result.html or "")
        raw_items = self._parser.extract_items(fetch_result.html or "")

        normalized_items = []
        for raw_item in raw_items:
            try:
                normalized_items.append(self._normalizer.normalize_item(raw_item))
            except Exception as exc:
                errors.append(f"Erro ao normalizar item {raw_item.line_number}: {exc}")

        processed_save = self._processed_repository.save(
            header=header,
            items=normalized_items,
        )

        return ProcessReceiptResult(
            success=True,
            items_count=len(normalized_items),
            document_id=raw_save.document_id,
            receipt_id=processed_save.receipt_id,
            errors=errors,
        )
