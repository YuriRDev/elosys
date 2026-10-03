## Purpose

O usuário quer explorar empresas abertas perto da eleição, preservando a distinção entre dado cadastral disponível e cobertura ainda incompleta.

## ADDED Requirements

### Requirement: Date-based evidence
O sistema SHALL comparar datas válidas de abertura e contratação usando parâmetros registrados.

#### Scenario: Recently opened supplier
- GIVEN uma empresa aberta em 2026-08-01 e contrato em 2026-08-11
- WHEN a regra usa uma janela de 30 dias na fixture
- THEN informa intervalo de 10 dias e referencia as duas fontes

### Requirement: Unknown registry coverage
O sistema SHALL distinguir cadastro ausente de ausência de indício.

#### Scenario: Supplier without opening date
- GIVEN um fornecedor sem data de abertura coletada
- WHEN a regra é executada
- THEN o caso é contado como cobertura insuficiente, sem conclusão de que a empresa é antiga

### Requirement: Official election date for electoral proximity
O sistema SHALL exigir a data oficial do pleito para apresentar um indício de proximidade à eleição.

#### Scenario: Election date unavailable
- GIVEN uma empresa com abertura e contratação conhecidas, mas sem data oficial do pleito disponível
- WHEN a regra avalia proximidade eleitoral
- THEN esse cálculo fica indisponível
- AND eventual intervalo até a contratação é identificado como uma análise distinta
