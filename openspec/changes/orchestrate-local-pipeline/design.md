## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Adicionar execução declarativa de etapas selecionadas, preview, validação de parâmetros e relatório por etapa, interrompendo em falhas.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Selecionar etapas e anos explicitamente; validar nomes, dependências e parâmetros antes de executar a primeira etapa. Oferecer dry-run mostrando ordem e escopo de cada coletor.
- Os coletores são rewrite-only e possuem commits próprios. O relatório deve declarar tabelas/anos sob responsabilidade da execução; não prometer preservação ou rollback global inexistentes.
- Executar etapas de escrita em série. Não tentar acelerar o pipeline disparando múltiplos escritores SQLite.
- Interromper na primeira falha e registrar etapas concluídas, etapa com erro e não executadas. Retomada é uma execução explícita de etapas selecionadas, sem promessa de idempotência antes de verificar cada coletor.
- Atualizar busca após contas concluídas e executar diagnóstico conforme plano. Informar quais regras derivadas precisam ser refeitas após substituir as fontes.
- Usar sidecar JSON com versão e parâmetros sanitizados, sem tokens ou valores de variáveis secretas. Logs locais datados usam BRT; timestamps da proveniência no banco mantêm UTC.
- Etapas pagas são opcionais e nunca entram implicitamente em um plano padrão. Não agendar jobs externos ou publicar artefatos automaticamente.

## Dependencies and Delivery

Depende do índice e diagnóstico. Antes da implementação, reproduzir o ciclo de reset em banco já preenchido e documentar dependências reais entre coletores e dados derivados.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
