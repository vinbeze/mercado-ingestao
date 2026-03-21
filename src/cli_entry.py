def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    from src.interface_adapters.cli.app import app

    app()
