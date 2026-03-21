## Descrição

<!-- Descreva de forma objetiva o que essa mudança faz e por que é necessária -->

## Tipo de mudança

- [ ] `feature` — nova funcionalidade
- [ ] `fix` — correção de bug
- [ ] `refactor` — refatoração sem mudança de comportamento
- [ ] `docs` — documentação

## Branch de destino

- [ ] `develop` — para branches `feature/**` e `fix/**`
- [ ] `main` — para branches `release/**`

## Checklist

- [ ] Lint passou (`ruff check .` e `ruff format --check .`)
- [ ] Type check passou (`mypy .`)
- [ ] Build ok (entrypoint responde ao `mercado-nfe --help`)
- [ ] Security scan sem vulnerabilidades (`pip-audit`)
- [ ] Testes passando (`pytest -v --tb=short`)
- [ ] Sem código comentado ou prints de debug
- [ ] Se for release: merge de volta para `develop` foi feito
