# Próximas melhorias do Elosys

Propostas de 2026-10-03 (BRT) para revisão do mantenedor. Base analisada: `ca4de23`.

## Prioridades

| Ordem | Proposta | Resultado para o usuário | Esforço estimado |
| --- | --- | --- | --- |
| 1 | [Índice de busca](changes/rebuild-person-search-index/proposal.md) | Buscar doadores e fornecedores sem copiar SQL do README | Pequeno a médio |
| 2 | [Diagnóstico local](changes/add-database-doctor/proposal.md) | Descobrir problemas de instalação e dados com uma orientação acionável | Médio |
| 3 | [CI com fixtures](changes/add-fixture-ci/proposal.md) | Verificar contribuições em Linux, macOS e Windows | Médio |
| 4 | [Exportação auditável](changes/export-finance-evidence/proposal.md) | Reutilizar resultados financeiros com filtros e fontes verificáveis | Médio a grande |

As estimativas são relativas e não representam prazos. O próximo PR recomendado é `rebuild-person-search-index`.

## Evidências observadas

- `README.md`, etapa 3, exige SQL manual para atualizar `pessoa_fisica_search`.
- `elosys/schema.sql` cria o índice, mas `elosys/tse/accounts.py` não o preenche; a busca por nomes em `web/src/lib/queries.ts` depende dele.
- O CLI tem `verify`, que rebaixa fontes, mas não possui um diagnóstico local rápido.
- `signal_actor` e `signal_evidence` usam referências polimórficas; verificar somente foreign keys não cobre todos esses vínculos.
- Não há workflow em `.github/`; `web/package.json` não possui comando de testes.
- A tabela financeira e o grafo não apresentam exportação auditável nos componentes analisados. O grafo já aceita o parâmetro `add`, portanto isso não deve ser descrito como ausência completa de links de entrada.
- Ruff passou em `elosys/` e `tests/` na base analisada. O build do frontend ainda precisa ser reproduzido antes de definir sua configuração de CI.

## Escopo acordado

Preservar Python, SQLite, Next.js e o schema existente. Usar comando manual e atualização automática do índice após coleta bem-sucedida. O diagnóstico será rápido por padrão, com auditoria profunda opcional. A CI cobrirá Python nos três sistemas e frontend em Linux. O primeiro recurso investigativo será exportação com fontes, hashes e filtros.

Os PRs [#5](https://github.com/YuriRDev/elosys/pull/5), [#6](https://github.com/YuriRDev/elosys/pull/6) e [#7](https://github.com/YuriRDev/elosys/pull/7) permaneciam abertos nesta análise. As novas implementações devem partir de um checkout atualizado e conferir essas dependências antes de começar.

## Uso

Cada mudança tem proposta, design, requisitos com cenários e tarefas pendentes. São propostas para revisão; as implementações permanecem pendentes.

Validação com OpenSpec 1.14.0:

```bash
npm exec --yes --package=@fission-ai/openspec@1.14.0 -- openspec validate --changes --strict --no-interactive
```

Veja também [skills recomendadas](skills.md) e o [backlog completo](feature-backlog.md), que inclui novas regras investigativas, comparação entre eleições e persistência de investigações.

## Backlog completo

Além das quatro propostas iniciais, há dez propostas para investigações editáveis no navegador, relatórios PDF/Excel, comparação, três novas regras, contexto dos dados, usabilidade e automações. O [backlog completo](feature-backlog.md) organiza as 14 mudanças por impacto, esforço e dependências. As implementações permanecem pendentes.
