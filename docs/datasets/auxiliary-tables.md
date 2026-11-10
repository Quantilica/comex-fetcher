---
dataset:
  id: auxiliary-tables
  fonte: comex
  titulo: "Tabelas auxiliares de códigos e classificações"
  resumo: "Tabelas de correlação de códigos (NCM, SH, CUCI, ISIC, CGCE, países, UF, municípios, via, URF e outras) que descrevem os códigos dos dados de comércio exterior."
  orgao: "Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX)"
  pagina_oficial: "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta"
  licenca: "Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas"
  periodicidade: "sem periodicidade declarada; as tabelas são republicadas junto com a base (sufixos de 20260806 a 20261006 no bruto)"
  cobertura: {inicio: 1989-01, fim: em-curso}
  unidade: "um código de uma classificação (ou a correlação de uma NCM com as classificações), conforme a tabela"
  granularidade: {espacial: "não se aplica (as tabelas `uf`, `uf_mun`, `pais` descrevem códigos)", temporal: "não se aplica"}
  formato_bruto: "CSV (um por tabela) separado por ponto e vírgula, com campos entre aspas, em latin-1, mais uma planilha `TABELAS_AUXILIARES.xlsx` que reúne as tabelas em abas"
  lake: {estado: convertido, particoes: [], chave: [], colunas: 131}
  unidades_de_medida:
    co_cuci_sub: "código (inteiro nas abas do XLSX)"
    co_cgce_n3: "código (inteiro nas abas do XLSX)"
    co_cgce_n2: "código (inteiro nas abas do XLSX)"
    co_cgce_n1: "código (inteiro nas abas do XLSX)"
    co_cuci_divisao: "código (inteiro nas abas do XLSX)"
    co_cuci_sec: "código (inteiro nas abas do XLSX)"
    co_isic_grupo: "código (inteiro nas abas do XLSX)"
    co_isic_divisao: "código (inteiro nas abas do XLSX)"
    co_siit: "código (inteiro nas abas do XLSX)"
    co_pais_ison3: "código ISO numérico (inteiro nas abas do XLSX)"
    co_bloco: "código (inteiro nas abas do XLSX)"
    co_mun_geo: "código de município (inteiro nas abas do XLSX)"
    numero_da_aba: "ordinal da aba"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-10
  versao_fetcher: 2.5.2
---

# Tabelas auxiliares de códigos e classificações

## Resumo

Um conjunto de tabelas de referência que o MDIC publica ao lado dos dados de comércio exterior para traduzir os códigos: produto (NCM, SH, CUCI, ISIC, CGCE, SIIT, fator agregado, PPE, PPI, grupo), país e bloco, UF e município, via de transporte, URF e unidade estatística, além da NBM e da conversão NBM para NCM. Todas as tabelas estão também reunidas em uma planilha, `TABELAS_AUXILIARES.xlsx`. O dataset do lake guarda cada tabela como um arquivo Parquet, sem partição.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `comex/auxiliary-tables` |
| Órgão | Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC), Secretaria de Comércio Exterior (SECEX) |
| Página oficial | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta |
| Licença | Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada (CC BY-ND 3.0), declarada no rodapé do site do MDIC para todo o conteúdo do site: https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR . A página dos dados não traz licença própria; a licença impede obras derivadas |
| Periodicidade | sem periodicidade declarada; as tabelas são republicadas junto com a base (sufixos de 20260806 a 20261006 no bruto) |
| Cobertura | 1989-01 a em-curso |
| Unidade (uma linha) | um código de uma classificação (ou a correlação de uma NCM com as classificações), conforme a tabela |
| Granularidade | espacial: não se aplica (as tabelas `uf`, `uf_mun`, `pais` descrevem códigos); temporal: não se aplica |
| Formato bruto | CSV (um por tabela) separado por ponto e vírgula, com campos entre aspas, em latin-1, mais uma planilha `TABELAS_AUXILIARES.xlsx` que reúne as tabelas em abas |
| Estado no lake | convertido |
| Partições | — |
| Chave | — |
| Colunas | 131 |
| Unidades de medida | `co_cuci_sub`: código (inteiro nas abas do XLSX); `co_cgce_n3`: código (inteiro nas abas do XLSX); `co_cgce_n2`: código (inteiro nas abas do XLSX); `co_cgce_n1`: código (inteiro nas abas do XLSX); `co_cuci_divisao`: código (inteiro nas abas do XLSX); `co_cuci_sec`: código (inteiro nas abas do XLSX); `co_isic_grupo`: código (inteiro nas abas do XLSX); `co_isic_divisao`: código (inteiro nas abas do XLSX); `co_siit`: código (inteiro nas abas do XLSX); `co_pais_ison3`: código ISO numérico (inteiro nas abas do XLSX); `co_bloco`: código (inteiro nas abas do XLSX); `co_mun_geo`: código de município (inteiro nas abas do XLSX); `numero_da_aba`: ordinal da aba |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-10 |
| Versão do fetcher | 2.5.2 |

## Origem e coleta

- O fetcher baixa cada tabela em CSV de `https://balanca.mdic.gov.br/balanca/bd/tabelas/` e a planilha `TABELAS_AUXILIARES.xlsx`. No bruto, o nome recebe o sufixo de data de última modificação: `pais@20261006.csv`, `urf@20260806.csv`, `nbm@20190903.csv`, `tabelas-auxiliares@20261006.xlsx`.
- Versões no bruto conferidas em 2026-11-09: 20 CSV mais a planilha. As tabelas `nbm` e `nbm_ncm` têm sufixo 20190903; `urf` e `via`, 20260806; as demais, 20261006.
- O fetcher confere a primeira linha útil dos CSV (descarta o `206` com código PHP que a fonte devolve para arquivo inexistente). Não baixa o calendário nem as correlações das classificações antigas.

## Conteúdo

- Cada arquivo é uma tabela independente. No lake o dataset junta **37 arquivos**: os 20 CSV e as 17 abas da planilha (16 abas de dados e a aba `indice`, que descreve as demais). Contagens de linhas (amostra completa do bruto de 2026-11-09):

| Tabela | O que é | Linhas |
|---|---|---|
| `sh` | Sistema Harmonizado (seções. capítulos SH2. posições SH4 e subposições SH6) | 6.620 |
| `cuci` | CUCI. revisão 4 (item. subgrupo. grupo. divisão. seção) | 2.971 |
| `cgce` | CGCE. grandes categorias econômicas (3 níveis) | 19 |
| `isic` | ISIC. revisão 4 (classe. grupo. divisão. seção) | 420 |
| `siit` | Setores industriais por intensidade tecnológica | 5 |
| `unidade` | Unidades estatísticas da NCM | 15 |
| `fat_agreg` | Fator agregado da NCM. classificação própria da SECEX | 6 |
| `ppi` | Pauta de Produtos Importados. classificação própria da SECEX; a fonte avisa: usar apenas para importação | 475 |
| `ppe` | Pauta de Produtos Exportados. classificação própria da SECEX; a fonte avisa: usar apenas para exportação | 415 |
| `pais` | Países | 281 |
| `pais_bloco` | Blocos de países (usar em conjunto com `pais`) | 324 |
| `uf` | Unidades da federação | 34 |
| `uf_mun` | Municípios (fundamental para os arquivos por município da empresa) | 5.570 |
| `via` | Via (modal) de transporte | 17 |
| `urf` | Unidade da Receita Federal (embarque/despacho) | 281 |
| `isic_cuci` | ISIC seção × CUCI grupo. usada na apresentação coletiva da balança | 13.746 |
| `ncm` | NCM e a correlação com as demais classificações | 13.753 |
| `grupo` | Grupo de produtos. classificação própria da SECEX | 169 |
| `nbm` | NBM. 1989 a 1996 | 13.628 |
| `nbm_ncm` | Conversão NBM para NCM | 13.628 |

- Na planilha, as abas 1 a 9 e 16 são **correlações por NCM**: cada linha é uma NCM com as colunas da classificação (por exemplo `co_ncm`, `no_ncm_por`, `co_cuci_item`, ...), e não a lista da classificação. A aba `indice` lista as 16 abas, o CSV de origem (`arquivo_referencia`) e a chave de cruzamento.
- Descrições oficiais (aba `indice`): a PPI "deve ser utilizada apenas para importação" e a PPE "apenas para exportação"; a tabela de municípios é indicada como fundamental para uso junto com os arquivos por município da empresa; o CUCI é a revisão 4; a ISIC, a revisão 4.
- As tabelas não têm período próprio. O conteúdo é o da data do sufixo do arquivo.
- Códigos especiais de UF (tabela `uf`, conferido): `EX` Exterior, `CB` Consumo de Bordo, `MN` Mercadoria Nacionalizada, `RE` Reexportação, `ED` Estados Diversos - Café, `ND` Não Declarada, `ZN` Zona Não Declarada.
- Vias de transporte (tabela `via`, conferido): 17 códigos, de `00` (via não declarada) a `15`, mais `99` (via desconhecida).
- Unidades estatísticas (tabela `unidade`, conferido): 15 códigos, `10` quilograma líquido, `11` número (unidade), `12` milheiro, `13` pares, `14` metro, `15` metro quadrado, `16` metro cúbico, `17` litro, `18` mil quilowatt-hora, `19` quilate, `20` dúzia, `21` tonelada métrica líquida, `22` grama líquido, `23` bilhões de unidades internacionais, `24` quilograma bruto.

## Variáveis

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_cgce_n3` | `CO_CGCE_N3` | texto (inteiro nas abas do XLSX) | Código de CGCE, nível 3 | em `cgce`, `ncm`, `xlsx:cgce` | todo |
| `no_cgce_n3` | `NO_CGCE_N3` | texto | Nome de CGCE, nível 3 | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n3_ing` | `NO_CGCE_N3_ING` | texto | Nome de CGCE, nível 3 em inglês | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n3_esp` | `NO_CGCE_N3_ESP` | texto | Nome de CGCE, nível 3 em espanhol | em `cgce`, `xlsx:cgce` | todo |
| `co_cgce_n2` | `CO_CGCE_N2` | texto (inteiro nas abas do XLSX) | Código de CGCE, nível 2 | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n2` | `NO_CGCE_N2` | texto | Nome de CGCE, nível 2 | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n2_ing` | `NO_CGCE_N2_ING` | texto | Nome de CGCE, nível 2 em inglês | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n2_esp` | `NO_CGCE_N2_ESP` | texto | Nome de CGCE, nível 2 em espanhol | em `cgce`, `xlsx:cgce` | todo |
| `co_cgce_n1` | `CO_CGCE_N1` | texto (inteiro nas abas do XLSX) | Código de CGCE, nível 1 | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n1` | `NO_CGCE_N1` | texto | Nome de CGCE, nível 1 | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n1_ing` | `NO_CGCE_N1_ING` | texto | Nome de CGCE, nível 1 em inglês | em `cgce`, `xlsx:cgce` | todo |
| `no_cgce_n1_esp` | `NO_CGCE_N1_ESP` | texto | Nome de CGCE, nível 1 em espanhol | em `cgce`, `xlsx:cgce` | todo |
| `co_cuci_item` | `CO_CUCI_ITEM` | texto | Código de CUCI, item | em `cuci`, `ncm`, `xlsx:cuci` | todo |
| `no_cuci_item` | `NO_CUCI_ITEM` | texto | Nome de CUCI, item | em `cuci`, `xlsx:cuci` | todo |
| `co_cuci_sub` | `CO_CUCI_SUB` | texto (inteiro nas abas do XLSX) | Código de CUCI, subgrupo (`sub`) | em `cuci`, `xlsx:cuci` | todo |
| `no_cuci_sub` | `NO_CUCI_SUB` | texto | Nome de CUCI, subgrupo (`sub`) | em `cuci`, `xlsx:cuci` | todo |
| `co_cuci_grupo` | `CO_CUCI_GRUPO` | texto | Código de CUCI, grupo | em `cuci`, `isic_cuci`, `xlsx:isic_cuci`, `xlsx:cuci` | todo |
| `no_cuci_grupo` | `NO_CUCI_GRUPO` | texto | Nome de CUCI, grupo | em `cuci`, `isic_cuci`, `xlsx:isic_cuci`, `xlsx:cuci` | todo |
| `co_cuci_divisao` | `CO_CUCI_DIVISAO` | texto (inteiro nas abas do XLSX) | Código de CUCI, divisão | em `cuci`, `xlsx:cuci` | todo |
| `no_cuci_divisao` | `NO_CUCI_DIVISAO` | texto | Nome de CUCI, divisão | em `cuci`, `xlsx:cuci` | todo |
| `co_cuci_sec` | `CO_CUCI_SEC` | texto (inteiro nas abas do XLSX) | Código de CUCI, seção | em `cuci`, `xlsx:cuci` | todo |
| `no_cuci_sec` | `NO_CUCI_SEC` | texto | Nome de CUCI, seção | em `cuci`, `xlsx:cuci` | todo |
| `co_fat_agreg` | `CO_FAT_AGREG` | texto | Código de fator agregado | em `fat_agreg`, `ncm`, `xlsx:fat_agreg` | todo |
| `no_fat_agreg` | `NO_FAT_AGREG` | texto | Nome de fator agregado | em `fat_agreg`, `xlsx:fat_agreg` | todo |
| `no_fat_agreg_gp` | `NO_FAT_AGREG_GP` | texto | Nome do grupo do fator agregado (por exemplo `PRODUTOS INDUSTRIALIZADOS` reúne `02` e `03`) | em `fat_agreg`, `xlsx:fat_agreg` | todo |
| `co_exp_subset` | `CO_EXP_SUBSET` | texto | Código de grupo de produtos SECEX, subconjunto (`subset`) | em `grupo`, `ncm` | todo |
| `no_exp_subset_por` | `NO_EXP_SUBSET_POR` | texto | Nome de grupo de produtos SECEX, subconjunto (`subset`) em português | em `grupo` | todo |
| `no_exp_subset_esp` | `NO_EXP_SUBSET_ESP` | texto | Nome de grupo de produtos SECEX, subconjunto (`subset`) em espanhol | em `grupo` | todo |
| `no_exp_subset_ing` | `NO_EXP_SUBSET_ING` | texto | Nome de grupo de produtos SECEX, subconjunto (`subset`) em inglês | em `grupo` | todo |
| `co_exp_set` | `CO_EXP_SET` | texto | Código de grupo de produtos SECEX, conjunto (`set`) | em `grupo` | todo |
| `no_exp_set` | `NO_EXP_SET` | texto | Nome de grupo de produtos SECEX, conjunto (`set`) | em `grupo` | todo |
| `no_exp_set_esp` | `NO_EXP_SET_ESP` | texto | Nome de grupo de produtos SECEX, conjunto (`set`) em espanhol | em `grupo` | todo |
| `no_exp_set_ing` | `NO_EXP_SET_ING` | texto | Nome de grupo de produtos SECEX, conjunto (`set`) em inglês | em `grupo` | todo |
| `co_isic_classe` | `CO_ISIC_CLASSE` | texto | Código de ISIC, classe | em `isic`, `ncm`, `xlsx:isic` | todo |
| `no_isic_classe` | `NO_ISIC_CLASSE` | texto | Nome de ISIC, classe | em `isic`, `xlsx:isic` | todo |
| `no_isic_classe_ing` | `NO_ISIC_CLASSE_ING` | texto | Nome de ISIC, classe em inglês | em `isic`, `xlsx:isic` | todo |
| `no_isic_classe_esp` | `NO_ISIC_CLASSE_ESP` | texto | Nome de ISIC, classe em espanhol | em `isic`, `xlsx:isic` | todo |
| `co_isic_grupo` | `CO_ISIC_GRUPO` | texto (inteiro nas abas do XLSX) | Código de ISIC, grupo | em `isic`, `xlsx:isic` | todo |
| `no_isic_grupo` | `NO_ISIC_GRUPO` | texto | Nome de ISIC, grupo | em `isic`, `xlsx:isic` | todo |
| `no_isic_grupo_ing` | `NO_ISIC_GRUPO_ING` | texto | Nome de ISIC, grupo em inglês | em `isic`, `xlsx:isic` | todo |
| `no_isic_grupo_esp` | `NO_ISIC_GRUPO_ESP` | texto | Nome de ISIC, grupo em espanhol | em `isic`, `xlsx:isic` | todo |
| `co_isic_divisao` | `CO_ISIC_DIVISAO` | texto (inteiro nas abas do XLSX) | Código de ISIC, divisão | em `isic`, `xlsx:isic` | todo |
| `no_isic_divisao` | `NO_ISIC_DIVISAO` | texto | Nome de ISIC, divisão | em `isic`, `xlsx:isic` | todo |
| `no_isic_divisao_ing` | `NO_ISIC_DIVISAO_ING` | texto | Nome de ISIC, divisão em inglês | em `isic`, `xlsx:isic` | todo |
| `no_isic_divisao_esp` | `NO_ISIC_DIVISAO_ESP` | texto | Nome de ISIC, divisão em espanhol | em `isic`, `xlsx:isic` | todo |
| `co_isic_secao` | `CO_ISIC_SECAO` | texto | Código de ISIC, seção | em `isic`, `isic_cuci`, `xlsx:isic_cuci`, `xlsx:isic` | todo |
| `no_isic_secao` | `NO_ISIC_SECAO` | texto | Nome de ISIC, seção | em `isic`, `isic_cuci`, `xlsx:isic_cuci`, `xlsx:isic` | todo |
| `no_isic_secao_ing` | `NO_ISIC_SECAO_ING` | texto | Nome de ISIC, seção em inglês | em `isic`, `xlsx:isic` | todo |
| `no_isic_secao_esp` | `NO_ISIC_SECAO_ESP` | texto | Nome de ISIC, seção em espanhol | em `isic`, `xlsx:isic` | todo |
| `co_nbm` | `CO_NBM` | texto | Código de NBM | em `nbm`, `nbm_ncm` | todo |
| `no_nbm` | `NO_NBM` | texto | Nome de NBM | em `nbm` | todo |
| `co_ncm` | `CO_NCM` | texto | Código de NCM | em `nbm_ncm`, `ncm`, `xlsx:sh`, `xlsx:isic_cuci`, `xlsx:cuci`, `xlsx:cgce` e mais 6 | todo |
| `co_unid` | `CO_UNID` | texto | Código de unidade estatística da NCM | em `ncm`, `xlsx:unidade`, `unidade` | todo |
| `co_sh6` | `CO_SH6` | texto | Código de Sistema Harmonizado, subposição (SH6) | em `ncm`, `sh`, `xlsx:sh` | todo |
| `co_ppe` | `CO_PPE` | texto | Código de Pauta de Produtos Exportados (PPE) | em `ncm`, `ppe`, `xlsx:ppe` | todo |
| `co_ppi` | `CO_PPI` | texto | Código de Pauta de Produtos Importados (PPI) | em `ncm`, `ppi`, `xlsx:ppi` | todo |
| `co_siit` | `CO_SIIT` | texto (inteiro nas abas do XLSX) | Código de SIIT (setores industriais por intensidade tecnológica) | em `ncm`, `siit`, `xlsx:siit` | todo |
| `no_ncm_por` | `NO_NCM_POR` | texto | Nome de NCM em português | em `ncm`, `xlsx:sh`, `xlsx:isic_cuci`, `xlsx:cuci`, `xlsx:cgce`, `xlsx:isic` e mais 5 | todo |
| `no_ncm_esp` | `NO_NCM_ESP` | texto | Nome de NCM em espanhol | em `ncm` | todo |
| `no_ncm_ing` | `NO_NCM_ING` | texto | Nome de NCM em inglês | em `ncm` | todo |
| `co_pais` | `CO_PAIS` | texto | Código de país | em `pais`, `pais_bloco`, `xlsx:pais`, `xlsx:pais_bloco` | todo |
| `co_pais_ison3` | `CO_PAIS_ISON3` | texto (inteiro nas abas do XLSX) | Código numérico de país (ISO 3166-1 numérico, pelos valores: `004` Afeganistão) | 3 dígitos; em `pais`, `xlsx:pais` | todo |
| `co_pais_isoa3` | `CO_PAIS_ISOA3` | texto | Código alfabético de 3 letras do país (ISO 3166-1 alfa-3, pelos valores: `AFG` Afeganistão) | 3 letras; em `pais`, `xlsx:pais` | todo |
| `no_pais` | `NO_PAIS` | texto | Nome de país | em `pais`, `xlsx:pais` | todo |
| `no_pais_ing` | `NO_PAIS_ING` | texto | Nome de país em inglês | em `pais`, `xlsx:pais` | todo |
| `no_pais_esp` | `NO_PAIS_ESP` | texto | Nome de país em espanhol | em `pais`, `xlsx:pais` | todo |
| `co_bloco` | `CO_BLOCO` | texto (inteiro nas abas do XLSX) | Código de bloco de países | em `pais_bloco`, `xlsx:pais_bloco` | todo |
| `no_bloco` | `NO_BLOCO` | texto | Nome de bloco de países | em `pais_bloco`, `xlsx:pais_bloco` | todo |
| `no_bloco_ing` | `NO_BLOCO_ING` | texto | Nome de bloco de países em inglês | em `pais_bloco`, `xlsx:pais_bloco` | todo |
| `no_bloco_esp` | `NO_BLOCO_ESP` | texto | Nome de bloco de países em espanhol | em `pais_bloco`, `xlsx:pais_bloco` | todo |
| `no_ppe` | `NO_PPE` | texto | Nome de Pauta de Produtos Exportados (PPE) | em `ppe`, `xlsx:ppe` | todo |
| `no_ppe_min` | `NO_PPE_MIN` | texto | Nome em minúsculas e com acentos (`min`) de Pauta de Produtos Exportados (PPE) | em `ppe`, `xlsx:ppe` | todo |
| `no_ppe_ing` | `NO_PPE_ING` | texto | Nome de Pauta de Produtos Exportados (PPE) em inglês | em `ppe`, `xlsx:ppe` | todo |
| `no_ppi` | `NO_PPI` | texto | Nome de Pauta de Produtos Importados (PPI) | em `ppi`, `xlsx:ppi` | todo |
| `no_ppi_min` | `NO_PPI_MIN` | texto | Nome em minúsculas e com acentos (`min`) de Pauta de Produtos Importados (PPI) | em `ppi`, `xlsx:ppi` | todo |
| `no_ppi_ing` | `NO_PPI_ING` | texto | Nome de Pauta de Produtos Importados (PPI) em inglês | em `ppi`, `xlsx:ppi` | todo |
| `no_sh6_por` | `NO_SH6_POR` | texto | Nome de Sistema Harmonizado, subposição (SH6) em português | em `sh`, `xlsx:sh` | todo |
| `no_sh6_esp` | `NO_SH6_ESP` | texto | Nome de Sistema Harmonizado, subposição (SH6) em espanhol | em `sh`, `xlsx:sh` | todo |
| `no_sh6_ing` | `NO_SH6_ING` | texto | Nome de Sistema Harmonizado, subposição (SH6) em inglês | em `sh`, `xlsx:sh` | todo |
| `co_sh4` | `CO_SH4` | texto | Código de Sistema Harmonizado, posição (SH4) | em `sh`, `xlsx:sh` | todo |
| `no_sh4_por` | `NO_SH4_POR` | texto | Nome de Sistema Harmonizado, posição (SH4) em português | em `sh`, `xlsx:sh` | todo |
| `no_sh4_esp` | `NO_SH4_ESP` | texto | Nome de Sistema Harmonizado, posição (SH4) em espanhol | em `sh`, `xlsx:sh` | todo |
| `no_sh4_ing` | `NO_SH4_ING` | texto | Nome de Sistema Harmonizado, posição (SH4) em inglês | em `sh`, `xlsx:sh` | todo |
| `co_sh2` | `CO_SH2` | texto | Código de Sistema Harmonizado, capítulo (SH2) | em `sh`, `xlsx:sh` | todo |
| `no_sh2_por` | `NO_SH2_POR` | texto | Nome de Sistema Harmonizado, capítulo (SH2) em português | em `sh`, `xlsx:sh` | todo |
| `no_sh2_esp` | `NO_SH2_ESP` | texto | Nome de Sistema Harmonizado, capítulo (SH2) em espanhol | em `sh`, `xlsx:sh` | todo |
| `no_sh2_ing` | `NO_SH2_ING` | texto | Nome de Sistema Harmonizado, capítulo (SH2) em inglês | em `sh`, `xlsx:sh` | todo |
| `co_ncm_secrom` | `CO_NCM_SECROM` | texto | Código de Sistema Harmonizado, seção (numeração romana) | em `sh`, `xlsx:sh` | todo |
| `no_sec_por` | `NO_SEC_POR` | texto | Nome de Sistema Harmonizado, seção em português | em `sh`, `xlsx:sh` | todo |
| `no_sec_esp` | `NO_SEC_ESP` | texto | Nome de Sistema Harmonizado, seção em espanhol | em `sh`, `xlsx:sh` | todo |
| `no_sec_ing` | `NO_SEC_ING` | texto | Nome de Sistema Harmonizado, seção em inglês | em `sh`, `xlsx:sh` | todo |
| `column16` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column17` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column18` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column19` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column20` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column21` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column22` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column23` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column24` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column25` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column26` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column27` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column28` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column29` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column30` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column31` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column32` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column33` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column34` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column35` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `column36` | — (artefato) | texto | Coluna espúria de `sh`: o conversor divide em `;` os textos que contêm ponto e vírgula (por exemplo o de `no_sec_ing`, `Lives animals; Animal products`); o resto cai nestas colunas. Não é variável da fonte | só em `sh` | todo |
| `no_siit` | `NO_SIIT` | texto | Nome de SIIT (setores industriais por intensidade tecnológica) | em `siit`, `xlsx:siit` | todo |
| `co_uf` | `CO_UF` | texto | Código de unidade da federação | em `xlsx:uf`, `uf` | todo |
| `sg_uf` | `SG_UF` | texto | Sigla da unidade da federação ou código especial (`EX`, `CB`, `MN`, `RE`, `ED`, `ND`, `ZN`) | tabela `uf`; em `xlsx:uf`, `xlsx:uf_mun`, `uf`, `uf_mun` | todo |
| `no_uf` | `NO_UF` | texto | Nome de unidade da federação | em `xlsx:uf`, `uf` | todo |
| `no_regiao` | `NO_REGIAO` | texto | Nome da região do Brasil | ex.: `REGIAO NORTE`; em `xlsx:uf`, `uf` | todo |
| `co_mun_geo` | `CO_MUN_GEO` | texto (inteiro nas abas do XLSX) | Código do município (7 dígitos, o mesmo de `co_mun` dos datasets `*-mun`) | 7 dígitos; em `xlsx:uf_mun`, `uf_mun` | todo |
| `no_mun` | `NO_MUN` | texto | Nome de município | em `xlsx:uf_mun`, `uf_mun` | todo |
| `no_mun_min` | `NO_MUN_MIN` | texto | Nome em minúsculas e com acentos (`min`) de município | em `xlsx:uf_mun`, `uf_mun` | todo |
| `co_via` | `CO_VIA` | texto | Código de via de transporte | em `xlsx:via`, `via` | todo |
| `no_via` | `NO_VIA` | texto | Nome de via de transporte | em `xlsx:via`, `via` | todo |
| `co_urf` | `CO_URF` | texto | Código de URF (Unidade da Receita Federal) | em `xlsx:urf`, `urf` | todo |
| `no_urf` | `NO_URF` | texto | Nome de URF (Unidade da Receita Federal) | em `xlsx:urf`, `urf` | todo |
| `no_unid` | `NO_UNID` | texto | Nome de unidade estatística da NCM | em `xlsx:unidade`, `unidade` | todo |
| `sg_unid` | `SG_UNID` | texto | Sigla da unidade estatística (com espaços à direita, como na fonte) | ex.: `KGL`, `UNID.`; em `xlsx:unidade`, `unidade` | todo |
| `numero_da_aba` | — | inteiro | Número da aba do XLSX descrita nesta linha | aba índice do XLSX; em `xlsx:indice` | todo |
| `nome` | `NOME` | texto | Nome de e | em `xlsx:indice` | todo |
| `descricao` | — | texto | Descrição da tabela dada pela fonte | aba índice do XLSX; em `xlsx:indice` | todo |
| `arquivo_referencia` | — | texto | Nome do CSV correspondente na fonte | aba índice do XLSX; em `xlsx:indice` | todo |
| `chave_de_cruzamento` | — | texto | Coluna(s) que ligam a tabela aos dados | aba índice do XLSX; em `xlsx:indice` | todo |

## No lake

- Dataset `comex/auxiliary-tables`, **sem partição**. Cada tabela vira um Parquet: `<tabela>.parquet` para os CSV e `tabelas-auxiliares__<n>.parquet` para as abas do XLSX (`__1` a `__16` e `__indice`). Não há coluna que diga de qual tabela a linha veio: só o nome do arquivo.
- Os CSV são lidos pelo DuckDB em latin-1, separador `;`, tudo como texto, com nomes em minúsculas. As abas do XLSX são lidas pelo Polars como texto e depois tipadas: coluna de código conhecida (`co_ncm`, `co_pais`, `co_uf`, `co_urf`, `co_via` etc.) continua texto; as demais viram inteiro ou decimal quando **todo** valor converte. Por isso a mesma coluna é texto nos CSV e inteiro em algumas abas (`co_cgce_n3`, `co_cuci_sub`, `co_siit`, `co_pais_ison3`, `co_bloco`, `co_mun_geo` e outras): a coluna do esquema de referência tem mais de um tipo.
- Os espaços à direita não são removidos (`sg_unid` tem `KGL  `).
- A tabela `sh` sai **com defeito** (ver Cuidados de uso).

## Cuidados de uso

- **`sh` (CSV) está mal lido no lake.** O DuckDB não reconhece as aspas do `sh@20261006.csv` e (1) mantém as aspas literais nos valores (`"010110"`, `"Animais vivos..."`) em 105.906 células, e (2) divide em `;` o texto `Lives animals; Animal products`, de modo que 4.918 das 6.620 linhas ganham valor nas colunas espúrias `column16` a `column36` (conferido em 2026-11-10). Para o Sistema Harmonizado use a aba `tabelas-auxiliares__1` (a NCM com o SH) ou refaça a leitura do CSV com aspas. Nenhuma outra tabela tem o problema; as aspas que aparecem em `nbm`, `ncm` e `ncm-vigente` fazem parte do texto da fonte.
- **Tipos diferentes para a mesma coluna.** O código `co_pais_ison3` é texto (`004`) nos CSV e inteiro (`4`) na aba `tabelas-auxiliares__10`; idem `co_cgce_*`, `co_cuci_sub`, `co_siit`, `co_bloco` e `co_mun_geo`. Para cruzar com os dados de comércio use o CSV (texto com zeros à esquerda) ou converta com `LPAD`.
- **Códigos de comércio são texto.** `co_ncm` (8 dígitos), `co_pais` (3), `co_urf` (7), `co_via` (2) e `sh4` (4) mantêm os zeros à esquerda nos CSV e no dataset `ncm-vigente`.
- **Duas tabelas de NCM.** `ncm` (CSV, 13.753 NCM com as classificações) e a aba `tabelas-auxiliares__1` (13.741 linhas) diferem, e `ncm-vigente` (outro dataset) tem 10.516 NCM de 8 dígitos vigentes em 2026-11-05. NCM antigas dos dados de 1997 em diante existem em `ncm` (todas as NCM das amostras de exportação e importação foram encontradas), mas não necessariamente em `ncm-vigente`.
- **PPI só para importação e PPE só para exportação**, segundo a fonte.
- **CUCI com item `I`.** A primeira linha de `cuci` tem `co_cuci_item` `I` ("Ouro, monetário"), um código que não é numérico; cuidado ao converter para inteiro.
- **Nomes de URF.** `no_urf` repete o código (`0510353 - IRF ILHEUS`).
- **Sem versão.** Cada arquivo guarda só a versão mais recente; o lake não registra quando um código passou a existir.

## Exemplos

Nome e região das UF mais exportadoras, juntando o dataset `exp` com a tabela `uf`:

```sql
SELECT u.no_regiao, u.no_uf, SUM(TRY_CAST(e.vl_fob AS BIGINT)) / 1e9 AS bi_usd
FROM read_parquet('lake/comex/exp/*/*.parquet', hive_partitioning = true) e
JOIN read_parquet('lake/comex/auxiliary-tables/uf.parquet') u ON u.sg_uf = e.sg_uf_ncm
WHERE e.ano = 2025
GROUP BY ALL ORDER BY bi_usd DESC LIMIT 5;
```

Descrição dos países de destino, sem usar a aba de inteiros:

```python
import polars as pl

pais = pl.read_parquet("lake/comex/auxiliary-tables/pais.parquet")
exp = pl.scan_parquet("lake/comex/exp/**/*.parquet", hive_partitioning=True)
top = (
    exp.filter(pl.col("ano") == 2025)
    .group_by("co_pais")
    .agg(pl.col("vl_fob").cast(pl.Int64).sum().alias("usd"))
    .collect()
    .join(pais.select("co_pais", "no_pais"), on="co_pais", how="left")
    .sort("usd", descending=True)
    .head(5)
)
```

## Referências

- Estatísticas de Comércio Exterior em Dados Abertos (MDIC): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
- Aviso sobre o arquivo único (Informativo SECEX 029/2025): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/informativos/informativo-2025-029
- Comex Stat: https://comexstat.mdic.gov.br/
- Tabelas de Correlações de Códigos e Classificações (seção 5 da página dos dados): https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
