## Purpose

O usuário quer identificar campanhas cujos gastos se concentram em poucas contrapartes e entender como essa concentração foi calculada.

## ADDED Requirements

### Requirement: Explain concentration calculation
O sistema SHALL mostrar os valores usados no cálculo da concentração.

#### Scenario: Supplier receives eighty percent
- GIVEN contratos elegíveis de 80000 centavos para um fornecedor e 20000 para outro na mesma campanha
- WHEN a concentração é calculada
- THEN o primeiro fornecedor representa 80% do total de 100000 centavos

### Requirement: No ratio without denominator
O sistema SHALL indicar cálculo indisponível quando não houver denominador elegível positivo.

#### Scenario: Campaign without eligible expenses
- GIVEN uma campanha sem despesas elegíveis positivas
- WHEN a regra a avalia
- THEN não produz participação infinita nem um indício baseado em divisão por zero
