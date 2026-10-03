## Purpose

O usuário quer melhorar os três fluxos de uso: buscar e filtrar, explorar grafos e operar por celular ou teclado.

## ADDED Requirements

### Requirement: Understand active filters
A interface SHALL mostrar quais filtros afetam o resultado atual.

#### Scenario: Clear a financial filter
- GIVEN uma tabela com filtro de eleição e faixa de valor
- WHEN o usuário limpa a faixa de valor
- THEN consegue identificar que a eleição continua ativa e o resultado corresponde a ela

### Requirement: Keyboard access to critical flows
A interface SHALL permitir operar busca e seleção de entidades por teclado.

#### Scenario: Select search result without pointer
- GIVEN uma busca que retornou candidatos
- WHEN o usuário navega e seleciona usando teclado
- THEN abre a entidade pretendida com foco identificável

### Requirement: Readable graph relationships
A interface SHALL disponibilizar resumo textual da relação selecionada no grafo.

#### Scenario: Inspect an edge in dense graph
- GIVEN um grafo com muitas relações
- WHEN o usuário seleciona uma relação
- THEN pode consultar suas entidades, valores aplicáveis e evidências sem depender apenas do desenho
