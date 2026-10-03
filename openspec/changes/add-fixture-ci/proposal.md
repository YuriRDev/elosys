## Why

Os testes atuais podem ser executados localmente, mas o repositório não possui workflow versionado para verificar contribuições. O frontend também não oferece comando de testes, deixando fluxos centrais sujeitos a regressões.

## What Changes

- Executar Python 3.12, pytest e Ruff em Linux, macOS e Windows.
- Executar instalação pelo lockfile, lint, checagem de tipos, build e smoke tests do frontend em Linux.
- Gerar banco sintético para os testes da interface.
- Executar em PRs e alterações de main, com permissões mínimas e cancelamento de runs superseded.

## Capabilities

### New Capabilities
- `fixture-ci`: validação automática do backend e frontend sem base completa ou APIs pagas.

### Modified Capabilities
Nenhuma spec canônica existente.

## Impact

Afeta `.github/workflows/`, ferramentas de fixtures e testes web. Dependências e scripts web podem precisar de ajustes após reprodução do build atual. Não depende de mudanças de schema; incluir as regressões dos PRs #5–#7 quando forem integradas.
