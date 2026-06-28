# Contract: Extrair CSV

## Function Signature

```python
def extract_csv(
    file_path: str,
    delimiter: str = ",",
    encoding: str = "utf-8",
    dtypes: dict[str, type] | None = None,
) -> "pd.DataFrame":
    """Carrega dados de um arquivo CSV e retorna um DataFrame.

    Args:
        file_path: Caminho do arquivo CSV (obrigatório).
        delimiter: Delimitador de colunas (padrão: ",").
        encoding: Encoding do arquivo (padrão: "utf-8").
        dtypes: Mapeamento de colunas para tipos. Se None, infere
                automaticamente.

    Returns:
        pd.DataFrame: Dados do CSV em formato tabular.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se o CSV estiver vazio, malformado ou >100MB.
    """
```

## Input Contract

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | `str` | Sim | — | Caminho do arquivo CSV |
| `delimiter` | `str` | Não | `","` | Delimitador de colunas |
| `encoding` | `str` | Não | `"utf-8"` | Encoding do arquivo |
| `dtypes` | `dict[str, type]` | Não | `None` | Tipos por coluna |

## Output Contract

### Success

| Field | Type | Description |
|-------|------|-------------|
| return | `pd.DataFrame` | Dados tabulares com colunas do cabeçalho |

### Error

| Condition | Exception | Message |
|-----------|-----------|---------|
| Arquivo não existe | `FileNotFoundError` | "Arquivo não encontrado: {path}" |
| Arquivo > 100MB | `ValueError` | "Arquivo excede o limite de 100MB: {path}" |
| CSV vazio | `ValueError` | "CSV vazio: {path}" |
| Linhas inconsistentes | `ValueError` | "CSV malformado em {path}: linha {n} tem {x} colunas, esperava {y}" |

## Dependencies

- `pandas` >= 2.2, < 3
- `logging` (stdlib)

## Version

1.0.0 — Initial contract for csv-data-extraction feature.
