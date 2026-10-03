## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Exibir contexto de cobertura, evidências dos cálculos e distinção entre identidade confirmada pela fonte, vínculo possível e anotação do usuário.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Usar metadados de coleta e relatórios disponíveis. Presença de registros em um ano não comprova coleta completa; relatórios ausentes produzem estado desconhecido.
- Mostrar data de acesso à fonte separada de data do fato e atualização do arquivo, quando conhecida. Não classificar uma fonte antiga como errada apenas pela idade.
- Reutilizar proveniência por registro e parâmetros versionados da regra para explicar os cálculos. Revisão por LLM permanece identificada como avaliação auxiliar.
- Diferenciar identidade determinística, vínculo possível e anotação. Ausência de informação não produz confiança alta por padrão; evitar um score numérico inventado.
- As consultas de metadados não devem varrer milhões de linhas a cada interação. Definir cache vinculado ao snapshot e medir seu custo.
- Sinais calculados sobre fontes anteriores devem indicar o contexto conhecido; o sistema não pode prometer detectar toda obsolescência sem metadados suficientes.

## Dependencies and Delivery

Depende de diagnóstico e proveniência disponíveis; serve de base para comparação, relatórios e novas regras.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
