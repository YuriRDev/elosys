## Context

O projeto usa `uv.lock` e `web/package-lock.json`. Os testes Python atuais usam fixtures. Ruff passou no backend analisado. O frontend utiliza `better-sqlite3`, um módulo nativo, e carrega fontes via Next.js; sua combinação de Node, build e runtime precisa ser validada.

## Goals / Non-Goals

Proteger contribuições nos sistemas usados por quem instala o projeto. Fora do escopo: benchmark dos 11,4 GB, execução dos coletores reais e testes dependentes de DeepSeek ou Apify.

## Technical Approach

- Matrix Python: Ubuntu, macOS e Windows, Python 3.12, `uv sync --locked`, pytest e Ruff.
- Job web em Linux: `npm ci`, lint, TypeScript, build e teste de navegação/API com Playwright e SQLite sintético.
- Reproduzir primeiro o build e fixar uma versão de Node compatível com Next.js e `better-sqlite3`; documentar a versão verificada, sem assumir compatibilidade de prebuilds nativos.
- Gerar fixture a partir do schema real com candidatura, pessoa física doadora/fornecedora e proveniência. Exportar `ELOSYS_DB_PATH` para a aplicação de teste.
- Smoke tests iniciais: carregar a página, encontrar candidato por nome, encontrar pessoa física pelo índice e consultar tabela financeira.
- Usar `pull_request` e `push` em main, `permissions: contents: read`, timeout e concurrency por branch/PR. Evitar `pull_request_target` executando código do contribuidor com privilégios.
- Downloads de dependências e fontes de build são separados dos dados testados. A execução dos testes não consulta TSE, BrasilAPI, Apify ou DeepSeek.
- Publicar screenshots e logs somente quando testes web falharem. Não incluir a base real ou segredos nesses artefatos.

## Risks / Trade-offs

A matriz aumenta minutos de CI e pode depender de disponibilidade de runners. O build web ainda não foi executado nesta rodada; falhas existentes devem ser reproduzidas e corrigidas em escopo explícito, sem exclusões silenciosas dos checks.

## Migration Plan

Verificar o pipeline localmente antes de versionar o workflow. Publicar um PR independente com logs de execução. Configuração de branch protection é uma decisão do mantenedor, posterior ao workflow funcionar.
