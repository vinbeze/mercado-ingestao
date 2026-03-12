from fastapi import FastAPI

from src.interface_adapters.http.controllers.receipt_controller import router as receipt_router

app = FastAPI(title="Mercado NF-e Ingestão", version="0.1.0")

app.include_router(receipt_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
