## Purpose

Disponibilizar busca nominal de pessoas físicas presentes nas contas de campanha sem exigir SQL manual.

## ADDED Requirements

### Requirement: Manual index rebuild
O sistema SHALL oferecer `elosys rebuild-search --db PATH` para reconstruir o índice nominal usando os registros atuais.

#### Scenario: Donor and supplier share a CPF
- GIVEN um doador e um fornecedor com o mesmo CPF e nomes não nulos
- WHEN o usuário reconstrói o índice
- THEN existe uma entrada desse CPF com o nome escolhido pela regra documentada de `max(name)`
- AND a contagem informada considera esse CPF uma vez

#### Scenario: Excluded records and stale entries
- GIVEN empresas, registros sem nome e um CPF antigo ausente dos dados atuais
- WHEN o usuário reconstrói o índice
- THEN esses registros não aparecem no índice resultante

### Requirement: Automatic refresh after successful accounts collection
O sistema SHALL atualizar o índice após uma coleta de contas concluir com sucesso.

#### Scenario: Successful collection
- GIVEN uma coleta de contas que termina com novos doadores e fornecedores
- WHEN o comando termina com código zero
- THEN o índice representa os registros coletados

#### Scenario: Collection fails
- GIVEN uma coleta que lança erro antes de concluir
- WHEN o comando informa a falha
- THEN a reconstrução automática não é executada sobre essa coleta incompleta

### Requirement: Transactional index replacement
O sistema SHALL preservar o índice anterior quando a reconstrução falhar antes de concluir.

#### Scenario: Error during population
- GIVEN um índice preenchido
- WHEN ocorre um erro entre a limpeza e a conclusão do preenchimento
- THEN o índice anterior permanece disponível
- AND o comando termina com código não zero e informa como repetir a indexação

### Requirement: Existing database requirement
O sistema SHALL recusar a indexação de um caminho inexistente sem criar um banco novo.

#### Scenario: Incorrect database path
- GIVEN um caminho que não corresponde a um arquivo existente
- WHEN o usuário executa o comando manual
- THEN recebe uma orientação para verificar o caminho
- AND nenhum banco é criado
