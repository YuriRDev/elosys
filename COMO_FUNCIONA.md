# Como o EloSys funciona — visão geral técnica aprofundada

> Este documento existe pra explicar o projeto inteiro pra alguém que nunca viu o
> código: o que ele faz, de onde vem cada dado, como cada algoritmo de detecção
> funciona por dentro (com os números exatos, não só a ideia), e — o mais
> importante — como qualquer pessoa pode conferir, de fora, que nada aqui foi
> inventado ou alterado.
>
> Complementa (não substitui) os documentos em `ADs/` — que registram as
> *decisões* de arquitetura e o porquê delas — e o `README.md` — que é a porta de
> entrada rápida. Aqui a ideia é o caminho completo, de ponta a ponta.

## Sumário

1. [O que é o EloSys](#1-o-que-é-o-elosys)
2. [As duas metades do projeto](#2-as-duas-metades-do-projeto)
3. [O princípio central: rewrite-only + prova pública](#3-o-princípio-central-rewrite-only--prova-pública)
4. [A cadeia de proveniência](#4-a-cadeia-de-proveniência-de-onde-vem-cada-campo)
5. [Como uma pessoa vira "uma pessoa só" no banco](#5-como-uma-pessoa-vira-uma-pessoa-só-no-banco-resolução-de-identidade)
6. [Fonte por fonte: o que cada coletor baixa](#6-fonte-por-fonte-o-que-cada-coletor-baixa)
7. [Os algoritmos de detecção, um por um](#7-os-algoritmos-de-detecção-um-por-um)
8. [As camadas opcionais de IA](#8-as-camadas-opcionais-de-ia-triagem-não-veredito)
9. [O banco de dados](#9-o-banco-de-dados)
10. [A aplicação web](#10-a-aplicação-web)
11. [Como verificar e validar tudo isso você mesmo](#11-como-verificar-e-validar-tudo-isso-você-mesmo)
12. [Limitações conhecidas, de propósito](#12-limitações-conhecidas-de-propósito)

---

## 1. O que é o EloSys

Um cruzamento de **dados públicos brasileiros** (TSE, Receita Federal, Portal da
Transparência, redes sociais que o próprio candidato declarou à Justiça
Eleitoral) organizado **por pessoa**, com duas coisas que a maioria dos projetos
parecidos não tem:

- **Proveniência em cada campo**: todo dado mostrado na tela sabe de qual
  arquivo oficial ele saiu, quando foi baixado, e o hash que prova que não foi
  alterado depois.
- **Indício, não prova**: os algoritmos de detecção (doação circular, sócio de
  fornecedor, despesa desproporcional) nunca dizem "isso é crime" — eles dizem
  "isso é estatisticamente incomum, olhe aqui os dados brutos e confira você
  mesmo". Essa frase ("indício não é prova") aparece literalmente nos
  comentários do código-fonte, de propósito, como lembrete constante.

## 2. As duas metades do projeto

```
┌─────────────────────────┐        ┌──────────────────────────┐
│   elosys/  (Python)      │  ───▶  │   elosys.db (SQLite)      │  ───▶  web/ (Next.js)
│   coletores + regras     │        │   um arquivo só            │        lê, nunca escreve
└─────────────────────────┘        └──────────────────────────┘
```

- **`elosys/`** (Python) — um conjunto de **coletores independentes**
  (`elosys/tse/*.py`, `elosys/receita/cnpj.py`, `elosys/transparencia/sanctions.py`,
  `elosys/social/*.py`) e **regras de detecção** (`elosys/rules/*.py`) que juntos
  constroem o banco do zero a cada rodada. Cada um roda via `elosys <comando>`
  (ver `elosys/cli.py`).
- **`elosys.db`** — um único arquivo SQLite. É um *artefato de build*: não é
  editado à mão, não guarda histórico de versões — cada rodada dos coletores o
  reconstrói (ver §3).
- **`web/`** (Next.js/React) — a aplicação que as pessoas realmente usam. Ela
  **só lê** o banco (`web/src/lib/db.ts` abre a conexão como `readonly` +
  `PRAGMA query_only = ON`) — nunca escreve, nunca migra. Toda a lógica de
  consulta mora em `web/src/lib/queries.ts` (mais de 70 funções exportadas, uma
  ou poucas por seção de tela).

## 3. O princípio central: rewrite-only + prova pública

A decisão mais importante do projeto (documentada em `ADs/imutabilidade.md`) é
que o banco **não é editado incrementalmente**. Cada coletor:

1. Apaga só as tabelas que ele mesmo é dono (`reset_source()` em
   `elosys/provenance.py`) — nunca mexe no que outro coletor gerou.
2. Baixa os arquivos oficiais de novo.
3. Reconstrói suas tabelas do zero.

Se um valor sair errado, a correção é **consertar o código do parser e rodar de
novo** — nunca um `UPDATE` manual numa linha specific do banco. Isso existe
porque a alternativa (um "ledger" append-only com triggers de auditoria,
`supersedes_id`, cadeia de hash linha a linha) foi cogitada e descartada: o
projeto não é incremental, então esse aparato inteiro defenderia contra uma
operação (editar histórico) que nunca acontece.

Em troca, a prova de integridade fica em **dois arquivos versionados no git**,
não dentro do banco:

- **`manifest.json`** — gerado a cada build, lista **cada arquivo baixado**:
  fonte, URL exata, `accessed_at`, `payload_sha256`, tamanho, status HTTP, e o
  commit do coletor que processou aquele arquivo.
- **`<coletor>_report.json`** — o que aquela rodada decidiu: quantas linhas por
  ano, quantos CPFs foram descartados por ambiguidade (e por quê), quantas
  colisões foram puladas.

O comando `elosys verify` **rebaixa cada URL do manifesto e confere o hash**.
Se bater tudo, o banco inteiro é reproduzível a partir de fontes públicas — sem
confiar em nada que o EloSys "disse" sobre si mesmo.

## 4. A cadeia de proveniência (de onde vem cada campo)

Toda linha de dado real (uma doação, uma candidatura, um bem declarado) aponta
para uma cadeia de 4 tabelas:

```
source  →  collection  →  collection_file  →  parse  →  (a linha de dado em si)
"TSE -     "um download    "um CSV dentro     "uma
 bem_       concreto"       do zip"            versão de
 candidato"                                    parser"
```

- **`source`**: a fonte em si (nome, agência, base legal — ex: "Declarar bens é
  obrigatório pela Lei 9.504/1997 art. 11 §1 IV").
- **`collection`**: um download específico — `url`, `http_status`,
  `accessed_at`, `payload_sha256`, `size_bytes`.
- **`collection_file`**: um arquivo específico *dentro* do zip (a maioria dos
  arquivos do TSE vem em zips com vários CSVs).
- **`parse`**: qual versão do código leu aquilo (`parser_name`,
  `parser_version`, `run_at`) — se o parser mudar de versão, toda linha nova
  aponta pra parse nova, sem confundir com a antiga.

Cada registro de dado (uma doação, um bem, uma candidatura) tem uma coluna
`provenance_id` apontando pra um `parse` — e por isso, um `JOIN` simples
responde "de onde veio isso?" pra qualquer campo da tela. Na interface, isso
aparece como o botão pequeno "fonte" que abre um modal com exatamente esses
dados.

## 5. Como uma pessoa vira "uma pessoa só" no banco (resolução de identidade)

Duas pessoas com o mesmo nome não são a mesma pessoa; a mesma pessoa em
eleições diferentes pode aparecer com CPF mascarado num ano e CPF completo no
outro (o TSE mascarou o CPF em 2024 por LGPD e reverteu em 2026). A tabela
`people` existe pra resolver isso, com uma ordem de match **determinística**
(`elosys/identity.py`, função `resolve_person`):

1. Se o **título de eleitor** já existe em algum `people`, usa essa pessoa.
2. Senão, se o **CPF** é válido (dígito verificador correto) e já existe em
   algum `people`, usa essa pessoa.
3. Senão, cria uma pessoa nova.

Depois do match, se a pessoa encontrada estava com `cpf` ou `voter_id` vazio, o
dado novo **só preenche o que tava faltando** — nunca sobrescreve um valor já
existente. É assim que uma candidatura de 2024 (só com título, CPF mascarado)
"herda" o CPF que aparece no arquivo de 2026 da mesma pessoa.

Antes disso, `elosys/tse/candidates.py` já descartou CPFs ambíguos: um CPF é
jogado fora (e registrado em `rejected_cpf`, com o motivo) se ele está ligado a
**mais de um título de eleitor diferente**, ou se o título dele também aparece
ligado a **outro CPF diferente** — sinal de erro de digitação em algum lugar.
Rodando 2018–2026, isso descartou ~35 CPFs (~63 linhas) — um número pequeno,
de propósito: a filosofia aqui é "errar pra menos" (deixar duas pessoas
separadas por engano) em vez de fundir duas pessoas reais debaixo de um CPF
errado.

Cada linha de `people` carrega `cpf_trusted` (0 ou 1): **0** significa que o
CPF daquele registro específico veio vazio, mal-formado, ou foi rejeitado por
ambiguidade em algum ponto — a interface mostra "reconciliado" nesses casos,
sinalizando que aquele vínculo é menos forte que um CPF direto.

Doadores e fornecedores que **nunca foram candidatos** não ganham uma linha em
`people` — ficam como texto puro (nome + CPF/CNPJ) nas próprias tabelas de
doação/despesa. Só uma pessoa que realmente concorreu a cargo eletivo entra em
`people`. É por isso que a busca do site rotula esse tipo de resultado como
"pessoa física" em vez de linkar pra um perfil de candidato.

## 6. Fonte por fonte: o que cada coletor baixa

| Coletor | Fonte oficial | O que vira | Chave de identidade |
|---|---|---|---|
| `elosys/tse/candidates.py` | `consulta_cand_{ano}.zip`, CDN do TSE | `politician_history` (uma linha por candidatura/ano) | título eleitoral → CPF (ver §5) |
| `elosys/tse/accounts.py` | `prestacao_de_contas_eleitorais_candidatos_{ano}.zip` (3 CSVs: receitas, despesas contratadas, despesas pagas) | `campaign_org`, `campaign_donation`, `campaign_expense`, `campaign_expense_payment` | doador/fornecedor só vira `people` se já for candidato conhecido |
| `elosys/tse/assets.py` | `bem_candidato_{ano}.zip` | `declared_assets` (um bem por linha, nominal, sem correção de inflação) | via `SQ_CANDIDATO` |
| `elosys/tse/social.py` | `rede_social_candidato_{ano}.zip` | `social_media` (handles **declarados** ao TSE, obrigatório desde a Res. 23.610/2019) | via `SQ_CANDIDATO` |
| `elosys/tse/photo_urls.py` | API de busca por CPF do DivulgaCandContas (`pesquisar?cpf=...`) | `candidate_photo` (só a **URL** da foto oficial, nunca a imagem) | busca exata por CPF — sem risco de homônimo |
| `elosys/receita/cnpj.py` | BrasilAPI (proxy da Receita Federal) | `company_registry`, `company_partner` (quadro societário) | por CNPJ; sócio pessoa física vem com CPF **mascarado** pela própria fonte |
| `elosys/transparencia/sanctions.py` | Portal da Transparência — CEIS + CNEP (snapshot do dia, sem histórico por ano) | `sanction` | por CPF/CNPJ; nunca cria `people` novo, só liga a quem já existe |
| `elosys/social/x_posts.py` + `apify.py` | X/Twitter, via Apify, só das contas **declaradas ao TSE** | `social_account`, `social_post` | nunca "adivinha" um handle |

Pontos que valem destacar:

- **Nenhum coletor baixa endereço residencial, telefone ou e-mail pessoal** —
  são dados protegidos e ficam fora do projeto por decisão explícita.
- `accounts.py` e `assets.py` seguem a mesma regra de identidade de §5: um
  doador ou fornecedor que nunca foi candidato fica como texto puro, nunca
  vira uma linha fabricada em `people`.
- `photo_urls.py` é a **única exceção documentada** à regra "nunca usar a API
  interna não-documentada do DivulgaCandContas" (o resto do pipeline usa
  sempre o Portal de Dados Abertos, estruturado e estável) — porque a foto
  simplesmente não existe em nenhum arquivo em lote, só nessa API de busca. Se
  ela quebrar um dia, a tabela só para de se preencher; nada mais depende
  dela. É também o único coletor **incremental** (não rewrite-only) além do
  `receita/cnpj.py` — ver a nota de "arquivamento seletivo" abaixo.
- `social/x_posts.py` é a única parte do sistema que **não** passa por
  `manifest.json`/`elosys verify` — um post pode ser apagado a qualquer
  momento, então a prova de integridade fica junto do próprio registro
  (`raw_json` + `raw_sha256` + `retrieved_at`), não num arquivo externo.

### Por que `receita/cnpj.py` e `photo_urls.py` não são rewrite-only

Todo o resto do pipeline baixa **um arquivo em lote** por ano e reconstrói a
tabela inteira. Essas duas fontes são **APIs de consulta, uma requisição por
item** — não existe "o arquivo" pra baixar de uma vez. Refazer a consulta pra
todo mundo a cada build seria (a) lento e (b) ofensivo com o serviço alheio.
Por isso os dois são **caches incrementais**: só buscam quem ainda não tem
registro, priorizando por relevância (dinheiro movimentado, no caso do CNPJ;
ano de candidatura mais recente, no caso da foto), e podem ser rodados de novo
a qualquer momento pra completar mais um pedaço do catálogo.

## 7. Os algoritmos de detecção, um por um

Todos os três moram em `elosys/rules/` e escrevem nas mesmas 4 tabelas
genéricas (`rule_run`, `signal`, `signal_actor`, `signal_evidence` — ver §9).
Nenhum deles é rewrite-only incremental: cada rodada apaga só os sinais **daquela
regra** e recalcula do zero a partir do estado atual das tabelas-fonte.

Convenção que vale pras três: `severity` só existe como `"low" | "medium" |
"high"` — nunca "confirmado", nunca "culpado". Na prática, nenhuma das três
regras hoje chega a produzir `"low"` — só `medium`/`high` — mas o vocabulário
existe pronto pra quando uma regra mais permissiva precisar dele.

### 7.1 Doação circular (`circular_donations.py`)

**A pergunta que essa regra responde:** dinheiro que sai da campanha de um
político, por uma cadeia de doações e despesas, **volta pra dentro da mesma
teia de identidades**?

**Como o grafo é montado:** cada linha de `campaign_donation` vira uma aresta
`doador → candidato`; cada linha de `campaign_expense` vira uma aresta
`candidato → fornecedor`. Um laço no próprio nó (`origem == destino`, ex:
autofinanciamento) é descartado de propósito — não é "voltar por outra
pessoa". Se o mesmo par de nós tem doação **e** despesa entre si, isso vira uma
aresta só do tipo `"both"`, com o valor somado das duas.

**O algoritmo, em duas etapas:**

1. **SCC de Tarjan** (implementação iterativa, sem recursão — importante,
   porque o grafo real tem mais de 5 milhões de nós, e uma versão recursiva
   estouraria a pilha) encontra todos os **componentes fortemente conexos**:
   grupos de nós onde dá pra ir de qualquer um a qualquer outro seguindo as
   setas. Só os componentes com mais de 1 nó interessam (um nó sozinho nunca é
   um ciclo).
2. Dentro de cada componente, uma **busca em profundidade limitada por
   profundidade** (estilo Johnson) encontra os ciclos simples de fato — só
   avançando para vizinhos com id **maior** que o nó de partida do ciclo, uma
   técnica que garante achar cada ciclo simples **exatamente uma vez**, nunca
   duplicado.

**Os números exatos que controlam isso** (`elosys rule-circular-donations
--max-depth N --max-fanout N`):

- `max_depth = 5` — o ciclo mais longo que a busca considera (5 arestas). Sem
  esse limite a busca seria exponencial.
- `max_fanout = 400` — um nó com mais de 400 arestas de saída dentro do
  componente (ex: a conta nacional de um partido grande) é tratado como um
  "hub": a busca não *ramifica* por ele (evita explosão combinatória), embora
  ele ainda possa aparecer como ponta de um ciclo direto de 2 nós.

**Severidade:** ciclos com até 3 nós são `"high"`; de 4 a 5 nós, `"medium"`.

**O valor mostrado no sinal** é a soma exata de cada aresta do ciclo (não uma
amostra) — e o "grafo completo" que a interface linka usa até 10 linhas brutas
de `campaign_donation`/`campaign_expense` por aresta como evidência
(`signal_evidence`), não todas, quando uma aresta é sustentada por dezenas de
doações repetidas.

**Uma rodada real, pra dar noção de escala** (não são limites do sistema, é só
o resultado de uma execução real, citado no próprio código): grafo de
5.350.221 nós / 7.658.959 arestas; Tarjan roda em ~12s; 108.400 ciclos
encontrados em ~10,5s; 63.556 de severidade alta, 44.844 média. O ciclo de
maior valor (R$ 177.776.963,25) envolvia o comitê nacional de um partido, um
candidato, uma empresa e outro candidato — citado explicitamente como **não
necessariamente incomum**, já que a conta nacional de um partido movimenta
dinheiro com centenas de campanhas por natureza.

### 7.2 Sócio de fornecedor (`candidate_supplier_partner.py`)

**A pergunta:** um candidato é **sócio** de uma empresa que recebeu dinheiro de
campanha — seja da própria campanha dele, seja de outra?

**O problema de partida:** o quadro societário (via Receita Federal/BrasilAPI)
vem com o CPF do sócio **mascarado** (formato `***498538**` — só 6 dígitos do
meio visíveis). Não dá pra casar por CPF completo.

**O critério de match usado** (`match_basis = "nome_e_6_digitos"`):

- O nome normalizado do sócio bate **exatamente** com o nome canônico de uma
  pessoa em `people`, **e**
- Esses mesmos 6 dígitos do meio do CPF mascarado batem com os 6 dígitos
  correspondentes do CPF real dessa pessoa.
- Nomes curtos (menos de 8 caracteres, ou sem espaço — ex: "J SILVA") são
  descartados de propósito: colidem com gente demais pra confiar.
- Se **duas ou mais pessoas diferentes** batem no mesmo nome + mesmos 6
  dígitos, o match é jogado fora inteiro (ambíguo demais pra decidir).

Por isso a interface sempre rotula isso como "possível" — é um cruzamento de
probabilidade, não uma prova de identidade como um CPF completo seria.

**O que a regra calcula por match encontrado:**

- `paid_by_self` — a própria campanha do candidato-sócio pagou aquela empresa?
- `payer_candidacies` — quantas campanhas **diferentes** pagaram a empresa (se
  mais de uma, e nenhuma delas é o próprio sócio, é um sinal de que outros
  candidatos estão pagando uma empresa de um colega).
- `payments_total_cents` / `payments_count` — soma e contagem de todos os
  pagamentos daquela empresa, de qualquer campanha.

### 7.3 Despesa desproporcional (`disproportionate_expense.py`)

**A pergunta:** uma despesa de campanha descreve um item tipicamente barato,
mas foi cobrada por um valor desproporcional?

**O método (deliberadamente simples e auditável, v1.0):** procura por
palavras-chave no texto livre da despesa (o campo `DS_DESPESA` do próprio
TSE, sem tirar acento) — `CANETA, LAPIS/LÁPIS, LAPISEIRA, BORRACHA,
APONTADOR, ADESIVO, CRACHA/CRACHÁ, ETIQUETA, CLIPS, GRAMPO, GRAMPEADOR,
REGUA/RÉGUA, BLOCO DE ANOTA, ENVELOPE, MARCADOR DE TEXTO, PRANCHETA,
PERFURADOR, ELASTICO/ELÁSTICO` — e, se achar, compara o valor com dois pisos:

- **R$ 5.000** — piso mínimo pra virar sinal (`medium`).
- **R$ 50.000** — piso pra virar `high`.

**Limitação assumida no próprio código:** o TSE não publica quantidade
comprada, só o valor total contratado — então essa regra nunca calcula um
"preço unitário" de verdade, só sinaliza "categoria tipicamente barata, valor
alto". Uma v2 que comparasse contra a mediana de despesas da mesma categoria
foi cogitada e **não foi implementada** — é um ponto em aberto documentado.

Uma rodada real: 22.269 sinais (1.232 altos, 21.037 médios); o maior caso
citado foi R$ 2.504.200,00 numa despesa descrita como "PRAGÕES, BIG HAND,
PERFURADO, PRAGUINHA, ADESIVO".

## 8. As camadas opcionais de IA (triagem, não veredito)

Duas ferramentas **opcionais** (precisam de `DEEPSEEK_API_KEY`) usam um LLM
(DeepSeek) só pra **ordenar por onde um humano deveria começar a olhar** — elas
não confirmam nem descartam nada sozinhas, e não criam `rule_run` (não são
"regras" no sentido formal do pipeline).

### 8.1 `ai_review.py` — segunda opinião sobre sinais financeiros

Roda sobre os sinais de `circular_donations` e `disproportionate_expense`
(existem ~108 mil sinais de ciclo circular — inviável um humano ler todos).
Pra cada sinal, manda pro modelo os fatos brutos e pede um JSON com:

- `veredito`: `"bizarro"` | `"plausivel"` | `"inconclusivo"`
- `confianca`: `"baixa"` | `"media"` | `"alta"`
- `explicacao` (2 a 4 frases) + `fatos` citados

O prompt do sistema define exemplos concretos do que é **plausível** (mesma
coligação/partido, conta nacional financiando candidatos próprios, sobra de
campanha devolvida, compra em lote com preço justificável) versus **bizarro**
(ciclo curto fechado entre gente sem vínculo partidário nenhum; empresa que
doou milhões e recebeu quase o mesmo valor de volta; fornecedor cujo ramo não
tem nada a ver com o serviço contratado; valor fora de escala sem explicação),
e instrui explicitamente: **"NUNCA afirme que houve crime, fraude ou
irregularidade."**

### 8.2 `social_review.py` — triagem de discurso em redes sociais

Mesmo princípio, aplicado aos posts que bateram no léxico de termos
potencialmente ofensivos (`elosys/social/lexicon.py` — **~470 termos** em 15
categorias: racismo, LGBTfobia, misoginia, xenofobia, capacitismo,
antissemitismo, etc., cada termo com peso `alta/média/baixa` conforme o quanto
depende de contexto). O léxico é descrito no próprio código como **um filtro de
recall, não um classificador** — ele só decide o que vale a pena um humano ou o
LLM lerem; quem decide se é ofensivo de fato é a revisão seguinte.

O modelo julga **só a fala do próprio autor** (se é uma resposta, o tweet
original é só contexto) e devolve `ofensivo` (sim/não), `categorias`,
`severity`, e o **trecho exato** citado como prova — a interface sempre mostra
essa citação literal + link pro post original, com aviso de que é classificação
automática e pode errar.

## 9. O banco de dados

SQLite, um arquivo só (`ADs/banco.md` justifica: sem guardar o payload bruto,
o banco cabe em ~1GB; a carga de trabalho real é "uma reconstrução pesada,
depois muita leitura analítica" — perfil que SQLite atende bem sem precisar de
um servidor de banco separado).

Convenções fixas em todo o schema:
- Toda chave primária é um `INTEGER PRIMARY KEY` simples.
- Dinheiro é sempre `INTEGER` em **centavos** (`*_cents`), nunca `REAL` — evita
  erro de ponto flutuante em valores monetários.
- Datas são `TEXT` ISO-8601 (UTC pra timestamps, `YYYY-MM-DD` pra datas).
- Booleano é `INTEGER` 0/1.

As tabelas de detecção (usadas pelas 3 regras da §7) são deliberadamente
genéricas, não uma tabela por regra:

```sql
rule_run       -- uma linha por execução de uma regra (versão, parâmetros, quando)
signal         -- o sinal em si: tipo, severidade, explicação, valor, tamanho do caminho
signal_actor   -- quem está envolvido (pessoa ou empresa) e em que papel
signal_evidence -- quais linhas brutas (doação, despesa...) sustentam esse sinal
```

Um sinal **sem nenhuma linha em `signal_evidence` é considerado inválido** por
design — é o jeito de garantir que todo sinal é rastreável até o dado bruto que
o gerou.

## 10. A aplicação web

Next.js (App Router), Server Components por padrão. Estrutura:

- **`web/src/lib/queries.ts`** — a única camada que fala com o SQLite. Cada
  página/seção chama uma função específica daqui (`getPersonHeader`,
  `getCycleEdgeAmounts`, `searchPeople`, etc.) — nada de SQL espalhado pelos
  componentes.
- **`web/src/lib/db.ts`** — abre a conexão **somente leitura**.
- **Rotas principais**: `/` (busca), `/politico/[id]` (perfil completo, com
  `<Suspense>` por seção — cada bloco pode carregar num ritmo próprio sem travar
  o resto), `/cpf/[cpf]` e `/cnpj/[cnpj]` (perfil de quem não é candidato),
  `/grafo` (rede de correlações interativa), `/ranking` (bens declarados),
  `/sinais/*` (uma página por tipo de sinal de alerta).
- **Design**: tema claro/escuro seguindo o sistema operacional por padrão
  (zero-flash via um script inline no `<head>`), paleta neutra em cinza com um
  único acento (violeta) reservado só pra links "clicáveis" dentro de tabelas.
  Cards com sombra sutil + cantos arredondados + animação de entrada leve
  (`--shadow-card`, `.animate-in` em `globals.css`).

## 11. Como verificar e validar tudo isso você mesmo

Isso é o ponto central do projeto, então vale repetir de forma direta:

```bash
elosys verify --db elosys.db
```

Esse comando **rebaixa cada URL registrada no `manifest.json`** e compara o
hash com o que foi salvo na hora do build original. Se todos baterem, você
provou, sem confiar em nada que o EloSys "disse" — só olhando pros arquivos
públicos do TSE/Receita/Portal da Transparência — que o banco inteiro é
reconstruível a partir de fontes oficiais.

O resultado vem por arquivo: `ok`, `changed` (a fonte mudou desde a coleta — comum
nos arquivos do ano eleitoral corrente, que o TSE republica várias vezes por dia) ou
`error` (o download falhou; não prova nada, só precisa ser refeito). Por padrão só
os arquivos em lote são conferidos; as consultas item a item à BrasilAPI e à API de
fotos entram com `--include-api` (e `--api-delay` entre elas), para não estourar o
limite de requisições desses serviços.

Outras formas de conferir:

- **O botão "fonte"** em qualquer campo da interface abre um modal com a URL
  exata, quando foi coletado, e o hash daquele arquivo.
- **`manifest.json`** e **`<coletor>_report.json`** são commitados no git — dá
  pra ver o histórico de builds e o que cada um decidiu (quantos CPFs
  rejeitados, por quê) sem rodar nada.
- **Reconstruir do zero**: como o build é rewrite-only, rodar os coletores de
  novo numa máquina limpa reproduz o mesmo banco (a menos que a fonte
  original tenha mudado de valor — o que o `elosys verify` também detecta,
  como uma divergência de hash).
- **Os algoritmos de detecção são código aberto, sem caixa-preta**: os
  thresholds exatos (R$ 5.000, profundidade 5, etc.) estão no próprio arquivo
  `.py` da regra, versionados (`RULE_VERSION`) e citados no `rule_run.params`
  de cada execução — dois builds com os mesmos parâmetros geram exatamente os
  mesmos sinais.

## 12. Limitações conhecidas, de propósito

- **CPF mascarado em 2024**: o TSE mascarou parte do CPF naquele ano por LGPD
  (revertido em 2026) — candidaturas só desse ano, sem outro ano pra "herdar"
  o CPF completo, ficam com `cpf_trusted = 0`.
- **Sócio de fornecedor é probabilístico**: nome + 6 dígitos nunca é uma prova
  de identidade tão forte quanto um CPF inteiro — por isso "possível" em toda
  a interface.
- **Despesa desproporcional não sabe a quantidade comprada**: só sinaliza
  categoria-tipicamente-barata + valor alto, nunca um preço unitário real.
- **Discurso em redes sociais é o único dado sem `manifest.json`**: conteúdo
  de rede social pode ser apagado a qualquer momento — a prova de integridade
  fica no próprio registro (hash + data de coleta), não num arquivo externo
  verificável por terceiros do mesmo jeito que o resto.
- **Nenhum sinal é acusação**: todos os três algoritmos de detecção, e as duas
  camadas de IA, existem pra apontar "olha aqui, isso é incomum" — a conclusão
  de se é irregular ou não é sempre de quem lê os dados brutos, nunca do
  sistema.
