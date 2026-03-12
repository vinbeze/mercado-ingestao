# mercado-nfe-ingestao

Sistema de ingestão de NF-e (Nota Fiscal Eletrônica) a partir de imagens de cupom fiscal.

## Sobre o projeto

O sistema recebe uma foto de cupom fiscal, extrai os dados da nota via QR Code e os persiste no banco de dados de forma estruturada e normalizada.

**Fluxo de processamento:**

1. Recebe a imagem do cupom fiscal
2. Lê o QR Code com OpenCV + pyzbar
3. Valida a URL extraída do QR Code
4. Busca o HTML da nota no portal da SEFAZ
5. Faz o parse do HTML (cabeçalho + itens) com BeautifulSoup
6. Normaliza os itens (nomes canônicos, marcas, categorias)
7. Persiste os dados brutos e processados no PostgreSQL

## Arquitetura

O projeto segue **Clean Architecture** com separação em três camadas:

```
src/
├── domain/             # Entidades e ports (interfaces)
│   ├── entities/       # ReceiptHeader, RawReceiptItem, NormalizedReceiptItem, etc.
│   └── ports/          # Contratos: QRCodeReader, ReceiptParser, repositories, etc.
├── application/        # Use cases e DTOs
│   ├── use_cases/      # ProcessReceiptImageUseCase
│   └── dtos/           # ProcessReceiptCommand, ProcessReceiptResult, etc.
└── infrastructure/     # Implementações concretas
    ├── qr/             # OpenCV + pyzbar
    ├── http/           # httpx
    ├── parsing/        # BeautifulSoup
    ├── normalization/  # Normalizador por dicionário
    ├── validation/     # Validador de URL
    └── persistence/    # SQLAlchemy + PostgreSQL
```

As dependências fluem de fora para dentro: `infrastructure → application → domain`. O domínio não depende de nenhum framework externo.

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI + Uvicorn |
| Validação | Pydantic |
| Leitura de QR | OpenCV + pyzbar |
| HTTP client | httpx |
| HTML parsing | BeautifulSoup4 |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Banco de dados | PostgreSQL |
| Testes | pytest + pytest-asyncio + pytest-mock |

## Pré-requisitos

- Python 3.12+
- PostgreSQL rodando localmente (ou via Docker)

## Configuração

Copie o arquivo de exemplo e preencha as variáveis:

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mercado_nfe
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/mercado_nfe

APP_ENV=development
SECRET_KEY=sua_chave_secreta
```

> Em produção, gere uma chave segura com: `openssl rand -hex 32`

## Rodando o projeto

```bash
# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instalar dependências
pip install -e .

# Executar as migrations
alembic upgrade head

# Iniciar a API
uvicorn src.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## Rodando os testes

```bash
pip install -e ".[dev]"
pytest
```

Para ver a cobertura:

```bash
pytest --tb=short -v
```
