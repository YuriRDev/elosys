## Context

A receita SQL já documentada agrupa por CPF as pessoas físicas presentes em doações e despesas. O frontend utiliza `pessoa_fisica_search` para busca nominal; esse índice é derivado, sem criar identidade em `people`.

## Goals / Non-Goals

Automatizar a etapa existente e permitir recuperação manual. Preservar seus filtros e a seleção determinística de nome. Fora do escopo: novas regras de identidade, busca de empresas e migração de banco.

## Technical Approach

- Criar função compartilhada que reconstrói `pessoa_fisica_search` a partir das tabelas atuais.
- Utilizar savepoint ou transação que englobe limpeza e preenchimento do índice, respeitando transações do chamador. Propagar falhas depois de rollback.
- Preservar a receita documentada: pessoa física sem vínculo de empresa, documento com 11 caracteres, nome não nulo; agrupar por CPF e selecionar `max(name)`.
- O comando manual abre banco existente em modo de escrita; não inicializa um banco vazio em caminho incorreto.
- Integrar a mesma função após retorno bem-sucedido de `accounts.run`. Uma falha de indexação produz saída não zero e orientação de recuperação.
- Informar contagem e tempo da etapa. O processamento deve ocorrer no SQLite, sem carregar milhões de pessoas em listas Python.

## Risks / Trade-offs

A agregação percorre tabelas grandes e pode usar espaço temporário. Não promete tempo máximo sem benchmark na base real. A transação protege apenas o índice: os coletores continuam com seus próprios commits. Se a coleta ou indexação falhar, os dados e o índice podem representar estados diferentes; o comando deve comunicar essa condição, sem declarar o pipeline concluído.

## Migration Plan

Usuários de bancos existentes executam `rebuild-search` uma vez. Novas coletas bem-sucedidas atualizam o índice automaticamente. O PR pode ser independente das três correções anteriores; conferir a versão atual antes de implementar.
