# Data Model: Pipeline Runner

**Date**: 2026-07-25

## Entities

### Pipeline Runner Function

Orchestrates the 5-stage ETL pipeline.

| Field | Type | Description |
|-------|------|-------------|
| input_path | str \| Path | Path to input CSV file (default: `data/electronics_sales_raw.csv`) |
| output_dir | str \| Path | Output directory for `.duckdb` files (default: `"output"`) |
| return value | Path | Output directory path (for programmatic use) |

### Pipeline Flow

```
[input.csv] → extract_csv() → [DataFrame raw]
         → validate_sales() → [DataFrame clean]
         → prepare_sales() → [DataFrame prepared]
         → analyze_sales() → [DataFrame analytical]
         → store_analytics() → [5 .duckdb files]
```

## Validation Rules

- Input file must exist (raises `FileNotFoundError` if missing)
- DataFrame must not be empty after validation (raises `ValueError` from store)
- Output directory is created automatically if missing

## State Transitions

```
[Idle] → run_pipeline() → [Extracting] → [Validating] → [Preparing] → [Analyzing] → [Storing] → [Complete]
```

Idempotent: re-running overwrites all output files.
