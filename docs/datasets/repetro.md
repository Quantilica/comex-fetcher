---
dataset:
  id: repetro
  fonte: comex
  titulo: "REPETRO contabilizado em separado"
  resumo: "Série de exportações fictas e nacionalizações sob o regime REPETRO, destacadas da metodologia principal da balança comercial."
  orgao: "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX)"
  pagina_oficial: "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
  licenca: "Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas"
  periodicidade: "sem periodicidade declarada; republicada junto com a base (sufixos 20261006 e 20261008 no bruto)"
  cobertura: {inicio: 2001-01, fim: em-curso}
  unidade: "exportação (ou importação) REPETRO de uma NCM, num mês, para um país (linha agregada)"
  granularidade: {espacial: "país", temporal: "mês"}
  formato_bruto: "planilha XLSX (`exp_repetro.xlsx`, `imp_repetro.xlsx`), uma aba (`Sheet 1`) com cabeçalho na primeira linha"
  lake: {estado: convertido, particoes: [], chave: [co_ano, co_mes, co_ncm, co_pais], colunas: 7}
  unidades_de_medida:
    vl_fob: "US$ FOB (a fonte não detalha; coluna de mesmo nome dos dados principais)"
    kg_liquido: "quilograma líquido (kg)"
    qt_estat: "quantidade estatística (unidade da NCM)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# REPETRO contabilizado em separado

## Resumo

Segundo o MDIC, é a "série histórica dos dados REPETRO que fizeram parte da compilação estatística e foram destacados da metodologia principal, não compondo mais a balança comercial divulgada pela SECEX". Cobre as exportações fictas e as nacionalizações de origem Brasil sob o regime REPETRO, e "não representa o universo total de operações ao amparo do regime".

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/repetro` |
| Órgão | Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX) |
| Página oficial | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas |
| Periodicidade | sem periodicidade declarada; republicada junto com a base (sufixos 20261006 e 20261008 no bruto) |
| Cobertura | 2001-01 a em-curso |
| Unidade (uma linha) | exportação (ou importação) REPETRO de uma NCM, num mês, para um país (linha agregada) |
| Granularidade | espacial: país; temporal: mês |
| Formato bruto | planilha XLSX (`exp_repetro.xlsx`, `imp_repetro.xlsx`), uma aba (`Sheet 1`) com cabeçalho na primeira linha |
| Estado no lake | convertido |
| Partições | — |
| Chave | `co_ano`, `co_mes`, `co_ncm`, `co_pais` |
| Colunas | 7 |
| Unidades de medida | `vl_fob`: US$ FOB (a fonte não detalha; coluna de mesmo nome dos dados principais); `kg_liquido`: quilograma líquido (kg); `qt_estat`: quantidade estatística (unidade da NCM) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa duas planilhas de `https://balanca.mdic.gov.br/balanca/bd/repetro/` (`exp_repetro.xlsx`, `imp_repetro.xlsx`). No bruto: `exp-repetro@AAAAMMDD.xlsx` e `imp-repetro@AAAAMMDD.xlsx`, com a data de última modificação do servidor.
- Versões no bruto conferidas em 2026-11-09: `exp-repetro@20261006`, `imp-repetro@20261006` e `imp-repetro@20261008`. A importação de 8 de outubro substitui a de 6 no lake (o lake converte só a versão mais recente).

## Conteúdo

- Exportação: 2.139 linhas, anos 2001 a 2026, sem linhas em 2025; 2026 vai até o mês 7. Importação (versão 20261008): 465 linhas, anos 2018 a 2026; 2024 vai até o mês 8 e 2026 até o mês 9. As linhas são únicas por ano, mês, NCM e país (conferido em 2026-11-10).
- A fonte não declara a cobertura nem o layout desta série; o que está aqui vem das planilhas.
- Não tem `co_unid`, via, URF nem UF, ao contrário de `exp` e `imp`.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_ano` | `CO_ANO` | inteiro | Ano de referência (nome do campo; a fonte não descreve) | AAAA | todo |
| `co_mes` | `CO_MES` | inteiro | Mês de referência (nome do campo; a fonte não descreve) | 1 a 12 | todo |
| `co_ncm` | `CO_NCM` | texto | Código da mercadoria na NCM | 8 dígitos; tabela `ncm` | todo |
| `co_pais` | `CO_PAIS` | texto | Código do país (destino na exportação, origem na importação, por analogia com os dados principais; a fonte não descreve) | 3 dígitos; tabela `pais` | todo |
| `vl_fob` | `VL_FOB` | decimal (exportação) / inteiro (importação) | Valor FOB | US$ (por analogia com os dados principais; a fonte não informa) | todo |
| `kg_liquido` | `KG_LIQUIDO` | decimal (exportação) / inteiro (importação) | Peso líquido | quilograma | todo |
| `qt_estat` | `QT_ESTAT` | decimal (exportação) / inteiro (importação) | Quantidade estatística | unidade estatística da NCM (a planilha não traz `co_unid`) | todo |

## No lake

- Dataset `comex/repetro`, sem partição; um Parquet por planilha (`exp-repetro__sheet_1.parquet`, `imp-repetro__sheet_1.parquet`), com a aba normalizada no nome. As duas direções ficam no mesmo dataset, **sem coluna que diga se a linha é exportação ou importação**: só o nome do arquivo.
- As células são lidas como texto e tipadas depois: `co_ncm` e `co_pais` ficam texto; as demais viram inteiro ou decimal quando todos os valores convertem. Por isso `vl_fob`, `kg_liquido` e `qt_estat` são decimais na exportação (214, 101 e 81 linhas têm fração) e inteiros na importação.

## Cuidados de uso

- **Não faz parte de `exp`/`imp`.** A série foi destacada da balança; não some com os datasets principais nem os use para fechar totais.
- **Direção só pelo nome do arquivo.** Ao ler `lake/comex/repetro/*.parquet` junto, as linhas de exportação e importação ficam indistinguíveis; leia cada arquivo e marque a direção.
- **Tipos diferentes por arquivo.** As três medidas são `double` na exportação e `int64` na importação. Converta para um tipo comum antes de unir.
- **Não é o universo do regime.** A própria fonte diz que cobre só as exportações fictas e as nacionalizações de origem Brasil.
- **Lacunas.** A exportação não tem linhas em 2025; a importação tem poucas linhas em 2024-2026 (11, 9 e 3).
- **Moeda e unidade não declaradas.** A fonte não documenta as colunas; moeda e unidade foram deduzidas do nome.

## Exemplos

Valor FOB de exportação REPETRO por ano (US$ milhões):

```python
import polars as pl

exp = pl.read_parquet("lake/comex/repetro/exp-repetro__sheet_1.parquet")
por_ano = (
    exp.group_by("co_ano")
    .agg((pl.col("vl_fob").sum() / 1e6).alias("milhoes_usd"))
    .sort("co_ano")
)
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
