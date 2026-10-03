## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Criar investigações no navegador com título, notas, entidades e evidências selecionadas. Permitir retomada local e exportação em PDF e XLSX com fontes e filtros.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Persistir no navegador um documento versionado, com ID da investigação, referências às entidades e evidências, filtros, notas e metadados do snapshot. Validar dados lidos antes de restaurar a interface.
- Notas do usuário são anotações, separadas dos dados oficiais e dos indícios calculados. Não entram na cadeia de proveniência como uma fonte governamental.
- Ao reabrir, verificar referências contra o banco atual; indicar entidades ou evidências indisponíveis e diferenças de snapshot, sem reapontar silenciosamente IDs reutilizados.
- Não afirmar que apenas encontrar o mesmo ID comprova que a evidência é idêntica. Preservar identificadores estáveis e metadados de origem suficientes para detectar mudanças; casos sem confirmação ficam pendentes de revisão.
- PDF inclui contexto, seções, tabelas legíveis, fontes, hashes disponíveis, filtros e limitações; separar notas e fatos. XLSX inclui abas de resumo, registros, fontes e notas, com relações entre elas.
- No XLSX, documentos permanecem texto, valores monetários mantêm representação exata e nomes não viram fórmulas. Exportações têm limites explícitos; nenhum relatório é truncado silenciosamente.
- Selecionar bibliotecas compatíveis com o runtime após verificar documentação e fixtures reais. Não incluir hash inventado do banco ou substituir o hash da fonte pelo hash do relatório.
- Armazenamento local pode falhar ou ser removido pelo navegador. Informar falhas de gravação, manter a investigação atual utilizável e explicar que os arquivos exportados são relatórios, não backups editáveis completos.
- Dividir a entrega: edição/retomada local; relatório XLSX; relatório PDF com revisão visual das páginas.

## Dependencies and Delivery

Depende dos contratos de exportação financeira e contexto de evidências; a área de edição pode começar com referências já disponíveis. Validar os relatórios com arquivos sintéticos antes de publicar.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
