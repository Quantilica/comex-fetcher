# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido

- `catalog`: o ano do comércio (NCM, `EXP_<ano>.csv`/`IMP_<ano>.csv` e as versões municipais) deixa de ser fixado na importação do módulo: é calculado a cada `list_datasets` (parâmetro `today`, só para testes). `GROUPS` guarda só o nome de cada grupo; as entradas saem de `list_datasets`.
- `catalog`: em janeiro o arquivo do ano novo ainda não existe (404, ou o "soft-206" do servidor), e o `sync` saía 3 todo dia até o MDIC publicar o primeiro mês. As entradas do ano corrente (NCM e municipal; as tabelas e a série NBM, fechadas, nunca) levam `pending_publication` por 60 dias desde 1º de janeiro (`PENDING_GRACE_DAYS`, estimativa: a divulgação de janeiro sai no começo de fevereiro). Nesse período, o `sync` do host conta o arquivo ausente como "ainda não publicado" (pulado, sem erro; no `check`, motivo `pending-publication`). Passada a folga, o arquivo ausente volta a ser erro.
- `sync`: o soft-206 (206 com código PHP no lugar de um arquivo inexistente) é o 404 do servidor. Passa a levantar `ServerFileMissingError` (subclasse de `CorruptPayloadError`, mesma família do erro de hoje, com a mensagem acrescida de "soft-206"), e só para entrada marcada com `pending_publication` o `ComexFetcherApp.download_entry` o converte em 404. Para as demais entradas, nada muda: segue erro do arquivo. HTML (manutenção, WAF) nunca é convertido.

### Alterado

- Requer `quantilica-cli>=0.30.0` como host (reconhece `pending_publication`).

## [2.7.2] - 2026-11-27

### Corrigido

- `lake`: brutos salvos com o nome do servidor (`EXP_1997.csv`, `IMP_2024_MUN.csv`, `EXP_1989_NBM.csv`, sem carimbo `@AAAAMMDD`) contam como a versão mais antiga da chave do fetcher (`exp_1997`, `imp-mun_2024`, `exp-nbm_1989`). Antes, `select_current` os tratava como outro arquivo: ao lado da versão carimbada, a partição recebia dois Parquets com as mesmas linhas (`exp/ano=1997/EXP_1997.parquet` e `exp_1997.parquet`). Agora só a versão carimbada é convertida, e o nome do servidor só entra quando está sozinho.
- `lake`: o ano é lido também de `EXP_2024_MUN.csv` e `IMP_1989_NBM.csv`. O `\b` do padrão não separa dígito de `_`, e esses nomes davam "não foi possível inferir ano da partição".
- `lake`: bruto com nome do servidor que não combina com a pasta (`exp-mun/EXP_1989_NBM.csv`) é ignorado com aviso, em vez de gravar linhas NBM no dataset municipal.

## [2.7.1] - 2026-11-19

### Adicionado

- Testes: identidade do registro conferida.

### Alterado

- Piso de `quantilica-analytics` do extra `analysis` sobe para 0.15.0 (`origin_outputs`, `LakeWriter.origin_complete`).
- CI e infraestrutura alinhados ao template (fetcher-template v0.2.1).

### Corrigido

- `lake`: o build sem mudança não lê mais o bruto. CSV e JSON (`ncm-vigente`) conferem `is_current` (sha256 do sidecar e rodapé do Parquet) antes de `check_file`. XLSX e ZIP declaram, em cada Parquet, a lista de todas as saídas do arquivo (`origin_outputs`: uma por aba, por CSV e por aba de XLSX de membro, listadas antes da primeira gravação) e só são pulados, sem abrir a planilha nem o ZIP, quando todas existem com o sha256 atual (`origin_complete`); antes, todo membro era extraído para um temporário antes de decidir. Uma conversão interrompida, um membro ou aba que falha e o erro "membros não tabulares ignorados" (declarado com ids `!erro/<membro>`, que nunca coincidem com a chave de uma saída real, mesmo com `a.csv` e `a.txt` no mesmo ZIP) deixam a declaração incompleta de propósito, e o arquivo é reaberto e o erro contado a cada build, como antes. Lake gravado sem a declaração reconverte uma vez e depois pula. As contagens de `converted`/`skipped`, `force` e o bruto novo ou alterado seguem como antes.
- CI: o pyproject declara o PyPI antes do índice Quantilica (`[[tool.uv.index]]`), e o workflow perde `--index` e `--index-strategy`. Com a estratégia padrão `first-index`, o `uv sync` só consulta o índice para o que não está no PyPI (`quantilica-analytics`) e deixa de receber o 503 intermitente que o GitHub Pages devolve a caminhos inexistentes.

## [2.7.0] - 2026-11-14

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, apelidos, órgão, licença, página e cadência) para o registro de fetchers da Quantilica.

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).

## [2.6.0] - 2026-11-10

### Corrigido
- Tabelas auxiliares (`auxiliary-tables`): os CSV passam a ser lidos com o dialeto fixo da fonte (campos entre aspas duplas, aspa no texto escrita `""`). Antes o DuckDB deduzia o dialeto e errava: na tabela `sh` as aspas ficavam literais e os textos com `;` (por exemplo `Lives animals; Animal products`) eram divididos, de modo que 4.918 das 6.620 linhas ganhavam valores nas colunas espúrias `column16` a `column36`; agora `sh` sai com as 16 colunas do cabeçalho e 6.620 linhas. Também deixam de sair com `""` literal os textos de `cgce`, `ppe` e `ppi`, e os nomes de `uf_mun` voltam a ter o apóstrofo (`LAGOA D'ANTA`, antes `LAGOA DANTA`). O dialeto vale para todos os CSV do Comex; em amostras de `exp`, `imp`, `exp-mun`, `exp-nbm` e `validacao` o resultado é idêntico.
- Tabelas auxiliares: os códigos das abas da planilha (`co_cgce_n1` a `n3`, `co_cuci_sub`, `co_cuci_divisao`, `co_cuci_sec`, `co_cuci_grupo`, `co_isic_grupo`, `co_isic_divisao`, `co_isic_secao`, `co_siit`, `co_pais_ison3`, `co_pais_isoa3`, `co_bloco`, `co_mun_geo`, `co_ncm_secrom`, `co_exp_set`, `co_exp_subset`) passam a ser texto, como nos CSV; antes viravam inteiro nas abas e a mesma coluna tinha dois tipos no dataset.

**Como reconverter `auxiliary-tables`.** O nome dos Parquets e as partições não mudam (o dataset não tem partição), mas o conteúdo mudou e o bruto continua o mesmo, então uma conversão comum pularia os arquivos como já convertidos. Apague antes a pasta `comex/auxiliary-tables/` do lake e converta de novo o dataset `auxiliary-tables`. Os outros datasets não precisam ser refeitos.

### Adicionado
- Documentação dos dados em `docs/`, conforme a norma de documentação dos dados: página da fonte, página de cada um dos dez datasets com dicionário de todas as variáveis e esquema de referência do lake. Um teste a verifica.

## [2.5.2] - 2026-11-05

### Corrigido
- `convert` sem o extra `analysis` falha com a instrução de instalação (`quantilica install comex --extra analysis`) em vez de um erro de import genérico, e o `sync` passa a ter diretório de saída padrão fixo.
- O extra `analysis` passa a instalar o `fastexcel`, de que o Polars precisa para ler as planilhas `.xlsx` (Repetro e tabelas auxiliares); sem ele a conversão desses arquivos falhava com `required package 'fastexcel' not found`.

## [2.5.1] - 2026-11-04

### Corrigido
- A conversão de CSV com aspas irregulares (campo que abre `"` e não fecha, ou aspa no meio do texto, como em `ncm@20261006.csv`) não falha mais: o arquivo é reescrito com as aspas reparadas, uma linha continua sendo um registro e nenhuma é perdida.

## [2.5.0] - 2026-11-04

### Adicionado
- Dataset `ncm-vigente` (tabela NCM do Siscomex, 15.157 linhas) no Lake.
- A conversão lê arquivos `.zip` e todas as abas de planilhas XLSX (antes só a primeira).

### Corrigido
- O `sync` descarta a resposta `206` com código PHP que o servidor devolve para arquivo inexistente, em vez de gravá-la como dado.

## [2.4.0] - 2026-11-04

### Corrigido
- Política de frescor volta a F1 (`HEAD_OR_MANIFEST`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.

### Alterado
- Exige `quantilica-core>=0.16.0`.

## [2.3.3] - 2026-10-29

### Corrigido

- Os downloads passam a usar `https://balanca.mdic.gov.br/balanca/bd/`, o novo
  endereço do Comex Stat. O anterior (`balanca.economia.gov.br`) deixou de
  responder e todo `sync` falhava. Os caminhos dos arquivos não mudaram.
- Atenção: o servidor novo responde `206` com código PHP, e não `404`, quando o
  arquivo pedido não existe (ano fora da faixa ou ainda não publicado). Valide
  o conteúdo do arquivo, não só o status.

## [2.3.2] - 2026-10-20

### Alterado

- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com
  código 1 e orienta `quantilica install <fonte>`.
- `pyproject.toml`: removidos os `per-file-ignores` de B008 para `cli.py`/
  `plugin.py` (obsoletos; `ruff check` continua limpo).

## [2.3.1] - 2026-08-31
### Corrigido
- Quitação de dívida de lint (E501) em docstrings; nenhum comportamento alterado.

## [2.3.0] - 2026-08-07
### Alterado
- Refatoração arquitetural: Remoção de dependências (`quantilica-cli` e `quantilica-catalog`) e limpeza de imports. Os fetchers agora são pacotes de extração puros, dependendo estritamente do `quantilica-core`.

## [2.1.0] - 2026-07-30

### Adicionado

- Novas opções no comando `sync` do CLI e plugin Typer: `--repetro`, `--validation` e `--other-tables` para permitir baixar dados do REPETRO, totais para validação e tabelas auxiliares em Excel.

### Alterado

- Atualizado `pyproject.toml` para o padrão PEP 639 de licenças, utilizando `license = "MIT"` e especificando a dependência do `hatchling>=1.27`.

## [2.0.0] - 2026-05-19

Primeira entrada em formato Keep a Changelog. O pacote foi renomeado de
`comexdown` para `comex-fetcher` e integrado ao ecossistema Quantilica.

### Alterado

- Renomeado de `comexdown` para `comex-fetcher` (ver guia de migração no README).

### Adicionado

- CLI standalone (`comex-fetcher`, argparse) e plugin Typer para o `quantilica-cli`
  (`quantilica comex`), com o comando `sync`.
- Manifestos de proveniência (`DownloadManifest`) via `quantilica-core`.
- Download de exportações, importações, dados municipais, série histórica NBM e
  tabelas auxiliares de códigos (NCM, países, UF, via).

**Histórico anterior.**

Versões até a 2.0.0 antecedem a adoção deste changelog e estão registradas nas
tags do repositório: 1.5.2 (2025-12-24), 1.4.1 (2024-03-08), 1.4.0 (2022-07-07),
1.3.3 (2021-04-23), 1.0 (2020-05-25), 0.9 (2020-04-30) — as anteriores à 2.0.0
ainda sob o nome `comexdown`.
