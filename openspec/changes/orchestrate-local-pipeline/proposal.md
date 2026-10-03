## Why

A reconstrução exige muitos comandos independentes. O usuário quer executá-los em sequência com relatório claro da etapa que falhou.

## What Changes

Adicionar execução declarativa de etapas selecionadas, preview, validação de parâmetros e relatório por etapa, interrompendo em falhas.

## Capabilities

### New Capabilities
- `local-pipeline`: Pipeline local sequencial.

### Modified Capabilities
Nenhuma spec canônica existente.

## Impact

Novo orquestrador CLI que reutiliza coletores e regras. Mantém um escritor SQLite, sem paralelizar escrita ou prometer rollback de todo o build.
