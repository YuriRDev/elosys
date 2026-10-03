## Purpose

Existem históricos e rankings, mas o usuário quer comparação lado a lado de finanças, patrimônio, relações em comum e evolução entre eleições.

## ADDED Requirements

### Requirement: Comparable financial measures
O sistema SHALL distinguir receitas, despesas contratadas e pagamentos na comparação.

#### Scenario: Different expense and payment amounts
- GIVEN uma candidatura com despesa contratada de 10000 centavos e pagamento de 6000 centavos
- WHEN ela é comparada com outra candidatura
- THEN os dois valores aparecem em métricas distintas

### Requirement: Coverage-aware history
O sistema SHALL distinguir ausência de dados de valores iguais a zero.

#### Scenario: Election without accounts collection
- GIVEN patrimônio disponível em uma eleição sem contas coletadas
- WHEN o usuário compara a série histórica
- THEN o patrimônio aparece e as finanças são marcadas como indisponíveis

### Requirement: Shared counterparties
O sistema SHALL mostrar relações em comum apenas quando a identidade da contraparte é compatível.

#### Scenario: Homonymous donors
- GIVEN dois doadores com o mesmo nome e documentos diferentes
- WHEN o usuário consulta doadores em comum
- THEN eles não são unidos somente pelo nome
