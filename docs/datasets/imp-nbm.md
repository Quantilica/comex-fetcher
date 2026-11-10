---
dataset:
  id: imp-nbm
  fonte: comex
  titulo: "Importações brasileiras por NBM (1989-1996)"
  resumo: "Série histórica das importações do Brasil por mês, NBM, país e UF, de 1989 a 1996."
  orgao: "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX)"
  pagina_oficial: "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
  licenca: "Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas"
  periodicidade: "encerrada (série histórica fechada em 1996)"
  cobertura: {inicio: 1989-01, fim: 1996-12}
  unidade: "importação de uma NBM, num mês, para um país e UF (linha agregada)"
  granularidade: {espacial: "UF e país", temporal: "mês"}
  formato_bruto: "CSV `EXP_AAAA_NBM.csv` / `IMP_AAAA_NBM.csv` (um por ano), separador ponto e vírgula, cabeçalho na primeira linha, campos de código entre aspas e medidas sem aspas, terminador CRLF; os arquivos conferidos são ASCII e o fetcher os lê como latin-1"
  lake: {estado: convertido, particoes: [ano], chave: [co_ano, co_mes, co_nbm, co_pais, sg_uf], colunas: 7}
  unidades_de_medida:
    kg_liquido: "quilograma líquido (kg)"
    vl_fob: "US$ FOB (valor em dólar)"
  dados_pessoais: nenhum
  eras:
    - {desde: 1997-01, mudanca: "a série continua na NCM (dataset imp); a NBM não é mais usada"}
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# Importações brasileiras por NBM (1989-1996)

## Resumo

Série histórica das importações brasileiras entre 1989 e 1996, classificadas pela Nomenclatura Brasileira de Mercadorias (NBM), anterior à NCM. A série contínua a partir de 1997 está em `imp`. A tabela `nbm_ncm`, em `auxiliary-tables`, converte NBM em NCM.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/imp-nbm` |
| Órgão | Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX) |
| Página oficial | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas |
| Periodicidade | encerrada (série histórica fechada em 1996) |
| Cobertura | 1989-01 a 1996-12 |
| Unidade (uma linha) | importação de uma NBM, num mês, para um país e UF (linha agregada) |
| Granularidade | espacial: UF e país; temporal: mês |
| Formato bruto | CSV `EXP_AAAA_NBM.csv` / `IMP_AAAA_NBM.csv` (um por ano), separador ponto e vírgula, cabeçalho na primeira linha, campos de código entre aspas e medidas sem aspas, terminador CRLF; os arquivos conferidos são ASCII e o fetcher os lê como latin-1 |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `co_ano`, `co_mes`, `co_nbm`, `co_pais`, `sg_uf` |
| Colunas | 7 |
| Unidades de medida | `kg_liquido`: quilograma líquido (kg); `vl_fob`: US$ FOB (valor em dólar) |
| Dados pessoais | nenhum |
| Eras | 1997-01: a série continua na NCM (dataset imp); a NBM não é mais usada |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa um CSV por ano e direção da base de dados bruta do MDIC (`https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/nbm/EXP_AAAA_NBM.csv`). No bruto, o arquivo recebe um sufixo de data, `imp-nbm_AAAA@AAAAMMDD.csv`, e um arquivo `.manifest.json` ao lado. O sufixo registra a data de última modificação informada pelo servidor; quando o servidor publica uma versão nova do mesmo ano, as duas ficam no bruto e o lake converte a mais recente.
- O fetcher confere a primeira linha útil de cada CSV e descarta respostas que não são dados (a fonte devolve `206` com código PHP para arquivo inexistente). Os arquivos únicos (`*_COMPLETA.zip`), que o MDIC deixou de oferecer em 2025, a calendarização (`dados_calendario.xlsx`) e as correlações das classificações antigas não são baixados.
- Versões no bruto conferidas em 2026-11-09: oito arquivos, 1989 a 1996, todos com o sufixo 20210113.

## Conteúdo

- Uma linha por mês, NBM, país e UF. A chave da fonte é única nas amostras convertidas (1989 e 1996).
- Cobertura anunciada pela fonte: 1989 a 1996. Cobertura no bruto: oito arquivos anuais, 1989 a 1996 (conferido em 2026-11-09). Cada ano das amostras tem os 12 meses.
- Amostras convertidas: 1989 (243.460 linhas) e 1996 (688.868); a contagem do lake é igual à do bruto menos o cabeçalho.
- Não há arquivo de totais para validação da série NBM, então as somas não foram comparadas com a fonte.
- Era: série encerrada em 1996-12; de 1997-01 em diante, os dados estão em `imp` (NCM).

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_ano` | `CO_ANO` | texto | Ano de referência (nome do campo; a fonte não descreve) | AAAA | 1989-1996 |
| `co_mes` | `CO_MES` | texto | Mês de referência (nome do campo; a fonte não descreve) | `01` a `12` | 1989-1996 |
| `co_nbm` | `CO_NBM` | texto | Código da mercadoria na Nomenclatura Brasileira de Mercadorias (NBM) | 10 dígitos; tabela `nbm` | 1989-1996 |
| `co_pais` | `CO_PAIS` | texto | Código do país de origem da mercadoria | 3 dígitos; tabela `pais` | 1989-1996 |
| `sg_uf` | `SG_UF` | texto | Sigla da UF de origem (exportação) ou destino (importação) do produto, segundo a página | sigla; tabela `uf` | 1989-1996 |
| `kg_liquido` | `KG_LIQUIDO` | texto | Peso líquido | quilograma | 1989-1996 |
| `vl_fob` | `VL_FOB` | texto | Valor FOB da operação | US$ | 1989-1996 |
| `ano` | — (partição) | inteiro | Ano do arquivo bruto (extraído do nome do arquivo); igual a `co_ano` | — | 1989-1996 |

## No lake

- Dataset `comex/imp-nbm`, particionado por `ano` (inteiro); um Parquet por ano.
- Conversão com o DuckDB em latin-1, separador `;`, todas as colunas como texto, nomes em minúsculas. O código `co_nbm` tem 10 dígitos e preserva os zeros à esquerda.
- Nenhuma linha é descartada nas amostras.

## Cuidados de uso

- **NBM não é NCM.** Os códigos de 10 dígitos da NBM não se casam diretamente com os de 8 dígitos da NCM; a tabela `nbm_ncm` (13.628 linhas) faz a conversão, e a fonte a chama de "tabela de conversão".
- **Sem `co_unid`, `qt_estat`, via ou URF.** O layout histórico só tem NBM, país, UF, peso e valor.
- **Medidas em texto.** `kg_liquido` e `vl_fob` são `VARCHAR`; converta antes de somar.
- **Linhas com valor zero.** Há linhas com `vl_fob` 0 (2 em 1989 na exportação; 618 em 1989 e 730 em 1996 na importação).
- **Valor em US$ FOB sem ajuste de inflação.**
- **Moeda original.** A fonte informa valores em dólar para toda a série.

## Exemplos

Valor importado (US$ milhões) por mês em 1996:

```python
import polars as pl

df = pl.scan_parquet("lake/comex/imp-nbm/**/*.parquet", hive_partitioning=True)
mensal = (
    df.filter(pl.col("ano") == 1996)
    .group_by("co_mes")
    .agg((pl.col("vl_fob").cast(pl.Int64).sum() / 1e6).alias("milhoes_usd"))
    .sort("co_mes")
    .collect()
)
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
