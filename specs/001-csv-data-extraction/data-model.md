# Data Model: Extração de Dados CSV

## Entities

### Arquivo CSV

Fonte de dados bruta. NUNCA deve ser alterado — transformações sempre
produzem novas tabelas/arquivos (constituição do projeto).

| Attribute | Type | Description |
|-----------|------|-------------|
| path | `str` | Caminho absoluto ou relativo no sistema de arquivos |
| size_bytes | `int` | Tamanho do arquivo em bytes (máx: 104.857.600 = 100MB) |
| encoding | `str` | Encoding do arquivo (padrão: UTF-8) |
| delimiter | `str` | Caractere delimitador (padrão: `,`) |
| has_header | `bool` | Se a primeira linha contém cabeçalho (padrão: True) |

**Constraints**:
- Tamanho máximo: 100MB (rejeitar com erro se exceder)
- Encoding suportados: UTF-8 (padrão), Latin-1
- Delimitadores suportados: `,` (padrão), `;`, `\t`

### Configuração de Extração

Parâmetros que controlam como o CSV é lido.

| Attribute | Type | Required | Default |
|-----------|------|----------|---------|
| file_path | `str` | Sim | — |
| delimiter | `str` | Não | `,` |
| encoding | `str` | Não | `utf-8` |
| dtypes | `dict[str, type]` | Não | `None` (inferência automática) |

### Tabela de Dados (DataFrame)

Estrutura de saída com dados tipados.

| Attribute | Type | Description |
|-----------|------|-------------|
| columns | `list[str]` | Nomes das colunas extraídos do cabeçalho |
| dtypes | `dict[str, type]` | Tipos inferidos ou explicitados |
| row_count | `int` | Número de linhas carregadas |
| data | tabular | Dados propriamente ditos |

## Validation Rules

### Regras por Requisito

| FR | Rule | Error |
|----|------|-------|
| FR-001 | file_path não pode ser vazio | `ValueError` |
| FR-007 | Arquivo deve existir no caminho informado | `FileNotFoundError` |
| FR-008 | CSV não pode estar vazio (zero linhas de dados) | Erro descritivo |
| FR-009 | Todas as linhas devem ter o mesmo número de colunas | Erro descritivo |
| FR-010 | Tamanho do arquivo não pode exceder 100MB | Erro descritivo |

### Regras por User Story

**US1 (P1)**:
- CSV com cabeçalho e 10 linhas → DataFrame com 10 linhas e nomes das
  colunas do cabeçalho
- Colunas numéricas inferidas como números; colunas de texto como texto

**US2 (P2)**:
- Delimitador customizado → colunas separadas corretamente
- Encoding Latin-1 → acentuação preservada
- Tipos explicitados → coluna carregada com tipo especificado

**US3 (P3)**:
- Arquivo inexistente → `FileNotFoundError` com mensagem clara
- CSV vazio → erro "CSV vazio"
- Linhas inconsistentes → erro descritivo

## State Transitions

A extração não possui estado — é uma operação puramente funcional:

```
file_path (str) + config (opcional) → [extrair] → DataFrame
                                                     ↘ Erro descritivo
```

Não há transições de estado porque o dado bruto nunca é alterado
(Princípio IV + Constraints da Constituição).
