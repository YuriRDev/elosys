# Backlog ampliado do Elosys

Backlog de contribuição de 2026-10-03 (BRT), totalizando **14 mudanças OpenSpec propostas** para revisão do mantenedor. As implementações permanecem pendentes.

## Escolhas registradas

- Incluir investigações, comparação e novas regras.
- Comparar finanças e patrimônio, relações em comum e evolução entre eleições.
- Explorar doações repetidas/fracionadas, concentração de fornecedores e empresas recentes, sempre com critérios e evidências explícitos.
- Salvar investigações no navegador para retomar a edição. Exportar relatórios em **PDF e Excel (.xlsx)**.
- Melhorar busca/filtros, grafo, mobile e acessibilidade após auditoria dos fluxos existentes.
- Explicar cobertura, cálculos e relações determinísticas ou apenas possíveis.
- Incluir pipeline sequencial, API documentada e consultas em lote.
- Manter um backlog amplo e organizado por impacto, esforço e dependências, com PRs pequenos nas primeiras entregas e recursos maiores divididos em fases.

## Priorização

O esforço é relativo, não uma estimativa de prazo. As ondas organizam dependências; propostas independentes podem avançar separadamente.

| Onda | Proposta | Impacto esperado | Esforço | Dependência principal |
| --- | --- | --- | --- | --- |
| 0 | [Índice de busca](changes/rebuild-person-search-index/proposal.md) | Busca completa sem SQL manual | Pequeno/médio | Contas coletadas |
| 0 | [Diagnóstico local](changes/add-database-doctor/proposal.md) | Identificar instalação e referências inconsistentes | Médio | Leitura protegida do PR #6 |
| 0 | [CI com fixtures](changes/add-fixture-ci/proposal.md) | Evitar regressões nos três sistemas | Médio | Baseline do frontend |
| 1 | [Contexto dos dados](changes/clarify-data-context/proposal.md) | Entender cobertura, fontes, cálculos e vínculos possíveis | Médio | Metadados e diagnóstico |
| 1 | [Usabilidade](changes/improve-investigation-usability/proposal.md) | Melhorar filtros, grafo, teclado e celular | Médio, em PRs pequenos | Auditoria e testes web |
| 1 | [Concentração de fornecedores](changes/add-supplier-concentration-signal/proposal.md) | Explicar concentração dos gastos | Médio | Elegibilidade e parâmetros definidos |
| 2 | [Comparação de candidatos](changes/compare-candidates/proposal.md) | Comparar métricas, relações e histórico com contexto | Grande, em fases | Cobertura e consultas limitadas |
| 2 | [Exportação financeira](changes/export-finance-evidence/proposal.md) | Reutilizar resultados com fontes e filtros | Médio/grande | Contrato financeiro |
| 2 | [Investigação e PDF/Excel](changes/add-investigation-workspace/proposal.md) | Retomar trabalho e produzir relatórios verificáveis | Grande, em fases | Contexto e exportação |
| 3 | [Padrões de doações](changes/add-donation-pattern-signal/proposal.md) | Explorar repetição e distribuição temporal | Médio/grande | Calibração com amostra |
| 3 | [Empresas recentes](changes/add-recent-company-signal/proposal.md) | Relacionar abertura e contratação com cobertura explícita | Médio/grande | Cadastro e datas oficiais |
| 3 | [Pipeline sequencial](changes/orchestrate-local-pipeline/proposal.md) | Executar etapas e localizar falhas | Médio/grande | Auditoria dos resets, índice e diagnóstico |
| 4 | [API documentada](changes/document-public-query-api/proposal.md) | Consumir dados por scripts com contratos estáveis | Médio/grande | Filtros, limites e snapshot |
| 4 | [Consultas em lote](changes/add-batch-entity-queries/proposal.md) | Pesquisar listas preservando identidade e ambiguidades | Médio | Resolução e relatórios |

## Recurso central: investigação com relatórios

Fluxo proposto: buscar entidades → selecionar registros/evidências → adicionar notas → salvar no navegador → retomar → exportar PDF ou XLSX.

O PDF atende leitura e compartilhamento, com contexto, fontes e tabelas verificadas visualmente. O XLSX atende análise, com abas de resumo, registros, fontes e notas. Documentos com zeros iniciais permanecem texto. Anotações não viram dados oficiais ou fórmulas executáveis.

A exportação financeira CSV/JSON anterior continua sendo um contrato de dados, diferente do relatório da investigação. PDF/XLSX não serão apresentados como backup editável completo; a retomada acordada é pelo armazenamento do navegador.

## Critérios que atravessam as propostas

- Preservar Python, SQLite, Next.js e schema existente.
- Não juntar pessoas apenas pelo nome ou promover correspondência mascarada a identidade confirmada.
- Distinguir ausência de dados de zero; indicar cobertura e contexto de cada comparação.
- Cada indício precisa de cálculo reproduzível, parâmetros, versão e evidências. Ele não comprova irregularidade.
- Parâmetros das novas regras ainda exigem definição e calibração antes do código. Exemplos nos cenários são fixtures, não limites legais ou defaults aprovados.
- Consultas e exports têm limites explícitos e não truncam dados silenciosamente.
- Fixtures e testes reais precedem implementação; PDF/XLSX também passam por verificação do arquivo gerado.
- Nenhuma proposta publica um site, agenda jobs ou utiliza APIs pagas implicitamente.

## Próximo passo recomendado

Implementar primeiro `rebuild-person-search-index`, já especificado, em um PR pequeno. Depois consolidar diagnóstico/CI e o contexto dos dados. A comparação e a investigação com PDF/Excel são as principais evoluções de produto; seu escopo será entregue por partes.

As correções dos PRs #5–#7 continuam como dependências a conferir no checkout atualizado. Um novo turno de implementação deve começar pelos arquivos da mudança escolhida, sem reler todo o backlog.
