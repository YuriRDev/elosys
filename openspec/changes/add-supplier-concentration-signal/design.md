## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Calcular participação dos maiores fornecedores por campanha e eleição, com parâmetros explícitos e evidências dos contratos considerados.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- A primeira versão mede despesas contratadas, sem misturá-las com pagamentos. Agrupar por identificação da contraparte e campanha/eleição.
- Exibir numerador, denominador, participação dos maiores fornecedores e cobertura de identificação. Montantes nulos, negativos, cancelados ou sem identificação têm tratamento definido antes do cálculo.
- Limiares de participação, número de fornecedores e gasto mínimo são parâmetros a calibrar. Não comparar campanhas de cargos e circunscrições diferentes como se fossem equivalentes.
- Fornecedor único pode ser legítimo. Usar linguagem de concentração e indício, com contratos e fontes disponíveis para revisão.
- Identidade insuficiente não é resolvida pelo nome. Registrar os resultados no modelo de sinais e garantir reexecução limitada à regra.

## Dependencies and Delivery

Depende das contas e da definição de tratamento dos valores elegíveis. A consulta agregada deve ser medida para evitar varreduras repetidas na interface.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
