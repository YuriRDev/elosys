## Purpose

O usuário quer explorar séries de doações relacionadas, com critérios explícitos e evidências, além dos ciclos já detectados.

## ADDED Requirements

### Requirement: Reproducible temporal pattern
O sistema SHALL produzir resultados reproduzíveis para os parâmetros registrados.

#### Scenario: Repeated donations meet configured criteria
- GIVEN três doações válidas de um doador para uma campanha em uma janela que atende aos parâmetros da fixture
- WHEN a regra é executada duas vezes sobre o mesmo snapshot
- THEN o agrupamento e a soma das transações são iguais nas duas execuções

### Requirement: Evidence and interpretation
O sistema SHALL apresentar as transações e os critérios que originaram cada indício.

#### Scenario: Review a donation pattern
- GIVEN um indício produzido pela regra
- WHEN o usuário o consulta
- THEN pode conferir recibos, datas, valores, parâmetros e fontes
- AND o resultado não é apresentado como prova de irregularidade
