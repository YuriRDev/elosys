## Purpose

O usuário quer reunir entidades, registros e anotações em uma investigação que possa ser retomada, com relatórios próprios para leitura e análise.

## ADDED Requirements

### Requirement: Resume local investigation
O sistema SHALL permitir retomar uma investigação salva no navegador.

#### Scenario: Return to a saved investigation
- GIVEN uma investigação com duas entidades, uma evidência e uma anotação
- WHEN o usuário fecha e reabre a aplicação no mesmo navegador
- THEN recupera suas seleções e a anotação sem alterar o banco SQLite

### Requirement: Report changed evidence
O sistema SHALL sinalizar referências que não possam ser confirmadas no banco atual.

#### Scenario: Dataset changed before reopening
- GIVEN uma evidência salva em um snapshot anterior e uma base atual diferente
- WHEN o usuário reabre a investigação
- THEN referências ausentes ou incompatíveis são indicadas para revisão
- AND o sistema não as troca silenciosamente por outros registros

### Requirement: PDF and Excel reports
O sistema SHALL exportar a investigação como PDF e XLSX com contexto e proveniência.

#### Scenario: Export selected evidence
- GIVEN uma investigação com filtros, registros e notas
- WHEN o usuário solicita cada formato
- THEN obtém PDF legível e XLSX com registros, fontes e notas identificáveis
- AND consegue distinguir fatos, indícios e anotações

### Requirement: Preserve spreadsheet identifiers
O sistema SHALL preservar documentos e campos textuais de forma segura no XLSX.

#### Scenario: Identifier with leading zero
- GIVEN um documento começando por zero e uma anotação começando por sinal de igual
- WHEN o usuário exporta XLSX
- THEN o documento mantém seus zeros e a anotação é uma célula textual sem fórmula
