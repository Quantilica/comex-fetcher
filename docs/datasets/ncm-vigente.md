---
dataset:
  id: ncm-vigente
  fonte: comex
  titulo: "NCM vigente (Portal Único Siscomex)"
  resumo: "Nomenclatura Comum do Mercosul vigente, com descrição, vigência e ato legal de cada código, em todos os níveis hierárquicos."
  orgao: "Portal Único de Comércio Exterior (Siscomex), governo federal"
  pagina_oficial: "https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json"
  licenca: "não informado pela fonte; o download público do JSON não traz termo de uso"
  periodicidade: "sem periodicidade declarada; o arquivo informa a data em que a NCM está vigente (\"Vigente em 05/11/2026\")"
  cobertura: {inicio: 2022-04, fim: em-curso}
  unidade: "um código da hierarquia da NCM (capítulo, posição, subposições e item de 8 dígitos) com sua vigência"
  granularidade: {espacial: "não se aplica", temporal: "data de vigência (início e fim) do código"}
  formato_bruto: "JSON em UTF-8 com os campos `Data_Ultima_Atualizacao_NCM`, `Ato` e a lista `Nomenclaturas` (`Codigo`, `Descricao`, `Data_Inicio`, `Data_Fim`, `Tipo_Ato_Ini`, `Numero_Ato_Ini`, `Ano_Ato_Ini`)"
  lake: {estado: convertido, particoes: [], chave: [codigo], colunas: 11}
  unidades_de_medida:
    nivel_digitos: "dígitos do código (2 a 8)"
  dados_pessoais: nenhum
  eras:
    - {desde: 2022-04, mudanca: "início de vigência da nomenclatura atual (menor `data_inicio` do arquivo conferido)"}
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# NCM vigente (Portal Único Siscomex)

## Resumo

A tabela da NCM que o Portal Único Siscomex publica como vigente, com a hierarquia completa: capítulo (2 dígitos), posição (4), e os níveis intermediários até o item de 8 dígitos, cada um com descrição, datas de vigência e o ato que o instituiu. Complementa a tabela `ncm` de `auxiliary-tables`, que traz só os itens de 8 dígitos com as classificações da SECEX.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/ncm-vigente` |
| Órgão | Portal Único de Comércio Exterior (Siscomex), governo federal |
| Página oficial | https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json |
| Licença | não informado pela fonte; o download público do JSON não traz termo de uso |
| Periodicidade | sem periodicidade declarada; o arquivo informa a data em que a NCM está vigente ("Vigente em 05/11/2026") |
| Cobertura | 2022-04 a em-curso |
| Unidade (uma linha) | um código da hierarquia da NCM (capítulo, posição, subposições e item de 8 dígitos) com sua vigência |
| Granularidade | espacial: não se aplica; temporal: data de vigência (início e fim) do código |
| Formato bruto | JSON em UTF-8 com os campos `Data_Ultima_Atualizacao_NCM`, `Ato` e a lista `Nomenclaturas` (`Codigo`, `Descricao`, `Data_Inicio`, `Data_Fim`, `Tipo_Ato_Ini`, `Numero_Ato_Ini`, `Ano_Ato_Ini`) |
| Estado no lake | convertido |
| Partições | — |
| Chave | `codigo` |
| Colunas | 11 |
| Unidades de medida | `nivel_digitos`: dígitos do código (2 a 8) |
| Dados pessoais | nenhum |
| Eras | 2022-04: início de vigência da nomenclatura atual (menor `data_inicio` do arquivo conferido) |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa o JSON de `https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json?perfil=PUBLICO`. A fonte não envia `Last-Modified` nem `ETag`, então o arquivo do bruto recebe a data da coleta (`ncm-vigente@AAAAMMDD.json`) e o fetcher só grava uma nova versão se o conteúdo mudar (comparação por SHA-256).
- Versões no bruto conferidas em 2026-11-09: uma, `ncm-vigente@20261105.json` (3,1 MB).
- No JSON conferido, `Data_Ultima_Atualizacao_NCM` é `Vigente em 05/11/2026` e `Ato` é `Resolução Gecex nº 926/2026`.

## Conteúdo

- 15.157 linhas, todas com `data_fim` 9999-12-31 (vigente), `data_inicio` entre 2022-04-01 e 2026-10-01 e o mesmo ato (`Resolução Gecex nº 926/2026`) (conferido no arquivo de 2026-11-05).
- Níveis: 96 de 2 dígitos, 957 de 4, 1.024 de 5, 1.661 de 6, 903 de 7 e 10.516 de 8 dígitos. Os níveis de 5 e 7 dígitos são subdivisões intermediárias (por exemplo `0101.2`), não NCM completas. Para as NCM dos dados de comércio, use `nivel_digitos = 8`.
- O `codigo` é único no arquivo.
- Atos que iniciaram a vigência: `Res Gecex` (15.135 linhas) e `Res Camex` (22).
- O arquivo traz só o que está vigente na data indicada; não há histórico de códigos extintos.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `codigo` | `Codigo` | texto | Código da nomenclatura com pontos, em qualquer nível | ex.: `01`, `01.01`, `0101.2`, `0101.21.00` | todo |
| `codigo_ncm` | — (gerada de `Codigo`) | texto | `codigo` sem os pontos, para cruzar com `co_ncm` dos dados de comércio quando tem 8 dígitos | 2 a 8 dígitos | todo |
| `descricao` | `Descricao` | texto | Descrição do código na NCM | — | todo |
| `data_inicio` | `Data_Inicio` | data | Início de vigência do código (no JSON `DD/MM/AAAA`) | data | todo |
| `data_fim` | `Data_Fim` | data | Fim de vigência; `9999-12-31` quando o código segue vigente | data | todo |
| `tipo_ato_ini` | `Tipo_Ato_Ini` | texto | Tipo do ato que iniciou a vigência | `Res Gecex`, `Res Camex` | todo |
| `numero_ato_ini` | `Numero_Ato_Ini` | texto | Número do ato que iniciou a vigência | — | todo |
| `ano_ato_ini` | `Ano_Ato_Ini` | texto | Ano do ato que iniciou a vigência | AAAA | todo |
| `nivel_digitos` | — (gerada) | inteiro | Número de dígitos de `codigo_ncm` | 2 a 8 | todo |
| `vigente_em` | `Data_Ultima_Atualizacao_NCM` | texto | Data a que o arquivo se refere, no texto do JSON, repetido em todas as linhas | texto, ex.: `Vigente em 05/11/2026` | todo |
| `ato` | `Ato` | texto | Ato que institui a versão vigente da NCM, repetido em todas as linhas | texto, ex.: `Resolução Gecex nº 926/2026` | todo |

## No lake

- Dataset `comex/ncm-vigente`, sem partição; um Parquet (`ncm-vigente.parquet`).
- O JSON é lido com o Polars. `codigo` vira texto; `codigo_ncm` é o `codigo` sem os não dígitos; `data_inicio` e `data_fim` viram data (`DD/MM/AAAA` estrito: data inválida interrompe a conversão); `nivel_digitos` é o tamanho de `codigo_ncm`. `vigente_em` e `ato` vêm do cabeçalho do JSON e se repetem em todas as linhas.
- Uma nova versão do JSON (outro SHA-256) substitui o arquivo do lake.

## Cuidados de uso

- **Hierarquia misturada.** O arquivo mistura capítulo, posição e subdivisões na mesma lista. Filtre `nivel_digitos = 8` antes de cruzar com `co_ncm`.
- **Só o vigente.** Não há códigos extintos nem históricos de descrição. NCM que aparecem em anos antigos de `exp` e `imp` podem não existir aqui; use a tabela `ncm` de `auxiliary-tables` para esses casos.
- **Datas de início não são datas de criação do código.** `data_inicio` mínima é 2022-04-01, início da vigência da atual versão da nomenclatura, mesmo para códigos antigos.
- **Fim sentinela.** `data_fim` 9999-12-31 significa "vigente", não uma data real.
- **Sem licença declarada.** O download público não traz termo de uso; confirme as condições com o Portal Único antes de redistribuir.

## Exemplos

As NCM de 8 dígitos do capítulo 87 (veículos) vigentes:

```python
import polars as pl

ncm = pl.read_parquet("lake/comex/ncm-vigente/*.parquet")
cap87 = ncm.filter((pl.col("nivel_digitos") == 8) & pl.col("codigo_ncm").str.starts_with("87"))
print(cap87.height, cap87.select("codigo_ncm", "descricao").head())
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
- Download público da NCM, Portal Único Siscomex: https://portalunico.siscomex.gov.br/classif/api/publico/nomenclatura/download/json
