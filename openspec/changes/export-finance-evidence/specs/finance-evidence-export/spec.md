## Purpose

Permitir reutilização de resultados financeiros com filtros, contexto e fontes rastreáveis.

## ADDED Requirements

### Requirement: Export effective financial filters
O sistema SHALL exportar os resultados financeiros correspondentes aos filtros efetivos informados.

#### Scenario: Expense filter and ordering
- GIVEN despesas de duas eleições e filtro para uma eleição com ordenação por valor
- WHEN o usuário exporta a consulta
- THEN o arquivo contém somente as despesas da eleição selecionada na ordem solicitada
- AND registra os filtros efetivos usados

### Requirement: Source attribution
O sistema SHALL acompanhar cada registro exportado com a proveniência disponível em seu snapshot.

#### Scenario: CSV source file is known
- GIVEN um registro financeiro cujo parse referencia um CSV com hash registrado
- WHEN o usuário exporta esse registro
- THEN consegue identificar fonte, URL, data da coleta, hash da coleta e hash do CSV

#### Scenario: Provenance is inconsistent
- GIVEN um registro cuja proveniência obrigatória não pode ser resolvida
- WHEN o usuário solicita exportação auditável
- THEN recebe erro explícito sem arquivo apresentado como completo

### Requirement: Explicit export size limit
O sistema SHALL recusar consultas acima de 5.000 linhas sem produzir truncamento silencioso.

#### Scenario: Query exceeds limit
- GIVEN uma consulta com 5.001 linhas elegíveis
- WHEN o usuário solicita o export
- THEN recebe status 422 com orientação para restringir filtros
- AND nenhum arquivo parcial é apresentado como exportação completa

### Requirement: Safe CSV serialization
O sistema SHALL serializar campos textuais em CSV sem transformá-los em fórmulas executáveis de planilha.

#### Scenario: Formula-like counterparty name
- GIVEN um nome de contraparte iniciado por `=` e contendo aspas e quebra de linha
- WHEN o usuário exporta CSV
- THEN o campo permanece uma célula textual corretamente delimitada
- AND abrir a planilha não executa a expressão como fórmula

### Requirement: Exact monetary values
O sistema SHALL preservar valores financeiros em centavos inteiros no formato JSON.

#### Scenario: Centavos are preserved
- GIVEN uma despesa de 12345 centavos
- WHEN o usuário exporta JSON
- THEN o valor monetário exportado é o inteiro 12345
