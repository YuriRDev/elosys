## Context

Proposta de 2026-10-03 (BRT), após nova entrevista grill-me. Preservar Python, SQLite, Next.js e schema existente. Implementação ainda não iniciada.

## Goals / Non-Goals

Aceitar lista limitada de identificadores e produzir resultados individuais com status de correspondência, contexto e fontes.
Fora do escopo: mudanças de schema, novas acusações automáticas, fontes não aprovadas e publicação externa automática.

## Technical Approach

- Primeira versão recebe CSV com tipo e identificador explícitos, preservando documentos como texto. Busca por nome retorna candidatos de correspondência, não identificação automática.
- Definir limite inicial de 1.000 entradas, deduplicação de consultas e preservação de uma saída por linha de entrada. Nunca truncar silenciosamente o arquivo.
- Cada entrada informa status encontrado, não encontrado, ambíguo ou inválido. Falha de uma entrada não desaparece do relatório.
- Reutilizar contratos e limites de consulta; usar banco em leitura e evitar fan-out ilimitado. Não enriquecer dados por APIs pagas automaticamente.
- Exportar resultado tabular com referência às fontes e resumo de cobertura. Integração com Excel/PDF depende do contrato de relatórios, não de fórmulas ou macros.
- Não usar CPFs mascarados ou nome semelhante para juntar pessoas distintas.

## Dependencies and Delivery

Depende da resolução de entidades, dos contratos de exportação e do diagnóstico. Integração com API versionada pode ocorrer depois do comando local.
Consultar o backlog ampliado para prioridade. Tarefas e critérios devem ser cumpridos antes de declarar o recurso implementado.
