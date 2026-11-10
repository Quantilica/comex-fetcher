---
dataset:
  id: imp
  fonte: comex
  titulo: "Importações brasileiras por NCM"
  resumo: "Importações do Brasil por mês, NCM, país, UF, via e URF, em valor FOB, peso líquido e quantidade estatística."
  orgao: "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX)"
  pagina_oficial: "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
  licenca: "Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas"
  periodicidade: "mensal; o arquivo do ano corrente cresce a cada mês (a fonte não declara periodicidade formal)"
  cobertura: {inicio: 1997-01, fim: em-curso}
  unidade: "importação de uma NCM, num mês, por unidade estatística, país, UF, via e URF (linha agregada, não uma operação individual)"
  granularidade: {espacial: "UF do produto, país e URF", temporal: "mês"}
  formato_bruto: "CSV `EXP_AAAA.csv` / `IMP_AAAA.csv` (um por ano), separador ponto e vírgula, cabeçalho na primeira linha, campos de código entre aspas e medidas sem aspas, terminador CRLF; os arquivos conferidos são ASCII e o fetcher os lê como latin-1"
  lake: {estado: convertido, particoes: [ano], chave: [co_ano, co_mes, co_ncm, co_unid, co_pais, sg_uf_ncm, co_via, co_urf], colunas: 13}
  unidades_de_medida:
    qt_estat: "quantidade na unidade estatística indicada em co_unid (ver tabela unidade)"
    kg_liquido: "quilograma líquido (kg)"
    vl_fob: "US$ FOB (valor em dólar)"
    vl_frete: "não informado pela fonte"
    vl_seguro: "não informado pela fonte"
  dados_pessoais: nenhum
  eras:
    - {desde: 1997-01, mudanca: "nomenclatura NCM; de 1989 a 1996 a série usa a NBM (dataset imp-nbm)"}
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# Importações brasileiras por NCM

## Resumo

As importações brasileiras detalhadas por Nomenclatura Comum do Mercosul (NCM), que alimentam a balança comercial e o Comex Stat. Cada linha soma as operações de um mês com a mesma NCM, unidade estatística, país, UF do produto, via de transporte e URF. A importação traz, além do valor FOB, o frete e o seguro. Os arquivos municipais (`imp-mun`) reabrem o mesmo total por município da empresa e posição SH4.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/imp` |
| Órgão | Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX) |
| Página oficial | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas |
| Periodicidade | mensal; o arquivo do ano corrente cresce a cada mês (a fonte não declara periodicidade formal) |
| Cobertura | 1997-01 a em-curso |
| Unidade (uma linha) | importação de uma NCM, num mês, por unidade estatística, país, UF, via e URF (linha agregada, não uma operação individual) |
| Granularidade | espacial: UF do produto, país e URF; temporal: mês |
| Formato bruto | CSV `EXP_AAAA.csv` / `IMP_AAAA.csv` (um por ano), separador ponto e vírgula, cabeçalho na primeira linha, campos de código entre aspas e medidas sem aspas, terminador CRLF; os arquivos conferidos são ASCII e o fetcher os lê como latin-1 |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `co_ano`, `co_mes`, `co_ncm`, `co_unid`, `co_pais`, `sg_uf_ncm`, `co_via`, `co_urf` |
| Colunas | 13 |
| Unidades de medida | `qt_estat`: quantidade na unidade estatística indicada em co_unid (ver tabela unidade); `kg_liquido`: quilograma líquido (kg); `vl_fob`: US$ FOB (valor em dólar); `vl_frete`: não informado pela fonte; `vl_seguro`: não informado pela fonte |
| Dados pessoais | nenhum |
| Eras | 1997-01: nomenclatura NCM; de 1989 a 1996 a série usa a NBM (dataset imp-nbm) |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa um CSV por ano e direção da base de dados bruta do MDIC (`https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_AAAA.csv`). No bruto, o arquivo recebe um sufixo de data, `imp_AAAA@AAAAMMDD.csv`, e um arquivo `.manifest.json` ao lado. O sufixo registra a data de última modificação informada pelo servidor; quando o servidor publica uma versão nova do mesmo ano, as duas ficam no bruto e o lake converte a mais recente.
- O fetcher confere a primeira linha útil de cada CSV e descarta respostas que não são dados (a fonte devolve `206` com código PHP para arquivo inexistente). Os arquivos únicos (`*_COMPLETA.zip`), que o MDIC deixou de oferecer em 2025, a calendarização (`dados_calendario.xlsx`) e as correlações das classificações antigas não são baixados.
- Versões no bruto conferidas em 2026-11-09: um arquivo por ano, de 1997 a 2026 (conferido pela listagem do bruto).

## Conteúdo

- Uma linha por combinação de mês, NCM, unidade estatística, país, UF, via e URF. A chave da fonte é única nas amostras convertidas (zero duplicatas em 1997, 2005, 2015, 2025 e 2026).
- Cobertura anunciada pela fonte: 1997 a 2026 ("Últimos dados disponíveis: janeiro - outubro de 2026", página atualizada em 06/11/2026). Cobertura no bruto: 30 arquivos anuais, 1997 a 2026 (conferido em 2026-11-09). O arquivo de 2026 coletado em 2026-10-06 traz os meses 01 a 09.
- Conferência por amostra: convertidos 1997, 2005, 2015, 2025 e 2026 (amostra); o número de linhas, a soma de `vl_fob`, `kg_liquido` e `qt_estat`, `vl_frete` e `vl_seguro` de cada ano é igual ao do arquivo de totais para validação (dataset `validacao`) publicado pela fonte.
- Todas as linhas amostradas têm NCM com 8 dígitos e, todo código de NCM, país, via, URF e unidade das amostras existe nas tabelas auxiliares do mesmo lote (conferido em 2026-11-10).
- Eras: de 1989 a 1996 a fonte publica a série histórica pela NBM (`imp-nbm`); a partir de 1997, pela NCM, neste dataset. Não há outra quebra de layout nas amostras.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_ano` | `CO_ANO` | texto | Ano de referência (nome do campo; a fonte não descreve) | AAAA | todo |
| `co_mes` | `CO_MES` | texto | Mês de referência (nome do campo; a fonte não descreve) | `01` a `12` | todo |
| `co_ncm` | `CO_NCM` | texto | Código da mercadoria na Nomenclatura Comum do Mercosul (NCM) | 8 dígitos, com zeros à esquerda; tabela `ncm` | todo |
| `co_unid` | `CO_UNID` | texto | Código da unidade estatística da NCM, na qual `qt_estat` é medida | 2 dígitos, `10` a `24`; tabela `unidade` | todo |
| `co_pais` | `CO_PAIS` | texto | Código do país de origem da mercadoria | 3 dígitos; tabela `pais` | todo |
| `sg_uf_ncm` | `SG_UF_NCM` | texto | Sigla da UF de origem (exportação) ou destino (importação) do produto, segundo a página; aceita também códigos que não são UF | sigla de 2 letras; tabela `uf` (`ND` = não declarada) | todo |
| `co_via` | `CO_VIA` | texto | Código da via de transporte | 2 dígitos, `00` a `15` e `99`; tabela `via` | todo |
| `co_urf` | `CO_URF` | texto | Código da Unidade da Receita Federal de embarque (exportação) ou desembarque (importação) | 7 dígitos; tabela `urf` | todo |
| `qt_estat` | `QT_ESTAT` | texto | Quantidade estatística, na unidade de `co_unid`. Zero quando a quantidade não se aplica ou não foi informada | unidade de `co_unid` | todo |
| `kg_liquido` | `KG_LIQUIDO` | texto | Peso líquido | quilograma | todo |
| `vl_fob` | `VL_FOB` | texto | Valor FOB da operação | US$ | todo |
| `vl_frete` | `VL_FRETE` | texto | Valor do frete (nome do campo; a fonte não descreve nem informa a moeda) | não informado pela fonte | todo |
| `vl_seguro` | `VL_SEGURO` | texto | Valor do seguro (nome do campo; a fonte não descreve nem informa a moeda) | não informado pela fonte | todo |
| `ano` | — (partição) | inteiro | Ano do arquivo bruto (extraído do nome do arquivo); igual a `co_ano` | — | todo |

## No lake

- Dataset `comex/imp`, particionado por `ano` (inteiro, extraído do nome do arquivo); um Parquet por ano (`imp_AAAA.parquet`).
- A conversão lê o CSV com o DuckDB em latin-1, separador `;`, **todas as colunas como texto**: não há conversão de tipo. Os nomes das colunas ficam em minúsculas. Os zeros à esquerda de `co_ncm`, `co_urf`, `co_via` e `co_pais` são preservados.
- `co_ano` (texto) repete a partição `ano` (inteiro).
- Nenhuma linha é descartada: a contagem de linhas do lake é igual à do arquivo bruto menos o cabeçalho, em todas as amostras.
- A chave de arquivo no lake é o nome do arquivo sem a data (`imp_AAAA`); uma versão mais nova do mesmo ano o substitui.

## Cuidados de uso

- **Medidas em texto.** `qt_estat`, `kg_liquido` e `vl_fob` são `VARCHAR` no lake; converta antes de somar (`TRY_CAST(... AS BIGINT)`). Nas amostras todos os valores são inteiros (zero falhas de conversão).
- **Valor FOB em US$, sem ajuste.** A fonte informa dólar FOB; não informa deflator nem câmbio. Séries longas em dólar nominal não descontam inflação.
- **`qt_estat` não é comparável entre linhas.** A unidade muda com `co_unid` (quilograma, número, litro, metro cúbico...). Somar `qt_estat` entre NCMs distintas não tem sentido. Em exportação de 2026, em 66.826 das 874.235 linhas com `co_unid` 10 (quilograma), `qt_estat` é 0; a quantidade então só está em `kg_liquido` (conferido em 2026-11-10).
- **Linhas com valor zero.** Há linhas com `vl_fob` igual a 0 (por exemplo 1.036 em 1997 e 2.806 em 2026) e muitas com `kg_liquido` 0 (conferido nas amostras): são mercadorias de valor ou peso desprezível, não erros de leitura.
- **Ano corrente parcial.** O arquivo de 2026 vai só até o último mês divulgado (09 na coleta de 2026-10-06). Compare apenas meses completos.
- **Revisões.** A fonte afirma que anos anteriores estão congelados e que basta baixar o ano mais recente (Informativo 029/2025). Os sufixos de data dos arquivos recentes, porém, mostram uma nova versão de cada ano no início do ano seguinte (por exemplo, 2025 em 20260205).
- **Não some com `imp-mun` nem com `repetro`.** Os arquivos municipais repetem o mesmo valor total; os totais de `vl_fob` e `kg_liquido` de imp e imp-mun coincidem em todos os anos conferidos (1997, 2005, 2010, 2015, 2020, 2024 e 2025, pelos totais de validação). A série REPETRO é separada e não compõe a balança divulgada.
- **Códigos que não são lugar.** `sg_uf_ncm` aceita valores como `ND` (não declarada); `co_pais` `000` é "Não Definido". Consulte as tabelas auxiliares antes de agrupar por UF ou país.
- **Excel.** A própria fonte avisa que softwares de planilha podem perder linhas: use ferramentas de banco de dados.

## Exemplos

Valor importado (US$ bilhões) por UF do produto em 2025, com as 5 maiores:

```python
import polars as pl

df = pl.scan_parquet("lake/comex/imp/**/*.parquet", hive_partitioning=True)
top = (
    df.filter(pl.col("ano") == 2025)
    .with_columns(pl.col("vl_fob").cast(pl.Int64))
    .group_by("sg_uf_ncm")
    .agg((pl.col("vl_fob").sum() / 1e9).alias("bi_usd"))
    .sort("bi_usd", descending=True)
    .head(5)
    .collect()
)
```

O mesmo em DuckDB, com os códigos descritos pela tabela `uf`:

```sql
SELECT e.sg_uf_ncm, u.no_uf, SUM(TRY_CAST(e.vl_fob AS BIGINT)) / 1e9 AS bi_usd
FROM read_parquet('lake/comex/imp/*/*.parquet', hive_partitioning = true) e
LEFT JOIN read_parquet('lake/comex/auxiliary-tables/uf.parquet') u ON u.sg_uf = e.sg_uf_ncm
WHERE e.ano = 2025
GROUP BY ALL ORDER BY bi_usd DESC LIMIT 5;
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
