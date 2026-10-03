## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Relacionar a data de abertura registrada à data de contratos de campanha, com janela configurável, fontes e cobertura. Mostrar eleição como contexto, sem usar uma data presumida para toda candidatura.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Utilizar company_registry.opened_at e expense_date; mostrar o intervalo antes da contratação e o ano eleitoral correspondente.
- A janela e o valor mínimo devem ser definidos e calibrados antes da implementação. Data de eleição somente entra se houver uma fonte/campo confiável para aquele pleito.
- Para rotular um resultado como abertura próxima da eleição, exigir a data oficial do respectivo pleito e sua proveniência. Guardar esses metadados no contrato da execução sem alterar o schema. Sem essa data, a proximidade eleitoral fica indisponível; o intervalo até a contratação é uma análise distinta e explicitamente rotulada.
- Cadastro ausente ou data inválida significa desconhecido, não empresa antiga. Contabilizar cobertura elegível e casos excluídos.
- Data de abertura posterior ao contrato é inconsistência a investigar; não classificá-la como empresa recém-aberta válida.
- Vínculo usa CNPJ identificado, não similaridade de nome. Cada indício apresenta contrato e fonte cadastral separadamente.
- Empresa recente pode operar legitimamente; o resultado não equivale a empresa de fachada.

## Dependencies and Delivery

Depende do enriquecimento cadastral disponível, das contas e do contexto de cobertura. Reutiliza o modelo de sinais após definir parâmetros.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
