# Instruções do Projeto

## Variáveis de Ambiente

- Nunca leia arquivos `.env` (`.env`, `.env.local`, `.env.production`, etc.)
- Assuma que todas as variáveis de ambiente já estão preenchidas e configuradas corretamente
- Para saber quais variáveis o projeto utiliza, leia o `.env.example`

## Desenvolvimento de novas features

Toda nova feature deve seguir o ciclo TDD:

1. **Red** — escreva o teste antes do código de produção e confirme que ele falha
2. **Green** — implemente o mínimo de código necessário para o teste passar
3. **Refactor** — melhore o código sem quebrar os testes

Não implemente funcionalidade sem um teste correspondente que a cubra.

## Arquitetura

O projeto segue **Clean Architecture** com três camadas. Respeite rigorosamente as dependências:

```
Infrastructure → Application → Domain
```

- **Domain** (`src/domain/`): entidades e ports (interfaces ABC). Sem dependências de frameworks.
- **Application** (`src/application/`): use cases e DTOs. Sem dependências de infraestrutura.
- **Infrastructure** (`src/infrastructure/`): implementações concretas dos ports.
- **Interface Adapters** (`interface_adapters/`): CLI com Typer.

Nunca crie dependências invertendo esse fluxo (ex: domain importando infrastructure).

## Convenções de Nomenclatura

| Elemento | Convenção | Exemplo |
|---|---|---|
| Interfaces/Ports | PascalCase sem prefixo | `QRCodeReader`, `ReceiptParser` |
| Implementações | Prefixo com tecnologia | `OpenCVQRReader`, `HttpxReceiptPageFetcher` |
| Use Cases | Sufixo `UseCase` | `ProcessReceiptImageUseCase` |
| DTOs de entrada | Sufixo `Command` | `ProcessReceiptCommand` |
| DTOs de saída | Sufixo `Result` | `ProcessReceiptResult` |
| Modelos ORM | Sufixo `Model` | `DocumentRawModel` |
| Métodos/atributos privados | Prefixo `_` | `_parse_currency()`, `self._session` |
| Constantes | `UPPER_SNAKE_CASE` | `SUPPORTED_CONTENT_TYPES` |
| Dicionários de regras | Sufixo `_RULES` | `_BRAND_RULES`, `_CATEGORY_RULES` |

## Tipagem

- Python 3.12 com `mypy` em modo `strict`. Todo código novo deve passar sem erros.
- Use `str | None` (PEP 604), nunca `Optional[str]`.
- Use genéricos nativos: `list[str]`, `dict[str, str]`, nunca `List`, `Dict`.
- Sempre declare tipos de retorno explicitamente.

## Padrões de Código

### DTOs (Command/Result)
Toda operação entre camadas usa dataclasses com `Command` (entrada) e `Result` (saída):

```python
@dataclass
class FooResult:
    success: bool
    error: str | None = None
```

### Tratamento de Erros
- Acumule erros em `list[str]` durante a execução; não lance exceções imediatamente.
- Retorne `success=False` com a lista de erros preenchida.
- Lance exceções apenas para violações de invariantes (ex: campos obrigatórios em repositórios).

### Injeção de Dependências
Dependências são injetadas via construtor e armazenadas com prefixo `_`:

```python
def __init__(self, qr_reader: QRCodeReader, ...) -> None:
    self._qr_reader = qr_reader
```

### Persistência (SQLAlchemy)
Sempre use transações explícitas com rollback em caso de falha:

```python
try:
    self._session.add(obj)
    self._session.commit()
    self._session.refresh(obj)
except Exception:
    self._session.rollback()
    return SaveFooResult(success=False)
```

## Padrões de Teste

- Testes ficam em `tests/unit/` espelhando a estrutura de `src/`.
- Use fixtures em `conftest.py` para dados compartilhados entre testes.
- Agrupe testes relacionados em classes: `class TestFooBar`.
- Siga o padrão AAA (Arrange, Act, Assert).
- Use helpers privados para montar objetos de teste: `_make_use_case()`, `_default_command()`.
- Mocke todas as dependências externas; nunca acesse rede, disco ou banco em testes unitários.

## Commits

Use commits semânticos em português, com escopo quando aplicável:

```
feat(qrcode): adiciona funcionalidade para leitura de qrcode
fix(parser): corrige extração de valor total da nota
refactor(db): simplifica lógica de rollback no repositório
chore(ci): atualiza pipeline de release
```

Tipos: `feat`, `fix`, `refactor`, `chore`, `test`, `docs`, `style`.

## Validações antes de todo `git push`

Antes de executar qualquer `git push`, rode obrigatoriamente as validações abaixo na ordem indicada.
Se qualquer etapa falhar, corrija o problema antes de prosseguir com o push.

```bash
# 1. Lint
ruff check .
ruff format --check .

# 2. Type check
mypy .

# 3. Testes
pytest -v --tb=short
```

> Não é necessário rodar `pip-audit` nem o build completo localmente — essas etapas
> são cobertas pela pipeline do GitHub Actions após o push.
