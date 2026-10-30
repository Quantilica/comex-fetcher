# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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

### Histórico anterior

Versões até a 2.0.0 antecedem a adoção deste changelog e estão registradas nas
tags do repositório: 1.5.2 (2025-12-24), 1.4.1 (2024-03-08), 1.4.0 (2022-07-07),
1.3.3 (2021-04-23), 1.0 (2020-05-25), 0.9 (2020-04-30) — as anteriores à 2.0.0
ainda sob o nome `comexdown`.
