# Quickstart: Validação de Dados de Vendas

## Pré-requisitos

- Python 3.14
- Pandas >= 2.2, < 3
- pytest
- Ambiente virtual ativado (`.venv/`)

## Setup

```bash
# Ativar ambiente virtual
source .venv/bin/activate  # Linux
# .venv\Scripts\activate   # Windows

# Dependências já instaladas via pip install -e ".[dev]"
```

## Validar Dados de Vendas

```bash
python -c "
from src.extract import extract_csv
from src.validate import validate_sales

# Carregar dados brutos
df = extract_csv('data/electronics_sales_raw.csv')
print(f'Registros carregados: {len(df)}')

# Validar
df_valid = validate_sales(df)
print(f'Registros válidos: {len(df_valid)}')
print(f'Registros rejeitados: {len(df) - len(df_valid)}')
print(df_valid.head())
"
```

**Saída esperada** (exemplo):
```
Registros carregados: 7000
Registros válidos: 7000
Registros rejeitados: 0
```

## Validar Rejeição

Para testar a detecção de registros inválidos, use um DataFrame com dados propositalmente inconsistentes:

```bash
python -c "
import pandas as pd
from src.validate import validate_sales

df_teste = pd.DataFrame({
    'order_id': [1, 2, 3],
    'quantity': [2, 0, -1],
    'unit_price': [50.0, 25.0, 10.0],
    'discount_pct': [0.1, 0.5, 1.5],
    # ... demais colunas (preenchidas com dados válidos)
})

df_valido = validate_sales(df_teste)
print(f'Válidos: {len(df_valido)}')  # Deve ser 1 (apenas o registro 1)
"
```

## Executar Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Apenas testes de validação
python -m pytest tests/test_validate.py -v
```

## Referências

- [Spec](spec.md) — Especificação da feature
- [Contract](contracts/validate-sales.md) — Contrato da função
- [Data Model](data-model.md) — Modelo de dados
