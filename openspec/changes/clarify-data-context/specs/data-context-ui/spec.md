## Purpose

O usuário quer compreender anos e fontes disponíveis, o cálculo de cada indício e o grau de confirmação dos vínculos.

## ADDED Requirements

### Requirement: Explicit collection coverage
O sistema SHALL distinguir cobertura confirmada, parcial e desconhecida.

#### Scenario: Year has records but no completion report
- GIVEN registros de um ano sem relatório suficiente para comprovar coleta completa
- WHEN a cobertura é exibida
- THEN a interface não apresenta esse ano como integralmente coletado

### Requirement: Explain possible relationships
O sistema SHALL identificar vínculos cuja identidade não foi confirmada.

#### Scenario: Masked partner match
- GIVEN um vínculo de sócio fornecedor baseado em nome e dígitos mascarados
- WHEN o vínculo é apresentado
- THEN ele permanece rotulado como possível e mostra os critérios de correspondência

### Requirement: Explain signal origin
O sistema SHALL tornar acessíveis parâmetros e evidências de cada indício.

#### Scenario: Inspect a calculated signal
- GIVEN um indício e uma avaliação auxiliar por LLM
- WHEN o usuário consulta sua explicação
- THEN consegue distinguir cálculo da regra, fatos usados e avaliação do modelo
