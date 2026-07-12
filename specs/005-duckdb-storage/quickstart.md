# Quickstart: DuckDB Analytical Storage

**Feature**: 005-duckdb-storage
**Date**: 2026-07-12

## Prerequisites

- Python 3.14+
- Dependências instaladas: `pip install -e ".[dev]"`
- DuckDB adicionado ao `pyproject.toml` (dependência desta feature)

## Validation Scenarios

### Scenario 1: Persistência básica (P1)

Verificar que o pipeline completo cria o banco DuckDB com a tabela `sales`.

```bash
# Executar pipeline de ponta a ponta
python -c "
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales
from src.store import store_analytics

df = extract_csv('data/input.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)
store_analytics(df, 'output/test.duckdb')
"

# Verificar que o arquivo foi criado
ls -la output/test.duckdb

# Verificar contagem de registros
python -c "
import duckdb
con = duckdb.connect('output/test.duckdb', read_only=True)
count = con.execute('SELECT COUNT(*) FROM sales').fetchone()[0]
print(f'Registros persistidos: {count}')
con.close()
"
```

**Expected**: Arquivo `output/test.duckdb` criado com todos os registros do DataFrame.

---

### Scenario 2: Views criadas corretamente (P2)

Verificar que todas as 5 views são criadas e retornam dados.

```bash
python -c "
import duckdb
con = duckdb.connect('output/test.duckdb', read_only=True)

views = ['v_monthly_revenue', 'v_store_performance', 'v_category_sales', 'v_top_products', 'v_sales_summary']
for view in views:
    result = con.execute(f'SELECT COUNT(*) FROM {view}').fetchone()[0]
    print(f'{view}: {result} rows')

con.close()
"
```

**Expected**: Todas as views retornam pelo menos 1 registro.

---

### Scenario 3: Idempotência (P2)

Executar duas vezes e verificar que os dados são idênticos.

```bash
# Primeira execução
python -c "
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales
from src.store import store_analytics

df = extract_csv('data/input.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)
store_analytics(df, 'output/test.duckdb')
"

# Capturar métricas da primeira execução
python -c "
import duckdb
con = duckdb.connect('output/test.duckdb', read_only=True)
r1 = con.execute('SELECT COUNT(*) AS cnt, SUM(net_revenue) AS total_rev FROM sales').fetchone()
print(f'Exec 1: rows={r1[0]}, revenue={r1[1]:.2f}')
con.close()
"

# Segunda execução (sobrescreve)
python -c "
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales
from src.store import store_analytics

df = extract_csv('data/input.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)
store_analytics(df, 'output/test.duckdb')
"

# Capturar métricas da segunda execução
python -c "
import duckdb
con = duckdb.connect('output/test.duckdb', read_only=True)
r2 = con.execute('SELECT COUNT(*) AS cnt, SUM(net_revenue) AS total_rev FROM sales').fetchone()
print(f'Exec 2: rows={r2[0]}, revenue={r2[1]:.2f}')
con.close()
"
```

**Expected**: `Exec 1` e `Exec 2` mostram exatamente os mesmos valores de `rows` e `revenue`.

---

### Scenario 4: Validação de integridade (P2)

Verificar que contagem de registros e soma de receita conferem entre DataFrame e DuckDB.

```bash
python -c "
import duckdb
import pandas as pd
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales

# Pipeline em memória
df = extract_csv('data/input.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)

expected_count = len(df)
expected_revenue = df['net_revenue'].sum()

# DuckDB
con = duckdb.connect('output/test.duckdb', read_only=True)
actual_count = con.execute('SELECT COUNT(*) FROM sales').fetchone()[0]
actual_revenue = con.execute('SELECT SUM(net_revenue) FROM sales').fetchone()[0]
con.close()

assert expected_count == actual_count, f'Count mismatch: {expected_count} vs {actual_count}'
assert abs(expected_revenue - actual_revenue) < 0.01, f'Revenue mismatch: {expected_revenue} vs {actual_revenue}'
print(f'Integrity check PASSED: {actual_count} rows, revenue={actual_revenue:.2f}')
"
```

**Expected**: `Integrity check PASSED` com valores idênticos.

---

### Scenario 5: Tratamento de diretório inexistente (FR-006)

Verificar que o diretório de destino é criado automaticamente.

```bash
rm -rf output/subdir/

python -c "
from src.extract import extract_csv
from src.validate import validate_sales
from src.prepare import prepare_sales
from src.analyze import analyze_sales
from src.store import store_analytics

df = extract_csv('data/input.csv')
df = validate_sales(df)
df = prepare_sales(df)
df = analyze_sales(df)
store_analytics(df, 'output/subdir/nested/test.duckdb')
"

ls -la output/subdir/nested/test.duckdb
```

**Expected**: Arquivo `output/subdir/nested/test.duckdb` criado com sucesso.

---

### Scenario 6: Testes unitários

```bash
pytest tests/test_store.py -v
```

**Expected**: Todos os testes passam (TDD — testes escritos antes da implementação).
