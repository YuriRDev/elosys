## Why

Quem instala o Elosys não possui uma verificação local que diferencie arquivo ausente, schema incompatível e problemas de dados. O comando `verify` rebaixa fontes e atende a outro objetivo.

## What Changes

- Adicionar `elosys doctor --db ...`, com saída humana e `--json`.
- Verificar rapidamente arquivo, abertura de leitura, tabelas e disponibilidade da busca.
- Oferecer `--deep` para integridade SQLite, foreign keys e referências de proveniência e sinais.
- Fornecer códigos de saída e orientações acionáveis, sem escrever no banco.

## Capabilities

### New Capabilities
- `database-doctor`: diagnóstico local com verificações rápidas e auditoria profunda opcional.

### Modified Capabilities
Nenhuma spec canônica existente.

## Impact

Novo módulo de diagnóstico, integração no CLI, testes e documentação. Não altera schema ou dados. Depende da proteção de leitura do PR #6 ou de solução equivalente já integrada ao projeto.
