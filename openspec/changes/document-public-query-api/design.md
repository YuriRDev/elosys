## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Definir API versionada de leitura com busca, entidades, finanças e proveniência, parâmetros validados e exemplos reprodutíveis.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- A primeira versão cobre busca, perfil básico, finanças paginadas e proveniência. Preservar os endpoints usados pela UI até uma migração explícita.
- Validar parâmetros, tipos de entidade e limites; erro de entrada é distinto de resultado vazio ou base indisponível. Não expor mensagens internas de SQL ou caminhos locais.
- Reutilizar a normalização financeira e os filtros efetivos dos exports. Identificadores mascarados e vínculos possíveis não são promovidos a identidades confirmadas.
- Documentar versão do contrato, unidades monetárias, paginação, contexto do snapshot e campos opcionais. Metadados de versão não devem ser apresentados como hash criptográfico do banco sem cálculo comprovável.
- Limitar páginas e consultas de grafos. Definir comportamento de cache e snapshot, medindo SQLite síncrono para evitar travar requisições concorrentes.
- Exemplos usam fixture pública pequena e não dependem da base distribuída. O usuário hospeda a API se desejar; nenhuma implantação é feita por esta proposta.

## Dependencies and Delivery

Depende de contratos de filtros/proveniência e CI. O desenho de limites e versão do snapshot deve preceder o código.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
