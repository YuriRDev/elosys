# EloSys
DB consolidada de candidatos brasileiros (2014 a 2026), construída **exclusivamente** a partir de fontes oficiais e cruzada por CPF e CNPJ. 


<img width="1174" height="517" alt="image" src="https://github.com/user-attachments/assets/6a760c7a-16ae-4e0d-b2c4-e6ada9031b98" />

O objetivo é apoiar a investigação de relações entre agentes políticos e identificar indícios de padrões atípicos, como doações circulares, fracionamento de doações, empresas de fachada e evolução patrimonial incompatível.


> **Aviso.** Os resultados do Elosys são indícios, não provas, e não constituem acusação contra nenhuma pessoa. O sistema produz sinais de alerta destinados à verificação por órgãos competentes (Ministério Público, TCU, Receita Federal, COAF). Cada dado exibido indica o arquivo público de origem, que pode ser baixado novamente e conferido por hash.

## Visão geral
- **Backend:** pipeline de coleta em Python, com armazenamento em SQLite (`elosys.db`).
- **Frontend:** aplicação Next.js somente leitura, em `/web`, que permite buscar candidatos e consultar a ficha completa com a fonte de cada campo.

## Uso com o banco pré-construído

A forma mais rápida de utilizar o projeto é baixar o banco já populado e executar a aplicação web, sem necessidade de rodar os coletores.

### Volume de dados coletados

| Conjunto | Volume |
|---|---|
| Candidaturas (`consulta_cand`, 2014–2026) | 1,63 milhão (cerca de 1,18 milhão de pessoas) |
| CNPJs de campanha | 1,04 milhão |
| Doações recebidas | 5,16 milhões, totalizando R$ 26,7 bilhões |
| Despesas contratadas | 9,47 milhões, totalizando R$ 16,2 bilhões |
| Pagamentos efetuados (regime de caixa) | 10,89 milhões, totalizando R$ 18,85 bilhões |
| Redes sociais declaradas (obrigatórias desde 2018) | 841 mil |
| Sanções federais (CEIS/CNEP) | 25,5 mil, das quais 474 empresas aparecem como doadoras ou fornecedoras de campanha |
| Bens declarados no registro de candidatura | 3,25 milhões, totalizando R$ 445,5 bilhões |

Tamanho do banco: aproximadamente 11,4 GB.


### 1. Download

O arquivo `elosys.zip` tem 2,84 GB compactado (cerca de 11,4 GB após a extração). Os dois endereços abaixo disponibilizam o mesmo arquivo:

| Origem | Endereço |
|---|---|
| Internet Archive | [archive.org/details/elosys](https://archive.org/details/elosys) |
| Hugging Face | [huggingface.co/datasets/YuriRDev/elosys](https://huggingface.co/datasets/YuriRDev/elosys) |

SHA-256 de `elosys.zip`:

```
96fb819b681752250db0c6cdc62566d1773338547daf6ea524edcd4024b16693
```

Recomenda-se verificar a integridade antes da extração:

```bash
sha256sum elosys.zip                          # Linux, macOS, Git Bash
```

```powershell
Get-FileHash elosys.zip -Algorithm SHA256     # PowerShell
```

O `Get-FileHash` exibe o hash em maiúsculas; o valor é o mesmo, pois hexadecimal não diferencia caixa. Para comparar diretamente (`-eq` é case-insensitive, retorna `True` se íntegro):

```powershell
(Get-FileHash elosys.zip -Algorithm SHA256).Hash -eq "96fb819b681752250db0c6cdc62566d1773338547daf6ea524edcd4024b16693"
```

Extraia o arquivo e posicione `elosys.db` na raiz do repositório. O banco já inclui todas as tabelas e o índice de busca por nome de doador e fornecedor.

### 2. Execução local

Requisitos: Node.js 20.9 ou superior e git.

```bash
git clone https://github.com/YuriRDev/elosys.git
cd elosys
# copie o elosys.db para esta pasta

cd web
npm install
npm run dev        # http://localhost:3000
```

A aplicação abre o banco em modo somente leitura e não realiza nenhuma escrita. Para utilizar outro caminho:

```bash
ELOSYS_DB_PATH=/caminho/para/elosys.db npm run dev
```

Build de produção:

```bash
npm run build && npm run start
```

## Construção do banco a partir das fontes

Este procedimento reconstrói a base integralmente a partir das fontes oficiais. O processo é demorado: os arquivos de prestação de contas do TSE ultrapassam 1 GB por ano, e algumas etapas levam horas. Os downloads são gravados em `dados_tmp/` e removidos após o processamento. Reserve cerca de 15 GB de espaço livre.

Requisito: [uv](https://github.com/astral-sh/uv), que instala o Python 3.12 e as dependências.

```bash
uv sync
uv run elosys init-db --db elosys.db
```

### Etapa 1: coleta das fontes

Cada coletor é independente e opera em modo *rewrite-only*: remove as tabelas sob sua responsabilidade e as reconstrói. Sem o parâmetro `--years`, todos os anos suportados são processados.

```bash
uv run elosys tse-candidates          --db elosys.db   # candidaturas 2014–2026
uv run elosys tse-accounts            --db elosys.db   # CNPJ de campanha, doações e despesas (etapa mais longa)
uv run elosys tse-social              --db elosys.db   # redes sociais declaradas
uv run elosys tse-assets              --db elosys.db   # bens declarados
uv run elosys transparencia-sanctions --db elosys.db   # CEIS/CNEP
uv run elosys transparencia-earmarks  --db elosys.db   # emendas parlamentares
```

Caso algum download retorne HTTP 403 (bloqueio anti-bot da fonte), baixe o arquivo `.zip` pelo navegador, salve-o em `dados_tmp/` com o nome indicado no log e execute o coletor novamente. O arquivo local será utilizado.

### Etapa 2: enriquecimento (opcional, incremental)

```bash
uv run elosys receita-cnpj   --db elosys.db --limit 500   # dados cadastrais e sócios de CNPJ (BrasilAPI)
uv run elosys tse-photo-urls --db elosys.db --limit 500   # foto oficial dos candidatos
```

Ambos os comandos são incrementais e preservam os registros existentes. Execuções sucessivas ampliam a cobertura.


### Etapa 3: índice de busca por nome

A busca por doadores e fornecedores que nunca foram candidatos depende de uma tabela FTS5 que nenhum coletor preenche. Execute o script abaixo após cada `tse-accounts`:

```bash
uv run python - <<'PY'
import sqlite3
con = sqlite3.connect("elosys.db")
con.executescript("""
DELETE FROM pessoa_fisica_search;
INSERT INTO pessoa_fisica_search (cpf, name)
SELECT cpf, max(name) FROM (
  SELECT donor_cpf_cnpj AS cpf, donor_name AS name FROM campaign_donation
    WHERE donor_company_id IS NULL AND donor_cpf_cnpj IS NOT NULL
      AND length(donor_cpf_cnpj) = 11 AND donor_name IS NOT NULL
  UNION ALL
  SELECT supplier_cpf_cnpj AS cpf, supplier_name AS name FROM campaign_expense
    WHERE supplier_company_id IS NULL AND supplier_cpf_cnpj IS NOT NULL
      AND length(supplier_cpf_cnpj) = 11 AND supplier_name IS NOT NULL
) GROUP BY cpf;
""")
con.commit()
PY
```

### Etapa 4: regras de detecção

As regras operam sobre os dados coletados e geram os sinais de alerta.

```bash
uv run elosys rule-disproportionate-expense --db elosys.db
uv run elosys rule-circular-donations       --db elosys.db   # cerca de 25 min na base completa
uv run elosys candidate-supplier-partner    --db elosys.db   # requer receita-cnpj (quadro societário)
```

### Etapa 5: análises complementares com LLM e X (opcional)

Exigem chaves de API definidas em variáveis de ambiente. Chaves nunca devem ser versionadas.

```bash
export DEEPSEEK_API_KEY=...
uv run elosys ai-review --db elosys.db --limit 100 --order tight

export APIFY_TOKEN=...
uv run elosys social-x      --db elosys.db --scope federal
uv run elosys social-review --db elosys.db --limit 5000
```

### Etapa 6: manifesto e testes

```bash
uv run elosys manifest --db elosys.db   # gera manifest.json com URL e SHA-256 de cada fonte
uv run pytest                           # testes com fixtures, sem acesso à rede
```

Como os coletores são *rewrite-only*, cada tabela passa a conter exatamente os anos informados em `--years`. Para partir de um estado completamente limpo, remova `elosys.db` e reinicie o processo.

## Arquitetura

Cada fonte de dados possui um coletor independente em `elosys/tse/*.py`. A execução de um coletor descarta as tabelas correspondentes e as reconstrói a partir dos arquivos oficiais. O banco é tratado como artefato descartável; a garantia de integridade está no `manifest.json`, versionado no repositório.

### Estrutura do banco

| Tabela | Conteúdo | Coletor |
|---|---|---|
| `politician_history` | Uma linha por candidatura e eleição: nome, partido, cargo, UF, situação, resultado e dados de registro | `tse-candidates` |
| `people` | Pessoa física, com chave substituta e CPF/título eleitoral como identificadores. Toda junção por pessoa utiliza esta tabela, nunca o CPF diretamente | compartilhada |
| `companies` | Empresa por CNPJ, classificada como campanha, doadora, fornecedora ou sancionada | compartilhada |
| `campaign_org` | CNPJ aberto por cada candidatura para a campanha (natureza jurídica 409-4) | `tse-accounts` |
| `campaign_donation` | Doações recebidas: doador (CPF/CNPJ e nome), valor, data e forma | `tse-accounts` |
| `campaign_expense` | Despesas contratadas: fornecedor, valor e descrição do serviço | `tse-accounts` |
| `campaign_expense_payment` | Data efetiva de pagamento de cada despesa, inclusive parcelas | `tse-accounts` |
| `social_media` | Redes sociais e sites declarados no registro da candidatura | `tse-social` |
| `declared_assets` | Bens declarados no registro: tipo, descrição e valor | `tse-assets` |
| `company_registry`, `company_partner` | Data de abertura, situação cadastral e quadro societário de CNPJ | `receita-cnpj` (incremental) |
| `sanction` | Pessoas e empresas impedidas de contratar com o poder público ou punidas por atos de corrupção (CEIS/CNEP) | `transparencia-sanctions` |
| `rejected_cpf` | CPFs descartados por ambiguidade (por exemplo, um mesmo CPF vinculado a mais de um título eleitoral) e o respectivo motivo | `tse-candidates` |
| `source`, `collection`, `collection_file`, `parse` | Proveniência: órgão, URL, arquivo, hash e parser de origem de cada registro | todos |
| `rule_run`, `signal`, `signal_actor`, `signal_evidence` | Sinais de alerta produzidos pelas regras de detecção (ver `ADs/dados_derivados.md`) | regras de detecção |
| `signal_ai_review` | Avaliação complementar de cada sinal por LLM, com resposta e prompt armazenados na íntegra | `ai-review` |
| `candidate_supplier_partner` | Candidatos que figuram no quadro societário de empresas que receberam pagamentos de campanha (correspondência não determinística) | `candidate-supplier-partner` |

Todo registro possui um `provenance_id` que o vincula, em cadeia, a `parse`, `collection` e `source`. A origem de qualquer dado pode ser obtida por uma junção simples.

## Sinais de alerta

As tabelas `rule_run`, `signal`, `signal_actor` e `signal_evidence` não provêm de fontes externas: são geradas pelo próprio sistema a partir dos dados coletados. Seguem a mesma disciplina de proveniência: cada evidência referencia um registro real, que por sua vez possui sua própria origem. A severidade é classificada apenas como `low`, `medium` ou `high`; o sistema não emite classificações como "confirmado" ou "fraude".

### Despesa desproporcional (`disproportionate_expense`)

Identifica, em `campaign_expense.description`, itens tipicamente de baixo custo (18 categorias, como canetas, adesivos e crachás) com valores muito acima do padrão da categoria. A severidade é `medium` a partir de 15 vezes a mediana histórica e `high` a partir de 30 vezes, com piso de R$ 1.000. Categorias com menos de 20 registros utilizam pisos fixos de R$ 5 mil e R$ 50 mil.

Na base completa, a regra gerou 28.743 sinais (13.856 de severidade alta e 14.887 de severidade média). O maior caso corresponde a R$ 2.504.200,00 em material adesivo, valor 9.879 vezes superior à mediana da categoria (R$ 253,50).

O TSE não publica a quantidade adquirida, apenas o valor total; por isso a regra não calcula preço unitário. Um valor elevado pode decorrer de lote grande, descrição incompleta ou erro de digitação. A página `/sinais/despesa-desproporcional` apresenta os maiores gastos por categoria, sua proporção em relação à receita da campanha e a comparação com a média de candidatos ao mesmo cargo e estado.

### Doação circular (`circular_donations`)

Constrói um grafo dirigido sobre toda a base (doador → candidato, candidato → fornecedor) e utiliza o algoritmo de Tarjan para componentes fortemente conexos, combinado com busca em profundidade limitada (padrão de 5 nós), para localizar ciclos em que recursos saem de uma campanha e retornam à mesma cadeia.

Na base completa, o grafo possui 5,35 milhões de nós e 7,66 milhões de arestas. Foram encontrados 108.400 ciclos; destes, 38.267 movimentaram mais de R$ 10.000 e foram registrados como sinais (10.705 de severidade alta, com até 3 nós, e 27.562 de severidade média). A página `/sinais/doacao-circular` permite filtrar por severidade, ordenar por valor ou comprimento do ciclo e acessar o grafo interativo. Ciclos podem ter explicações legítimas, como coligações ou ressarcimentos, e exigem verificação individual.

### Sócio fornecedor (`candidate_supplier_partner`)

Relaciona candidatos que constam no quadro societário de empresas remuneradas por campanhas. Como a Receita Federal publica o CPF de sócios de forma mascarada, a correspondência exige nome normalizado idêntico e coincidência dos seis dígitos visíveis do CPF. Por não confirmar identidade, o resultado é mantido fora de `people` e `signal_actor` e rotulado como vínculo possível. Casos ambíguos, em que mais de uma pessoa atende aos critérios, são descartados.

Na base completa, foram identificados 533 vínculos possíveis, envolvendo R$ 197,9 milhões movimentados nessas empresas. Em 66 casos, a campanha do próprio candidato contratou a empresa da qual ele é sócio (por exemplo, gráficas ou escritórios de advocacia). Os resultados estão disponíveis em `/sinais/socio-fornecedor`.

### Revisão por LLM (`ai-review`, opcional)

O módulo `elosys/rules/ai_review.py` submete os fatos de cada sinal de doação circular ou despesa desproporcional a um modelo de linguagem (DeepSeek), que avalia se o caso aparenta ser rotineiro ou atípico. A resposta, a justificativa, os fatos citados e o prompt utilizado são armazenados em `signal_ai_review` (um registro por sinal e modelo), permitindo auditoria humana do raciocínio.

O processo é incremental: novas execuções ampliam a cobertura e `--refresh` reprocessa sinais já avaliados. A ordenação pode priorizar valor (`--order amount`) ou ciclos mais curtos (`--order tight`). A chave de API deve ser fornecida via `DEEPSEEK_API_KEY`. Os resultados estão em `/sinais/analise-ia`. A avaliação do modelo é um elemento auxiliar e também está sujeita a erros.

## Registros de execução e auditoria

Cada execução de coletor cria ou atualiza, no mesmo diretório do banco:

- **`manifest.json`**: relação de todos os arquivos baixados, com URL, data de acesso, SHA-256 do arquivo compactado e de cada CSV contido nele. É o elemento central de não repúdio: uma vez versionado, o histórico público do repositório comprova o que foi coletado e quando.
- **Relatórios por coletor** (`tse_candidates_report.json`, `tse_accounts_report.json`, `tse_social_report.json`): linhas lidas por ano, registros gerados, CPFs descartados por ambiguidade e respectivos motivos, e registros sem vínculo de identidade.

A saída de console também serve como log: cada coletor exibe URL, tamanho e hash dos arquivos, progresso do processamento e um resumo por ano.

## Decisões de arquitetura

As decisões de arquitetura estão documentadas em `ADs/`, uma por tema:

| Documento | Princípio |
|---|---|
| `confiabilidade.md` | Não repúdio. Nenhum registro existe sem referência à coleta de origem. O arquivo bruto não é armazenado; guardam-se URL, data e SHA-256 para verificação posterior. |
| `imutabilidade.md` | *Rewrite-only*. O banco é reconstruído integralmente a cada execução. A proteção contra alterações retroativas decorre do `manifest.json` versionado e do build determinístico. |
| `banco.md` | SQLite em arquivo único, sem servidor. Datas em ISO 8601 (UTC), valores monetários em centavos, nomes de tabelas e colunas em inglês. |
| `identidade.md` | A identidade de uma pessoa é uma inferência do sistema, não um dado da fonte. A correspondência é determinística por título eleitoral e CPF; em caso de ambiguidade, o CPF é descartado e o motivo registrado. |
| `politician.md` | Não há entidade "político"; o modelo registra candidaturas por eleição (`politician_history`). O CPF mascarado de 2024 é reconciliado pelo título eleitoral. |
| `dados_derivados.md` | Correlações e sinais também possuem proveniência: regra, versão e registros utilizados. A severidade é limitada a `low`, `medium` e `high`. |

## Fontes de dados

Todas as fontes são oficiais e públicas.

| Fonte | Conteúdo | Situação |
|---|---|---|
| TSE: `consulta_cand` | Cadastro de candidaturas | Coletado (2014–2026) |
| TSE: prestação de contas eleitorais | CNPJ de campanha, doações, despesas contratadas e pagas | Coletado |
| TSE: `rede_social_candidato` | Redes sociais e sites declarados (obrigatórios desde a Res. TSE 23.610/2019) | Coletado (2018–2026) |
| X (via Apify) | Publicações de contas declaradas ao TSE, filtradas por léxico e triadas por LLM (ver `ADs/dados_derivados.md`, §1.4) | Coletado (eleitos federais) |
| TSE: `bem_candidato` | Bens declarados no registro de candidatura | Coletado (2014–2026) |
| TSE: `foto_cand` (DivulgaCandContas) | Foto oficial por candidatura | Coleta parcial e incremental (ver `ADs/politician.md`, §5) |
| Receita Federal (BrasilAPI) | Quadro societário, data de abertura e capital social de CNPJ | Coleta incremental (ver `ADs/politician.md`, §2.3) |
| Portal da Transparência: CEIS/CNEP | Pessoas e empresas impedidas de contratar com o poder público ou punidas por corrupção | Coletado (snapshot diário) |

**Dados não coletados:** endereço residencial, telefone e e-mail pessoal de candidatos; antecedentes fora de processos públicos; relatórios do COAF.


## Premissas legais e éticas

- Todas as fontes utilizadas são públicas por determinação legal ou judicial.
- O CPF de candidatos foi publicado de forma mascarada em 2024, por decisão do TSE fundamentada na LGPD, e voltou a ser divulgado integralmente em 2026. Os dados de 2024 são reconciliados pelo título eleitoral (ver `ADs/identidade.md`).
- Os resultados constituem indícios, não provas. O sistema gera sinais de alerta, e nenhum deles deve ser tratado como acusação pública sem apuração formal pelos órgãos competentes.

