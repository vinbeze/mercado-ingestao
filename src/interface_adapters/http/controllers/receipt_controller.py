from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.application.dtos.process_receipt_command import ProcessReceiptCommand
from src.application.use_cases.process_receipt_image_use_case import ProcessReceiptImageUseCase
from src.infrastructure.db import create_tables, get_session
from src.infrastructure.http.httpx_receipt_page_fetcher import HttpxReceiptPageFetcher
from src.infrastructure.normalization.dictionary_product_normalizer import DictionaryProductNormalizer
from src.infrastructure.parsing.html_receipt_parser import HtmlReceiptParser
from src.infrastructure.persistence.sqlalchemy.repositories.processed_receipt_repository import (
    SqlAlchemyProcessedReceiptRepository,
)
from src.infrastructure.persistence.sqlalchemy.repositories.raw_document_repository import (
    SqlAlchemyRawDocumentRepository,
)
from src.infrastructure.qr.opencv_qr_reader import OpenCVQRReader
from src.infrastructure.validation.simple_receipt_url_validator import SimpleReceiptURLValidator

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/receipts/process")
async def process_receipt(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de arquivo não suportado: {file.content_type}. Use image/jpeg ou image/png.",
        )

    image_bytes = await file.read()

    session = get_session()
    try:
        use_case = ProcessReceiptImageUseCase(
            qr_reader=OpenCVQRReader(),
            url_validator=SimpleReceiptURLValidator(),
            page_fetcher=HttpxReceiptPageFetcher(),
            parser=HtmlReceiptParser(),
            normalizer=DictionaryProductNormalizer(),
            raw_doc_repository=SqlAlchemyRawDocumentRepository(session),
            processed_repository=SqlAlchemyProcessedReceiptRepository(session),
        )

        command = ProcessReceiptCommand(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )

        result = use_case.execute(command)

        return JSONResponse(
            status_code=200 if result.success else 422,
            content={
                "success": result.success,
                "document_id": result.document_id,
                "receipt_id": result.receipt_id,
                "items_count": result.items_count,
                "errors": result.errors,
            },
        )
    finally:
        session.close()
