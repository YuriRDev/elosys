## Context

`/api/finance` já expressa escopo, direção, entidade, filtros e ordenação. As linhas financeiras referenciam `parse`, `collection`, `source` e, quando disponível, `collection_file`. A fonte pode republicar arquivos: os hashes registrados não garantem disponibilidade futura do conteúdo antigo.

## Goals / Non-Goals

Compartilhar resultados financeiros com contexto verificável. Fora do escopo: exportação integral do banco, novas fontes, classificação de fraude e persistência de investigações.

## Technical Approach

- Propor GET `/api/finance/export` com os filtros financeiros existentes e `format=csv|json`. Reutilizar a mesma normalização de filtros e ordenação, evitando divergência entre tabela e exportação.
- Definir primeira versão limitada a doações e despesas. Pagamentos ou vínculos derivados exigem contratos próprios antes de serem adicionados.
- Usar limite de 5.000 linhas; buscar no máximo limite + 1 para identificar excesso. Inputs inválidos retornam 400; excesso retorna 422 com orientação para restringir filtros.
- JSON: `format_version`, `generated_at` em UTC, filtros pedidos e efetivos, escopo do export, registros e fontes deduplicadas. Valores financeiros em centavos inteiros.
- CSV: colunas financeiras e colunas explícitas para filtros efetivos, fonte, URL, data da coleta, hash da coleta e hash do arquivo quando disponível. Preservar o documento conforme exibido, sem novas inferências de identidade.
- Distinguir hashes da fonte de qualquer checksum futuro do export. Não calcular hash do banco de 11,4 GB durante a solicitação nem inventar hashes ausentes.
- Obter registros e proveniência em um snapshot de leitura consistente. Não iniciar coleta ou chamadas pagas.
- Usar serialização CSV adequada e proteger células textuais que poderiam ser interpretadas como fórmulas por planilhas. Testar aspas, quebras de linha, Unicode e nomes iniciados por caracteres de fórmula.
- Falta de proveniência deve causar erro explícito, sem apresentar um export incompleto como auditável.

## Risks / Trade-offs

Exportações grandes aumentam CPU e bloqueio das consultas SQLite síncronas. O limite deve ser medido com fixtures e depois na base real. O arquivo representa os dados e metadados daquele snapshot; não certifica uma acusação ou a reprodução do material original.

## Migration Plan

Começar pelo contrato e testes do backend, depois integrar a ação na tabela. Usar a CI proposta e conferir conflitos com os PRs existentes de consultas. Publicar como recurso independente após priorizar instalação, busca e diagnóstico.
