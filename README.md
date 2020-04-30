# comexdown: Balança Comercial - Brasil

Este pacote Python contém funções para baixar e manipular os dados da Balança Comercial brasileira divulgados pelo [Ministério da Economia(ME)/Secretaria de Comércio Exterior (SCE)](http://www.mdic.gov.br/index.php/comercio-exterior/estatisticas-de-comercio-exterior/base-de-dados-do-comercio-exterior-brasileiro-arquivos-para-download).

## Instalação

```sh
git clone https://github.com/dkkomesu/comexdown.git
cd comexdown
pip setup.py install
```

## Uso

```python
import comexdown

# Baixa a tabela NCM principal no diretório ./DATA
comexdown.ncm(table="ncm", path="./DATA")

# Baixa o arquivo de exportações de 2019 no diretório ./DATA
comexdown.exp(year=2019, path="./DATA")
```

## Ferramenta de linha de comando

Baixar dados das transações de comércio exterior do Brasil (Exportações/Importações).

É possível especificar um intervalo de anos para baixar de uma vez.

```
comexdown download trade 2008:2019 -o "./DATA"
```

Baixar tabelas de códigos.

```shell
comexdown download code all  # Baixa todos os arquivos de código relacionados
comexdown download code uf   # Baixa apenas o arquivo UF.csv
comexdown download code via  # Baixa apenas o arquivo VIA.csv

comexdown download ncm all   # Baixa todos os arquivos de código NCM*.csv
comexdown download ncm cgce  # Baixa apenas o arquivo NCM_CGCE.csv

comexdown download nbm all   # Baixa todos os arquivos de código NBM*.csv
comexdown download nbm ncm   # Baixa apenas o arquivo NBM_NCM.csv
```

## Estrutura de diretórios dos dados

O pacote salva os arquivos na seguinte estrutura de diretórios por padrão:

```
.
├───code
│       ISIC_CUCI.csv
│       PAIS.csv
│       PAIS_BLOCO.csv
│       UF.csv
│       UF_MUN.csv
│       URF.csv
│       VIA.csv
│
├───exp
│       EXP_1997.csv
│       EXP_1998.csv
│       ...
│       EXP_2020.csv
│
├───exp_nbm
│       EXP_1989_NBM.csv
│       EXP_1990_NBM.csv
|       ...
|       EXP_1996_NBM.csv
│
├───imp
│       IMP_1997.csv
│       IMP_1998.csv
│       ...
│       IMP_2020.csv
│
├───imp_nbm
│       IMP_1989_NBM.csv
│       IMP_1990_NBM.csv
|       ...
|       IMP_1996_NBM.csv
│
├───nbm
│       NBM.csv
│       NBM_NCM.csv
│
└───ncm
        NCM.csv
        NCM_CGCE.csv
        NCM_FAT_AGREG.csv
        NCM_PPE.csv
        NCM_PPI.csv
        NCM_SH.csv
        NCM_UNIDADE.csv
```
