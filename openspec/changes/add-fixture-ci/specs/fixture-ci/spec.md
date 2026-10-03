## Purpose

Verificar contribuições com dados sintéticos e resultados reproduzíveis nos sistemas suportados.

## ADDED Requirements

### Requirement: Cross-platform Python validation
O projeto SHALL executar seus testes Python e lint em Linux, macOS e Windows para cada PR.

#### Scenario: Contributor opens a PR
- GIVEN um PR com alteração no backend
- WHEN o workflow é iniciado
- THEN os três sistemas instalam as dependências fixadas e executam pytest e Ruff
- AND uma falha de teste ou lint deixa o respectivo job com status de falha

### Requirement: Frontend validation with synthetic database
O projeto SHALL verificar o frontend em Linux usando banco sintético para seus fluxos de leitura.

#### Scenario: Search regression
- GIVEN uma fixture com candidato e pessoa física doadora indexada
- WHEN a busca deixa de retornar um desses registros esperados
- THEN o smoke test falha e disponibiliza evidência para diagnóstico

#### Scenario: Build or types fail
- GIVEN um PR que introduz erro de tipo ou build
- WHEN o job frontend executa seus checks
- THEN o job falha antes de declarar a contribuição validada

### Requirement: Tests without external datasets or paid APIs
O projeto SHALL executar a validação sem baixar a base distribuída ou consultar serviços externos de dados.

#### Scenario: Fork without API credentials
- GIVEN um PR de fork sem tokens de DeepSeek ou Apify e sem banco pré-construído
- WHEN a CI executa
- THEN a validação usa fixtures locais e não depende desses recursos

### Requirement: Observable failures
O projeto SHALL preservar logs e evidências úteis das falhas dos testes web.

#### Scenario: UI test fails
- GIVEN uma falha ao carregar ou consultar a interface com a fixture
- WHEN o job termina
- THEN o mantenedor consegue consultar logs e screenshots do teste que falhou
