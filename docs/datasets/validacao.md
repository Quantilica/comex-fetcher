---
dataset:
  id: validacao
  fonte: comex
  titulo: "Totais para validação dos arquivos anuais"
  resumo: "Totais anuais de linhas, valor e peso de cada arquivo de exportação e importação, para conferir o que foi baixado."
  orgao: "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX)"
  pagina_oficial: "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
  licenca: "Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas"
  periodicidade: "republicada junto com a base (sufixo 20261006 no bruto)"
  cobertura: {inicio: 1997-01, fim: em-curso}
  unidade: "um arquivo anual de dados (nome em `arquivo`) com seus totais"
  granularidade: {espacial: "não se aplica", temporal: "ano"}
  formato_bruto: "CSV `EXP_TOTAIS_CONFERENCIA.csv`, `IMP_TOTAIS_CONFERENCIA.csv`, `EXP_TOTAIS_CONFERENCIA_MUN.csv` e `IMP_TOTAIS_CONFERENCIA_MUN.csv`, separador ponto e vírgula, campos de texto entre aspas"
  lake: {estado: convertido, particoes: [], chave: [arquivo], colunas: 8}
  unidades_de_medida: null
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# Totais para validação dos arquivos anuais

## Resumo

Quatro pequenas tabelas (exportação e importação, por NCM e por município) com uma linha por arquivo anual: número de linhas e soma das medidas. Servem para conferir se o arquivo baixado e convertido está completo. A fonte as chama de "Totais para validação".

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/validacao` |
| Órgão | Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX) |
| Página oficial | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas |
| Periodicidade | republicada junto com a base (sufixo 20261006 no bruto) |
| Cobertura | 1997-01 a em-curso |
| Unidade (uma linha) | um arquivo anual de dados (nome em `arquivo`) com seus totais |
| Granularidade | espacial: não se aplica; temporal: ano |
| Formato bruto | CSV `EXP_TOTAIS_CONFERENCIA.csv`, `IMP_TOTAIS_CONFERENCIA.csv`, `EXP_TOTAIS_CONFERENCIA_MUN.csv` e `IMP_TOTAIS_CONFERENCIA_MUN.csv`, separador ponto e vírgula, campos de texto entre aspas |
| Estado no lake | convertido |
| Partições | — |
| Chave | `arquivo` |
| Colunas | 8 |
| Unidades de medida | — |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa os quatro CSV de `https://balanca.mdic.gov.br/balanca/bd/comexstat-bd/ncm/` e `.../mun/`. No bruto: `exp-validacao@AAAAMMDD.csv`, `imp-validacao`, `exp-mun-validacao` e `imp-mun-validacao`, todos com o sufixo 20261006 (conferido em 2026-11-09).

## Conteúdo

- 30 linhas por arquivo (anos 1997 a 2026, conferido em 2026-11-10). A coluna `arquivo` traz o nome do CSV de dados (`EXP_1997.csv`, `IMP_1997_MUN.csv`).
- O layout varia por tabela: a de exportação por NCM tem `qt_estat`; a de importação por NCM, também `vl_frete` e `vl_seguro`; as municipais só `kg_liquido` e `vl_fob`.
- **Conferência feita:** para os anos convertidos (exportação e importação por NCM: 1997, 2005, 2015, 2025, 2026; por município: 1997, 2010, 2026), `numero_linhas` e as somas de `vl_fob`, `kg_liquido`, `qt_estat`, `vl_frete` e `vl_seguro` são iguais às do lake. Os totais de `vl_fob` e `kg_liquido` de `exp` e `exp-mun` (e de `imp` e `imp-mun`) são iguais nos anos 1997, 2005, 2010, 2015, 2020, 2024 e 2025.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `arquivo` | `ARQUIVO` | texto | Nome do arquivo anual de dados a que a linha se refere | ex.: `EXP_1997.csv`, `IMP_2026_MUN.csv` | todo |
| `co_ano` | `CO_ANO` | texto | Ano do arquivo | AAAA | todo |
| `qt_estat` | `QT_ESTAT` | texto | Soma de `qt_estat` do arquivo; só nas tabelas por NCM | soma de quantidades em unidades diferentes (sem significado físico) | todo |
| `kg_liquido` | `KG_LIQUIDO` | texto | Soma de `kg_liquido` do arquivo | quilograma | todo |
| `vl_fob` | `VL_FOB` | texto | Soma de `vl_fob` do arquivo | US$ | todo |
| `vl_frete` | `VL_FRETE` | texto | Soma de `vl_frete`; só na importação por NCM | não informado pela fonte | todo |
| `vl_seguro` | `VL_SEGURO` | texto | Soma de `vl_seguro`; só na importação por NCM | não informado pela fonte | todo |
| `numero_linhas` | `NUMERO_LINHAS` | texto | Número de linhas de dados do arquivo (sem o cabeçalho) | linhas | todo |

## No lake

- Dataset `comex/validacao`, sem partição; um Parquet por CSV (`exp-validacao.parquet`, `imp-validacao.parquet`, `exp-mun-validacao.parquet`, `imp-mun-validacao.parquet`).
- Conversão com o DuckDB em latin-1, tudo como texto, nomes em minúsculas. As colunas ausentes em uma tabela simplesmente não existem naquele arquivo.
- Os totais ficam em texto; para somar ou comparar, converta com `TRY_CAST(... AS HUGEINT)`.

## Cuidados de uso

- **O arquivo de origem só aparece em `arquivo`.** Não há coluna que diga qual das quatro tabelas é; use o nome em `arquivo` (`EXP_`, `IMP_`, `_MUN`).
- **Compare só o que foi baixado.** Os totais descrevem os arquivos publicados na data do sufixo; um ano baixado antes de uma nova versão (por exemplo o ano corrente) não bate.
- **`qt_estat` somado não tem significado.** A soma mistura unidades; serve apenas para conferir integridade.
- **Medidas em texto.** Converta antes de comparar.

## Exemplos

Conferir o número de linhas de um ano do lake com o total publicado:

```sql
SELECT v.numero_linhas::BIGINT AS publicado, COUNT(*) AS no_lake
FROM read_parquet('lake/comex/validacao/exp-validacao.parquet') v,
     read_parquet('lake/comex/exp/ano=2025/*.parquet') e
WHERE v.co_ano = '2025'
GROUP BY v.numero_linhas;
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
