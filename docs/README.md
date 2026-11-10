# Comércio exterior brasileiro (`comex`)

O `comex-fetcher` coleta as estatísticas de comércio exterior em dados abertos do Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), por meio da Secretaria de Comércio Exterior (SECEX). Os arquivos são a base do sistema Comex Stat e dos dados usados para construir a balança comercial brasileira. O fetcher os converte para o lake em Parquet.

Página da fonte: https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta

| Dataset | O que é | Período | Página |
|---|---|---|---|
| `exp` | Exportações por NCM, país, UF do produto, via e URF | 1997 em diante | [exp](datasets/exp.md) |
| `imp` | Importações por NCM, com frete e seguro | 1997 em diante | [imp](datasets/imp.md) |
| `exp-mun` | Exportações por município da empresa e posição SH4 | 1997 em diante | [exp-mun](datasets/exp-mun.md) |
| `imp-mun` | Importações por município da empresa e posição SH4 | 1997 em diante | [imp-mun](datasets/imp-mun.md) |
| `exp-nbm` | Exportações pela NBM (série histórica) | 1989 a 1996 | [exp-nbm](datasets/exp-nbm.md) |
| `imp-nbm` | Importações pela NBM (série histórica) | 1989 a 1996 | [imp-nbm](datasets/imp-nbm.md) |
| `auxiliary-tables` | Tabelas de códigos e classificações (NCM, SH, CUCI, ISIC, países, UF, municípios, via, URF...) | sem período | [auxiliary-tables](datasets/auxiliary-tables.md) |
| `ncm-vigente` | NCM vigente, com todos os níveis e a vigência | vigente em 2026-11-05 | [ncm-vigente](datasets/ncm-vigente.md) |
| `repetro` | Exportações e importações REPETRO, destacadas da balança | 2001 em diante | [repetro](datasets/repetro.md) |
| `validacao` | Totais de linhas e valores de cada arquivo anual | 1997 em diante | [validacao](datasets/validacao.md) |

## Como o MDIC publica

- Um arquivo CSV por ano e por direção (`EXP_AAAA.csv`, `IMP_AAAA.csv`, e as versões `_MUN` e `_NBM`), com separador ponto e vírgula e cabeçalho. A página afirma que os arquivos reúnem todos os dados usados na construção da balança comercial e que os arquivos são grandes: o uso em planilhas pode perder linhas.
- A página não declara periodicidade. O arquivo do ano corrente cresce com os meses divulgados. Em 2025, o MDIC deixou de oferecer os arquivos únicos com todos os anos (`*_COMPLETA.zip`), com o aviso de que os anos anteriores estão congelados e de que basta baixar o ano mais recente (Informativo SECEX 029/2025).
- As tabelas de códigos saem em CSV e reunidas em uma planilha. A série REPETRO e os totais para validação saem em arquivos próprios. A página também publica um calendário de dias úteis e correlações das classificações antigas, que o fetcher não baixa.
- O fetcher guarda cada versão baixada com a data de última modificação do servidor no nome (`<arquivo>@AAAAMMDD`). O lake converte a versão mais recente de cada arquivo.

## Como os conjuntos se relacionam

- **NCM × município.** `exp` e `exp-mun` (e `imp` e `imp-mun`) trazem o mesmo total de valor FOB e peso líquido por ano (conferido pelos totais de validação de 1997, 2005, 2010, 2015, 2020, 2024 e 2025); os arquivos municipais abrem o total pela empresa e pela posição SH4, sem NCM, via e URF. Use um ou outro, nunca a soma.
- **NBM × NCM.** `exp-nbm` e `imp-nbm` cobrem 1989 a 1996 e `exp` e `imp` começam em 1997. A tabela `nbm_ncm` (em `auxiliary-tables`) converte uma classificação na outra.
- **REPETRO.** `repetro` não compõe a balança divulgada nem os arquivos `exp`/`imp`, segundo a fonte.
- **Códigos.** Os códigos dos dados de comércio são descritos por `auxiliary-tables`; a `ncm-vigente` traz a hierarquia atual da NCM.
- **Validação.** `validacao` permite conferir o número de linhas e os totais de cada arquivo anual.

## Quebras e avisos que valem para todos os conjuntos

| Desde | Mudança | Afeta |
|---|---|---|
| 1997-01 | A classificação passa da NBM para a NCM | `exp`, `imp` e as séries NBM |
| 2025-06 | O MDIC descontinua os arquivos únicos (`*_COMPLETA.zip`) | coleta |

- Todas as medidas e códigos vêm do CSV como texto: as colunas de dados de comércio são `VARCHAR` no lake. Converta antes de somar.
- A página do MDIC e a licença: o rodapé do site declara Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0) para o conteúdo do site, e a página dos dados não traz licença própria. Cite a fonte e não redistribua versões modificadas sem confirmar com o MDIC.
- Os dados são agregados por operação; não há dado pessoal nos arquivos.
