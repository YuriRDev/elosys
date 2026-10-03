## Context

A base distribuída tem cerca de 11,4 GB. `signal_actor` e `signal_evidence` referenciam tabelas conforme o tipo e não têm foreign keys completas para esses vínculos. A correção de proveniência do PR #5 protege novas chamadas, mas não audita registros anteriores.

## Goals / Non-Goals

Diagnóstico local útil para instalação e investigação de inconsistências. Fora do escopo: correção automática, download de fontes e certificação da veracidade dos dados.

## Technical Approach

- Abrir conexão efetivamente somente leitura; caminho ausente produz erro sem criação de arquivo.
- Modo padrão inspeciona schema, tabelas necessárias à interface e presença do índice. Evitar varreduras integrais, `COUNT(*)` nas tabelas grandes e PRAGMAs de integridade.
- Se necessário, avaliar apenas uma amostra limitada e declarar sua cobertura. Índice vazio gera aviso e sugestão de `rebuild-search`; não prova, sozinho, ausência de dados elegíveis.
- `--deep` executa `integrity_check`, `foreign_key_check` e verificações por joins de referências polimórficas e de coerência entre coleta e arquivo de cada parse.
- Usar allowlist de tabelas e tipos. Nunca interpolar `signal_evidence.table_name` arbitrário em SQL.
- Retornar checks com `id`, `status` (`ok`, `warning`, `error`), descrição e ação sugerida. JSON também informa versão, modo e cobertura.
- Códigos: 0 sem erros impeditivos, inclusive avisos; 1 para diagnóstico com erro; 2 para argumentos inválidos. Sem reparos implícitos.

## Risks / Trade-offs

Auditoria profunda pode ser demorada. A saída rápida não comprova integridade total ou atualização do índice. Mesmo uma auditoria profunda não detecta toda referência semanticamente errada cujo ID ainda existe, nem comprova hashes sem obter o material original.

## Migration Plan

Implementar após integração do PR #6. Testar schema completo, schema parcial, banco corrompido e referências ausentes usando arquivos pequenos. Publicar instruções diferenciando `doctor`, `doctor --deep` e `verify`.
