import os

from dotenv import load_dotenv

load_dotenv()

import uvicorn

from src.infrastructure.db import create_tables
from src.interface_adapters.http.app import app

if __name__ == "__main__":
    create_tables()

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"

    uvicorn.run(app, host=host, port=port)
