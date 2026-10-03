## Purpose

O usuário quer consultar o Elosys a partir de scripts com contratos documentados, em vez de depender dos detalhes internos da interface.

## ADDED Requirements

### Requirement: Documented read contract
A API SHALL fornecer respostas de leitura conforme contrato versionado.

#### Scenario: Paginated financial query
- GIVEN uma consulta financeira com filtros válidos
- WHEN um cliente pede uma página
- THEN recebe registros, paginação, filtros efetivos e contexto documentado

### Requirement: Validate query inputs
A API SHALL distinguir parâmetros inválidos de consultas válidas sem resultados.

#### Scenario: Invalid scope
- GIVEN um escopo que não faz parte do contrato
- WHEN o cliente envia a requisição
- THEN recebe erro de entrada documentado, sem ser tratado como busca vazia
