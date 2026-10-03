## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Adicionar análise configurável de repetição e distribuição temporal de doações por doador, campanha e eleição, sem declarar violação legal automaticamente.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Definir agrupamento, janela temporal, contagem mínima e agregação por campanha/eleição em parâmetros versionados. Os defaults serão calibrados com amostra e documentados antes de implementar; não inventar limites legais.
- Manter contagem, soma em centavos, datas e recibos envolvidos. Distinguir duplicação de importação de múltiplas transações legítimas.
- Registros sem data ou identificação suficiente não recebem uma identidade inferida apenas pelo nome; a cobertura excluída é informada.
- Repetição não comprova fracionamento irregular. Apresentar fatos e alternativas como parcelas legítimas, devoluções e correções; sem veredito automático de fraude.
- Cada execução registra regra, versão, parâmetros e evidências. Reexecução deve substituir somente resultados pertencentes a essa regra, respeitando revisões e referências existentes.
- Não iniciar o código de detecção enquanto agrupamentos e parâmetros não forem definidos e testados em exemplos positivos e negativos.

## Dependencies and Delivery

Depende de contas, diagnóstico e contexto dos indícios. Calibração dos parâmetros é uma tarefa aberta; esta proposta não autoriza usar thresholds arbitrários.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
