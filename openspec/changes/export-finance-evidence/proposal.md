## Why

A tabela financeira permite explorar resultados, mas os componentes analisados não oferecem exportação que preserve os filtros e a origem dos registros. Pesquisadores precisam reutilizar os dados e permitir que terceiros confiram de onde vieram.

## What Changes

- Exportar a consulta financeira filtrada como CSV ou JSON.
- Incluir proveniência, URLs de origem, hashes disponíveis e filtros efetivos.
- Registrar limite, versão do formato e data de geração; recusar exportações acima do limite em vez de truncar silenciosamente.
- Adicionar ação de exportação na tabela financeira com tratamento explícito de erros.

## Capabilities

### New Capabilities
- `finance-evidence-export`: exportação limitada de dados financeiros acompanhada de contexto e fontes.

### Modified Capabilities
Nenhuma spec canônica existente.

## Impact

Novo endpoint e integração na tabela financeira, com testes e fixtures. Utiliza tabelas de proveniência existentes; não cria tabelas ou uma conta de usuário. A primeira versão cobre doações e despesas, deixando grafos, sinais e avaliações de IA para outra proposta.
