## Purpose

O usuário quer pesquisar uma lista de entidades sem repetir buscas manuais ou misturar homônimos e documentos ambíguos.

## ADDED Requirements

### Requirement: One result per input
O sistema SHALL informar o resultado de cada entrada aceita do lote.

#### Scenario: Mixed valid and invalid entries
- GIVEN um lote com entidade encontrada, identificador ausente e entrada inválida
- WHEN a consulta termina
- THEN o relatório apresenta as três entradas com seus respectivos status

### Requirement: No automatic homonym merge
O sistema SHALL preservar ambiguidade quando houver mais de uma correspondência nominal.

#### Scenario: Two people share a name
- GIVEN dois candidatos diferentes com o mesmo nome
- WHEN uma entrada do lote busca esse nome
- THEN recebe correspondências ambíguas, sem fundir suas finanças

### Requirement: Explicit input limit
O sistema SHALL recusar lotes acima do limite documentado sem omitir entradas silenciosamente.

#### Scenario: Input contains too many rows
- GIVEN um arquivo com 1.001 entradas
- WHEN a primeira versão aceita no máximo 1.000
- THEN o usuário recebe erro com o limite, sem relatório apresentado como completo
