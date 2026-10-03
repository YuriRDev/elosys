## Purpose

A reconstrução exige muitos comandos independentes. O usuário quer executá-los em sequência com relatório claro da etapa que falhou.

## ADDED Requirements

### Requirement: Validate before running
O sistema SHALL validar o plano completo antes de iniciar suas etapas.

#### Scenario: Plan contains an unknown step
- GIVEN um plano com uma etapa válida e outra inexistente
- WHEN o usuário tenta executá-lo
- THEN o plano é recusado sem executar a primeira etapa

### Requirement: Stop after failure
O sistema SHALL interromper as etapas seguintes quando uma etapa falhar.

#### Scenario: Second step fails
- GIVEN um plano de três etapas
- WHEN a segunda etapa falha
- THEN a terceira não é executada e o relatório identifica os três estados

### Requirement: Preview without execution
O sistema SHALL permitir visualizar ordem e escopo sem executar coletores.

#### Scenario: Dry run with selected years
- GIVEN um plano com coleta de contas restrita a 2022
- WHEN o usuário solicita dry-run
- THEN vê etapas, anos e responsabilidades sem escrita no banco ou download
