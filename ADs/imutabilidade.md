# AD — Build reprodutível (rewrite-only) e âncora no git

**Status:** Aceita
**Relacionado:** [confiabilidade.md](confiabilidade.md), [banco.md](banco.md)

> Nomes de tabela/coluna em inglês (ver [banco.md](banco.md)); texto em português.

## Contexto

Não repúdio exige que ninguém — inclusive nós — altere o passado sem que dê para
perceber. A primeira versão tentou isso com um livro-razão *append-only*: triggers
`BEFORE UPDATE/DELETE`, correção só por linha nova com `supersedes_id`, e uma hash
chain sobre `collection` com checkpoints no git.

Na prática o projeto **não é incremental**. O `.db` é um artefato de build: gerado
do zero, numa única execução, a partir dos arquivos públicos. Para atualizar os
dados, apaga-se o arquivo e roda-se de novo. Ninguém edita registro; ninguém faz
merge incremental. Todo o maquinário append-only defendia contra uma operação que
não existe.

## Decisão

### 1. Modelo de execução: rewrite-only

- `elosys` constrói o banco inteiro num run, do arquivo vazio até o `.db` pronto.
- **Sem update incremental, sem append-only, sem correção in-place.** Valor errado
  = bug de parser → conserta o código, rebuilda.
- Nenhum trigger de imutabilidade. As tabelas são mutáveis *durante o build* (o
  passo `promote` faz `UPDATE`/`DELETE` no staging e resolve identidade com
  `UPDATE people`). Depois do build, quem consome abre com `PRAGMA query_only=ON`.
- O staging (`stg_candidate`) é `CREATE TEMP TABLE` — vive só na conexão do build
  e é dropado no fim. Não aparece no `.db` entregue.

### 2. A garantia de não repúdio vem do determinismo + manifesto público

Dado o mesmo conjunto de arquivos de entrada (hash conferido) e o mesmo commit do
código, o build é determinístico: qualquer pessoa reconstrói o mesmo banco.

**`manifest.json`** — gerado a cada build, contém, para cada arquivo baixado:
`source`, `url`, `accessed_at`, `payload_sha256`, `size_bytes`, `http_status`,
e o `sha256` de cada CSV dentro do zip. Mais o `collector_commit`.

Esse arquivo é **commitado no repositório**. O histórico do git passa a ser o log
imutável, de graça e auditável por terceiros: reescrever o que foi coletado exige
reescrever o histórico público do repo, o que é visível.

- `elosys verify` re-baixa cada URL do manifesto e confere o `payload_sha256`.
  Classifica cada coleta como `ok`, `changed` (a fonte hoje serve outro conteúdo)
  ou `error` (download falhou — não diz nada sobre integridade, refaça depois);
  uma falha de download não interrompe a verificação. Por padrão confere só os
  arquivos em lote (`source.type = 'csv'`); as consultas item a item às APIs
  (BrasilAPI, fotoUrl) só entram com `--include-api`, espaçadas por `--api-delay`,
  porque refazê-las de uma vez estoura o rate limit dessas APIs.
  Tudo `ok` = o banco é 100% reconstruível a partir das fontes públicas.
- `run_report.json` (também commitado) registra as decisões do build: linhas por
  ano, CPFs derrubados por ambiguidade e o motivo, colisões puladas.
- Opcional: commitar também o `sha256` do `.db` gerado, para amarrar "este
  arquivo saiu deste manifesto".

### 3. O que se perde e a mitigação

Append-only provava "não reescrevemos *a linha R* depois". Rewrite-only não prova
isso sozinho. Cobrem essa lacuna:

- o `manifest.json` + `run_report.json` commitados (o git é o histórico);
- o build ser determinístico e verificável (`elosys verify`);
- se ainda for pouco, guardar os zips do `consulta_cand` (~1 GB todos os anos)
  num store por hash — TODO em [confiabilidade.md](confiabilidade.md).

O risco real que sobra é o **da fonte**: o TSE republicar um arquivo no mesmo URL
com valores diferentes (eles fazem — CPF 2024/2026). Nesse caso `elosys verify`
acusa a mudança; o valor antigo só é recuperável se tivermos guardado o zip.

## Consequências

- Schema muito menor: sem triggers `ao_*`, sem `supersedes_id`, sem view
  `politician_history_current`, sem `record_hash`/`prev_hash`/`chain_hash`.
- "Consertar no banco" continua proibido — não porque um trigger barra, mas
  porque o banco é descartável: a correção é no código + rebuild.
- O artefato de auditoria saiu do `.db` e foi para arquivos versionados
  (`manifest.json`, `run_report.json`).
- `elosys verify` custa uma re-coleta completa (rede). É comando sob demanda.

## Pontos em aberto

- ⚠️ Automatizar `elosys verify` (CI semanal?) e alertar quando uma fonte muda.
- ⚠️ Commitar o `sha256` do `.db` no repo a cada build oficial — decidir o fluxo
  (o `.db` em si continua fora do git, ver `.gitignore`).
