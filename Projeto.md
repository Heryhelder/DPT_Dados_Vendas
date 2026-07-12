# ETL com Dados de Vendas

Projeto de Engenharia de Dados, focado na construção de um pipeline ETL. A proposta é transformar dados simples em insights relevantes para o contexto empresarial, por meio da validação, tratamento e modelagem em SQL com DuckDB, gerando uma base sólida e análises que realmente seriam aproveitados.

# Requisitos

## **BI / Visualização**

- Tableau

Tableau é uma plataforma de ***Business Intelligence*** e ***visualização de dados*** que permite a criação de dashboards interativos e análises visuais de forma simples e rápida.

## **Linguagens**

- **SQL (duckDB)**
- **Python 3.14**
    - Pandas ≥ 2.2, <3
    - ipykernel ≥ 7.2.0

## **Princípios**

- KISS (Keep It Simple, Stupid)
- YAGNI (You Ain't Gonna Need It)
- DRY (Don't Repeat Yourself)

Essas tecnologias foram utilizadas para:

- limpeza e tratamento de dados
- modelagem analítica
- criação de tabelas e views
- desenvolvimento das métricas utilizadas no dashboard

# Features

## Extração de Dados

* Entrada: arquivo `.csv` (dados brutos)
* Carregamento para um DataFrame (pandas)

## Validação de Dados

### 1. Checagens e tratamento principal:

* Conferir consistência entre colunas numéricas, como quantidade, valor unitário, desconto e valor de venda.
* Padronizar tipos de dados, convertendo datas para formato datetime, valores monetários para float.
* Remover espaços extras, corrigir capitalização e manter apenas registros válidos após o tratamento inicial.

## Preparação analítica e definição de métricas

### **1. Padronizações típicas:**

* Criar colunas para ajudar na análise como mês, ano, trimestre.
* Estruturar a base por dimensões de negócio: região, vendedor, categoria, canal e tipo de cliente.
* Organizar a tabela para facilitar filtros e comparações.

## Analise de comportamento e padrão

### 1. Exemplos de métricas:

* Analisar sazonalidade, observando picos e quedas ao longo do tempo.
* Calcular faturamento total, ticket médio, quantidade vendida e desconto médio.
* Identificar produtos e categorias de melhor desempenho.
* Calcular `gross_revenue` = `quantity * unit_price`.
* Calcular `net_revenue` = `gross_revenue * (1 - discount_pct)`.
* Criar `cost_of_goods_sold` com base em regra por subcategoria e depois calcular `gross_profit = net_revenue - cost_of_goods_sold`.

### 2. Métricas opcionais:

- A partir das novas colunas criadas pode ser calculado, ebitda, net_income, avg_ticket, realizar comparações de desempenho,  entre outras métricas de negócio.
- Utilizar customer_id para verificação de recorrência.

## Modelagem e criação de tabelas e views

### 1. Criação de tabelas e views:

* Criar tabelas para armazenar os dados analíticos tratados e modelados.
* Criar views para facilitar a consulta aos dados.
* Utilizar a linguagem SQL para criar tabelas e views.
* Salvar os dados no DuckDB.

## Dashboard no Tableau

* Salvar os dados tratados e levar para tableau.
* Antes de inserir os gráficos, criar uma estrutura com blocos para melhor apresentação.
* Separar áreas de KPIs, tendências, comparações e filtros.

## Views analíticas

### **1. Crie a estrutura do dashboard**

1. Monte primeiro os blocos principais da tela.
2. Reserve a área superior para KPIs.
3. Separe áreas para tendência, comparação e filtros.
4. Insira os gráficos no Tableau.