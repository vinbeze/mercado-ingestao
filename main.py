from dotenv import load_dotenv

load_dotenv()

from src.interface_adapters.cli.app import app  # noqa: E402

if __name__ == "__main__":
    app()
