## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Comparar de dois a quatro candidatos com contexto eleitoral explícito, métricas compatíveis, doadores/fornecedores em comum e séries históricas.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Usar person_id e candidaturas específicas; não conciliar pessoas apenas por nome nem CPF mascarado.
- Exibir eleição, cargo, UF e circunscrição em cada coluna. Comparação fora do mesmo contexto deve identificar diferenças; não produzir ranking de risco a partir de totais brutos.
- Separar receitas, despesas contratadas e pagamentos, sem tratá-los como medidas equivalentes. Bens são declarações daquele registro eleitoral.
- Diferenciar zero confirmado, valor ausente e fonte não coletada. Não preencher lacunas de 2014/2016 com zero quando não houver contas disponíveis.
- Relações em comum exigem identificadores compatíveis. Mostrar tipo da contraparte, transações e fontes; coincidência de nome não comprova identidade.
- Mudanças patrimoniais apresentam valores declarados e contexto; não alegar enriquecimento incompatível sem renda e critérios que a base não oferece. Valores nominais entre anos devem ser rotulados como nominais.
- Limitar candidatos e listas de relações; reutilizar agregações e medir planos SQL com fixtures antes de comparar desempenho na base completa.

## Dependencies and Delivery

Depende do índice nominal e do contexto de cobertura. Pode reutilizar exportação financeira e relatórios de investigação em uma fase seguinte.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
