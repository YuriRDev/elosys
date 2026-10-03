## Why

A instalação reconstruída pelo usuário depende de um bloco SQL manual para permitir busca nominal de doadores e fornecedores. Esquecer essa etapa deixa resultados ausentes ou desatualizados, embora o índice exista no schema.

## What Changes

- Adicionar `elosys rebuild-search --db ...`, com contagem dos CPFs indexados.
- Atualizar o índice após `tse-accounts` terminar com sucesso.
- Reconstruir o índice em transação, removendo entradas antigas e preservando o índice anterior em caso de falha durante a reconstrução.
- Substituir o bloco SQL manual do README pelo comando.

## Capabilities

### New Capabilities
- `person-search-index`: reconstrução e atualização automática da busca nominal de pessoas físicas.

### Modified Capabilities
Nenhuma spec canônica existente.

## Impact

Afeta `elosys/cli.py`, um novo módulo de busca, a integração com `tse-accounts`, testes e README. Usa a tabela FTS5 existente. Não exige novo schema ou download da base. A implementação deve evitar o arquivo de consultas alterado pelo PR #1.
