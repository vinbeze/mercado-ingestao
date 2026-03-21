# Instruções do Projeto

## Variáveis de Ambiente

- Nunca leia arquivos `.env` (`.env`, `.env.local`, `.env.production`, etc.)
- Assuma que todas as variáveis de ambiente já estão preenchidas e configuradas corretamente
- Para saber quais variáveis o projeto utiliza, leia o `.env.example`

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
