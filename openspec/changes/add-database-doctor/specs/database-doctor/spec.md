## Purpose

Identificar problemas locais de instalação e consistência do banco com ações de recuperação explícitas.

## ADDED Requirements

### Requirement: Read-only diagnosis
O sistema SHALL diagnosticar o banco sem criar ou modificar seu conteúdo.

#### Scenario: Missing file
- GIVEN um caminho inexistente
- WHEN o usuário executa `elosys doctor --db PATH`
- THEN recebe erro de diagnóstico e orientação sobre o caminho
- AND nenhum banco novo é criado

#### Scenario: Database in delete journal mode
- GIVEN um banco existente em journal mode DELETE
- WHEN o diagnóstico termina
- THEN o conteúdo e o journal mode permanecem iguais

### Requirement: Bounded default checks
O sistema SHALL informar a cobertura limitada do diagnóstico padrão sem executar uma auditoria integral.

#### Scenario: Tables exist but index is empty
- GIVEN tabelas necessárias presentes e índice nominal vazio
- WHEN o usuário executa o diagnóstico padrão
- THEN recebe um aviso com o comando de reconstrução
- AND a saída não declara que o índice está atualizado ou que toda a base é íntegra

### Requirement: Optional deep consistency audit
O sistema SHALL oferecer auditoria profunda de integridade e referências quando `--deep` for informado.

#### Scenario: Evidence points to absent record
- GIVEN uma evidência de sinal apontando para registro inexistente de uma tabela permitida
- WHEN o usuário executa `doctor --deep`
- THEN o relatório identifica a referência inconsistente e termina com código 1

#### Scenario: Parse references file from another collection
- GIVEN um parse cujo arquivo pertence a uma coleta diferente da indicada no parse
- WHEN o usuário executa `doctor --deep`
- THEN o relatório identifica a inconsistência de proveniência

### Requirement: Machine-readable results
O sistema SHALL disponibilizar relatório JSON com status, cobertura e ações sugeridas.

#### Scenario: Schema incompatible with frontend
- GIVEN um banco que não contém uma tabela obrigatória
- WHEN o usuário executa `doctor --json`
- THEN recebe JSON válido com o nome da tabela ausente, status de erro e orientação de recuperação
- AND o processo termina com código 1
