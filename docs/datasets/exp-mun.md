---
dataset:
  id: exp-mun
  fonte: comex
  titulo: "Exportações brasileiras por município da empresa e SH4"
  resumo: "Exportações do Brasil por mês, posição SH4, país e município (domicílio fiscal) da empresa exportadora."
  orgao: "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX)"
  pagina_oficial: "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
  licenca: "Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas"
  periodicidade: "mensal; o arquivo do ano corrente cresce a cada mês (a fonte não declara periodicidade formal)"
  cobertura: {inicio: 1997-01, fim: em-curso}
  unidade: "exportação de uma posição SH4, num mês, para um país, por município e UF da empresa declarante (linha agregada)"
  granularidade: {espacial: "município e UF do domicílio fiscal da empresa", temporal: "mês"}
  formato_bruto: "CSV `EXP_AAAA_MUN.csv` / `IMP_AAAA_MUN.csv` (um por ano), separador ponto e vírgula, cabeçalho na primeira linha, campos de código entre aspas e medidas sem aspas, terminador CRLF; os arquivos conferidos são ASCII e o fetcher os lê como latin-1"
  lake: {estado: convertido, particoes: [ano], chave: [co_ano, co_mes, sh4, co_pais, sg_uf_mun, co_mun], colunas: 8}
  unidades_de_medida:
    kg_liquido: "quilograma líquido (kg)"
    vl_fob: "US$ FOB (valor em dólar)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# Exportações brasileiras por município da empresa e SH4

## Resumo

As exportações brasileiras abertas pelo município do domicílio fiscal da empresa que declarou a operação, com a mercadoria no nível de posição SH4. Responde onde estão as empresas que exportam ou importam, não onde a mercadoria foi produzida ou consumida. O detalhe por NCM, UF do produto, via e URF está em `exp`.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/exp-mun` |
| Órgão | Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX) |
| Página oficial | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas |
| Periodicidade | mensal; o arquivo do ano corrente cresce a cada mês (a fonte não declara periodicidade formal) |
| Cobertura | 1997-01 a em-curso |
| Unidade (uma linha) | exportação de uma posição SH4, num mês, para um país, por município e UF da empresa declarante (linha agregada) |
| Granularidade | espacial: município e UF do domicílio fiscal da empresa; temporal: mês |
| Formato bruto | CSV `EXP_AAAA_MUN.csv` / `IMP_AAAA_MUN.csv` (um por ano), separador ponto e vírgula, cabeçalho na primeira linha, campos de código entre aspas e medidas sem aspas, terminador CRLF; os arquivos conferidos são ASCII e o fetcher os lê como latin-1 |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `co_ano`, `co_mes`, `sh4`, `co_pais`, `sg_uf_mun`, `co_mun` |
| Colunas | 8 |
| Unidades de medida | `kg_liquido`: quilograma líquido (kg); `vl_fob`: US$ FOB (valor em dólar) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa um CSV por ano e direção da base de dados bruta do MDIC (`https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/mun/EXP_AAAA_MUN.csv`). No bruto, o arquivo recebe um sufixo de data, `exp-mun_AAAA@AAAAMMDD.csv`, e um arquivo `.manifest.json` ao lado. O sufixo registra a data de última modificação informada pelo servidor; quando o servidor publica uma versão nova do mesmo ano, as duas ficam no bruto e o lake converte a mais recente.
- O fetcher confere a primeira linha útil de cada CSV e descarta respostas que não são dados (a fonte devolve `206` com código PHP para arquivo inexistente). Os arquivos únicos (`*_COMPLETA.zip`), que o MDIC deixou de oferecer em 2025, a calendarização (`dados_calendario.xlsx`) e as correlações das classificações antigas não são baixados.
- Versões no bruto conferidas em 2026-11-09: um arquivo por ano, de 1997 a 2026 (conferido pela listagem do bruto).

## Conteúdo

- Uma linha por mês, SH4, país, UF e município da empresa declarante. A chave da fonte é única nas amostras convertidas (zero duplicatas em 1997, 2010 e 2026).
- Cobertura anunciada pela fonte: 1997 a 2026. Cobertura no bruto: 30 arquivos anuais, 1997 a 2026 (conferido em 2026-11-09). O arquivo de 2026 coletado em 2026-10-06 traz os meses 01 a 09.
- Conferência por amostra (1997, 2010 e 2026): o número de linhas e as somas de `vl_fob` e `kg_liquido` são iguais às do arquivo de totais para validação; todos os `co_mun` das amostras existem em `uf_mun`.
- Os totais anuais de `vl_fob` e `kg_liquido` coincidem com os do dataset `exp` nos anos conferidos (pelos totais de validação de 1997, 2005, 2010, 2015, 2020, 2024 e 2025).
- Há municípios com `sg_uf_mun` `ND` (não declarada): 12 linhas em 2010 e 401 em 2026 (conferido nas amostras).

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_ano` | `CO_ANO` | texto | Ano de referência (nome do campo; a fonte não descreve) | AAAA | todo |
| `co_mes` | `CO_MES` | texto | Mês de referência (nome do campo; a fonte não descreve) | `01` a `12` | todo |
| `sh4` | `SH4` | texto | Posição do Sistema Harmonizado (SH4) da mercadoria | 4 dígitos; tabela `sh`, coluna `co_sh4` | todo |
| `co_pais` | `CO_PAIS` | texto | Código do país de destino da mercadoria | 3 dígitos; tabela `pais` | todo |
| `sg_uf_mun` | `SG_UF_MUN` | texto | Sigla da UF da empresa declarante (domicílio fiscal) | sigla; tabela `uf` (`ND` = não declarada) | todo |
| `co_mun` | `CO_MUN` | texto | Código do município da empresa declarante (domicílio fiscal) | 7 dígitos (código de município; tabela `uf_mun`, coluna `co_mun_geo`) | todo |
| `kg_liquido` | `KG_LIQUIDO` | texto | Peso líquido | quilograma | todo |
| `vl_fob` | `VL_FOB` | texto | Valor FOB da operação | US$ | todo |
| `ano` | — (partição) | inteiro | Ano do arquivo bruto (extraído do nome do arquivo); igual a `co_ano` | — | todo |

## No lake

- Dataset `comex/exp-mun`, particionado por `ano` (inteiro); um Parquet por ano (`exp-mun_AAAA.parquet`).
- Conversão com o DuckDB em latin-1, separador `;`, todas as colunas como texto, nomes em minúsculas. Os zeros à esquerda de `sh4` e `co_pais` são preservados.
- Nenhuma linha é descartada: a contagem do lake é a do bruto menos o cabeçalho, em todas as amostras.

## Cuidados de uso

- **Município da empresa, não da mercadoria.** A fonte descreve `CO_MUN` como município da empresa declarante. O valor de uma exportação feita por uma trading sediada em São Paulo aparece em São Paulo, mesmo que a mercadoria venha de outro estado.
- **Medidas em texto.** `kg_liquido` e `vl_fob` são `VARCHAR`; converta antes de somar.
- **Não some com `exp`.** O total anual de `exp-mun` é o mesmo de `exp`, só aberto de outra forma.
- **Sem quantidade estatística.** O arquivo municipal não tem `qt_estat`, NCM nem via; só SH4 e peso líquido.
- **Ano corrente parcial.** O arquivo de 2026 vai até o último mês divulgado (09 na coleta de 2026-10-06).
- **Valor FOB em US$ sem ajuste de inflação.**

## Exemplos

As cinco UFs de domicílio fiscal com maior valor exportado em 2025 (US$ bilhões):

```python
import polars as pl

df = pl.scan_parquet("lake/comex/exp-mun/**/*.parquet", hive_partitioning=True)
top = (
    df.filter(pl.col("ano") == 2025)
    .group_by("sg_uf_mun")
    .agg((pl.col("vl_fob").cast(pl.Int64).sum() / 1e9).alias("bi_usd"))
    .sort("bi_usd", descending=True)
    .head(5)
    .collect()
)
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
