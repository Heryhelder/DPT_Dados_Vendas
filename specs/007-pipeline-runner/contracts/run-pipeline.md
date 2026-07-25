# Contract: run_pipeline Function Interface

**Date**: 2026-07-25

## Function Signature

```python
def run_pipeline(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    output_dir: str | Path = "output",
) -> Path:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | `str \| Path` | `DEFAULT_INPUT_PATH` | Path to input CSV file |
| `output_dir` | `str \| Path` | `"output"` | Directory for `.duckdb` output files |

### Return Value

| Type | Description |
|------|-------------|
| `Path` | Absolute path to the output directory |

### Behavior

1. Calls `extract_csv(input_path)` → raw DataFrame
2. Calls `validate_sales(raw_df)` → cleaned DataFrame
3. Calls `prepare_sales(clean_df)` → prepared DataFrame
4. Calls `analyze_sales(prepared_df)` → analytical DataFrame
5. Calls `store_analytics(analytical_df, output_dir)` → 5 `.duckdb` files
6. Logs processing summary (rows, revenue, files, duration)
7. Returns output directory path

### Raises

| Exception | Condition |
|-----------|-----------|
| `FileNotFoundError` | Input CSV file does not exist |
| `ValueError` | DataFrame is empty after validation |
| Any stage exception | Propagated from the failing stage |

### Side Effects

- Creates/overwrites `.duckdb` files in the output directory
- Creates the output directory if it does not exist
- Logs processing summary via `logging`

### Idempotency

Re-running with the same inputs produces identical output files.

## Example Usage

```python
from src.pipeline import run_pipeline

# Run with defaults
output_path = run_pipeline()
# Uses data/electronics_sales_raw.csv → output/

# Run with custom paths
output_path = run_pipeline(
    input_path="data/custom_data.csv",
    output_dir="custom_output",
)
```
