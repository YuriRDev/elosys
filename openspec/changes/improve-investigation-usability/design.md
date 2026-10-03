## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Auditar os fluxos existentes e corrigir problemas comprovados de filtros, navegação do grafo, responsividade, foco e comunicação dos estados.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Reproduzir problemas antes de editar; alguns fluxos já utilizam cancelamento de requisições e links de entrada no grafo. Preservar esses comportamentos.
- Busca e filtros devem comunicar o escopo efetivo e permitir limpeza previsível. Resultado vazio, fonte não disponível e erro de banco são estados distintos.
- No grafo, priorizar foco na seleção, resumo textual das relações e limites explícitos de expansão. O resultado visual não substitui a evidência consultável.
- Fluxos críticos devem funcionar por teclado com foco visível e nomes acessíveis. Não criar atalhos que conflitem com digitação nos inputs.
- Verificar tamanhos de viewport e toque, tabelas largas e conteúdos de origem. A tabela pode ter rolagem horizontal identificada, sem esconder controles fora da tela.
- Medir operações caras e legibilidade com fixtures de grafos densos. Só incluir mudanças cuja necessidade seja demonstrada por inspeção ou testes.

## Dependencies and Delivery

Usa a CI de fixtures e skills de testes web/acessibilidade. Auditoria decide quais correções entram; os cenários são critérios para os fluxos, não alegações de bugs já comprovados.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
