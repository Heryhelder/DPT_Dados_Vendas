# Quickstart: Extração de Dados CSV

## Pré-requisitos

- Python 3.14
- Pandas >= 2.2, < 3
- pytest

## Setup

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install "pandas>=2.2,<3" pytest
```

## Validar Extração

```bash
# Criar arquivo CSV de teste
cat > data/input.csv << 'EOF'
produto,quantidade,preco_unitario
Camiseta,10,39.90
Calça,5,89.90
Tênis,3,199.90
EOF

# Executar extração (via script ou notebook)
python -c "
from src.extract import extract_csv

df = extract_csv('data/input.csv')
print(df)
print(f'Linhas: {len(df)}')
print(f'Colunas: {list(df.columns)}')
"
```

**Saída esperada**:
```
    produto  quantidade  preco_unitario
0  Camiseta          10           39.90
1     Calça           5           89.90
2     Tênis           3          199.90
Linhas: 3
Colunas: ['produto', 'quantidade', 'preco_unitario']
```

## Validar Erros

```bash
# Arquivo inexistente
python -c "
from src.extract import extract_csv
extract_csv('data/inexistente.csv')
"
# → FileNotFoundError: Arquivo não encontrado: data/inexistente.csv

# CSV vazio
python -c "
from src.extract import extract_csv
extract_csv('data/vazio.csv')
"
# → ValueError: CSV vazio: data/vazio.csv
```

## Executar Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Apenas testes de extração
python -m pytest tests/test_extract.py -v
```

## Referências

- [Spec](spec.md) — Especificação da feature
- [Contract](contracts/extract-csv.md) — Contrato da função
- [Data Model](data-model.md) — Modelo de dados
