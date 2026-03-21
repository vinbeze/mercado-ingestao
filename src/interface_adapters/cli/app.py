from pathlib import Path

import typer
from sqlalchemy import text

from src.application.dtos.process_receipt_command import ProcessReceiptCommand
from src.application.use_cases.process_receipt_image_use_case import (
    ProcessReceiptImageUseCase,
)
from src.infrastructure.db import create_tables, get_session
from src.infrastructure.http.httpx_receipt_page_fetcher import HttpxReceiptPageFetcher
from src.infrastructure.normalization.dictionary_product_normalizer import (
    DictionaryProductNormalizer,
)
from src.infrastructure.parsing.html_receipt_parser import HtmlReceiptParser
from src.infrastructure.persistence.sqlalchemy.repositories.processed_receipt_repository import (
    SqlAlchemyProcessedReceiptRepository,
)
from src.infrastructure.persistence.sqlalchemy.repositories.raw_document_repository import (
    SqlAlchemyRawDocumentRepository,
)
from src.infrastructure.qr.opencv_qr_reader import OpenCVQRReader
from src.infrastructure.validation.simple_receipt_url_validator import (
    SimpleReceiptURLValidator,
)

CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

app = typer.Typer(help="Processador de notas fiscais eletrônicas (NFe)")


@app.command()
def process(
    image_path: Path = typer.Argument(
        ..., help="Caminho para a imagem da nota fiscal (JPEG, PNG ou WebP)"
    ),
) -> None:
    """Processa uma nota fiscal a partir de uma imagem."""
    if not image_path.exists():
        typer.echo(f"Erro: arquivo não encontrado: {image_path}", err=True)
        raise typer.Exit(code=1)

    suffix = image_path.suffix.lower()
    content_type = CONTENT_TYPES.get(suffix)
    if not content_type:
        typer.echo(
            f"Erro: formato não suportado '{suffix}'. Use .jpg, .png ou .webp.",
            err=True,
        )
        raise typer.Exit(code=1)

    image_bytes = image_path.read_bytes()

    create_tables()
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
            image_bytes=image_bytes, content_type=content_type
        )
        result = use_case.execute(command)
    finally:
        session.close()

    if not result.success:
        for error in result.errors:
            typer.echo(f"Erro: {error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Documento salvo (id={result.document_id})")
    typer.echo(
        f"Nota processada com {result.items_count} itens (id={result.receipt_id})"
    )


@app.command("clear-db")
def clear_db() -> None:
    """Remove todos os dados do banco de dados."""
    typer.confirm("Isso apagará todos os dados permanentemente. Continuar?", abort=True)

    session = get_session()
    try:
        session.execute(text("DELETE FROM purchase_items_normalized"))
        session.execute(text("DELETE FROM purchase_receipts"))
        session.execute(text("DELETE FROM documents_raw"))
        session.commit()
    finally:
        session.close()

    typer.echo("Banco de dados limpo com sucesso.")
