# pyspark-data-reconciliation

Projeto de portfólio em **PySpark** para **conciliação de dados** entre duas fontes que deveriam representar o mesmo evento de negócio: pedidos registrados no ERP e transações registradas no gateway de pagamento.

O objetivo é demonstrar, de forma simples e validável, como estruturar um pipeline em camadas **Bronze / Silver / Gold** para:

- ingerir dados brutos de múltiplas fontes
- padronizar e tipar dados para comparação
- reconciliar registros por chave de negócio
- identificar divergências
- gerar indicadores consolidados de qualidade da conciliação

---

## Objetivo do projeto

Construir um pipeline batch em PySpark para comparar duas fontes de dados:

- **ERP Orders**: o que o sistema interno da empresa registrou como pedido
- **Gateway Transactions**: o que o processador de pagamento registrou como transação

O pipeline gera:

- uma tabela Gold com o resultado da conciliação por `order_id`
- uma tabela Gold agregada com os principais indicadores da execução

---

## Cenário de negócio

Em operações reais, é comum que um pedido aprovado no ERP precise ter correspondência com uma transação no gateway de pagamento. Quando isso não acontece, ou quando os valores e status não batem, surgem divergências operacionais que precisam ser monitoradas.

Este projeto simula esse cenário com um mock dataset pequeno, mas suficiente para cobrir os principais casos de conciliação.

---

## Arquitetura

### Bronze
Camada de ingestão bruta.

Responsabilidades:

- ler os arquivos CSV de entrada
- preservar os valores originais
- adicionar colunas técnicas de rastreabilidade

Views/tabelas:

- `pyspark_data_reconciliation__stg__erp_orders`
- `pyspark_data_reconciliation__stg__gateway_transactions`

### Silver
Camada de padronização e tipagem.

Responsabilidades:

- aplicar `trim` em campos textuais
- padronizar caixa (`upper`)
- converter datas e timestamps
- converter valores monetários para decimal
- padronizar `order_id`
- padronizar `currency`
- padronizar `payment_method`
- padronizar status para domínio comparável

Views/tabelas:

- `pyspark_data_reconciliation__calc__erp_orders`
- `pyspark_data_reconciliation__calc__gateway_transactions`

### Gold
Camada de consumo analítico e de negócio.

Responsabilidades:

- reconciliar as fontes por `order_id`
- classificar o resultado da conciliação
- consolidar os indicadores da execução

Views/tabelas:

- `pyspark_data_reconciliation__calc__recon_order_result`
- `pyspark_data_reconciliation__calc__agg_reconciliation_summary`

---

## Datasets de entrada

### ERP Orders
Campos:

- `order_id`
- `order_date`
- `customer_id`
- `expected_amount`
- `currency`
- `payment_method`
- `order_status`

### Gateway Transactions
Campos:

- `transaction_id`
- `order_id`
- `transaction_date`
- `paid_amount`
- `currency`
- `payment_method`
- `transaction_status`

---

## Mock dataset usado no projeto

### `erp_orders.csv`

```csv
order_id,order_date,customer_id,expected_amount,currency,payment_method,order_status
O1001,2026-01-05,C001,100.00,BRL,CREDIT_CARD,PAID
 O1002 ,2026-01-06,C002,250.50,brl,pix,paid
O1003,2026-01-06,C003,80.00,BRL,BOLETO,PAID
O1004,2026-01-07,C004,120.00,BRL,CREDIT_CARD,PAID
O1005,2026-01-07,C005,300.00,BRL,PIX,PAID
O1006,2026-01-08,C006,50.00,BRL,PIX,PENDING
```

### `gateway_transactions.csv`

```csv
transaction_id,order_id,transaction_date,paid_amount,currency,payment_method,transaction_status
T9001,O1001,2026-01-05 10:15:00,100.00,BRL,CREDIT_CARD,APPROVED
T9002, o1002 ,2026-01-06 11:00:00,250.50,brl,PIX,approved
T9003,O1003,2026-01-06 14:22:00,79.00,BRL,BOLETO,APPROVED
T9004,O1004,2026-01-07 09:40:00,120.00,BRL,CREDIT_CARD,PENDING
T9007,O1007,2026-01-08 16:10:00,500.00,BRL,PIX,APPROVED
T9008,O1008,2026-01-08 18:30:00,42.30,BRL,PIX,APPROVED
```

---

## Regras de negócio

### Chave de conciliação

- `order_id`

### Padronizações aplicadas na Silver

- `trim` em strings
- `upper` em campos textuais relevantes
- tipagem de datas e timestamps
- tipagem monetária com decimal
- normalização de status para comparação direta na Gold

### Mapeamento de status

#### ERP
- `PAID -> PAID`
- `PENDING -> PENDING`

#### Gateway
- `APPROVED -> PAID`
- `PENDING -> PENDING`

### Tolerância de valor

Um registro é considerado divergente por valor quando:

- `abs(erp_amount - gateway_amount) > 0.01`

### Ordem de precedência da conciliação

A classificação da Gold segue a seguinte ordem:

1. `MISSING_IN_ERP`
2. `MISSING_IN_GATEWAY`
3. `AMOUNT_MISMATCH`
4. `STATUS_MISMATCH`
5. `MATCHED`

---

## Estrutura da Gold

### 1. `recon_order_result`

Tabela principal da conciliação.

**Grão:**

- 1 linha por `order_id` da união entre ERP e Gateway

**Estratégia:**

- `full outer join` por `order_id`

**Campos principais:**

- `order_id`
- `erp_order_date`
- `gateway_transaction_date`
- `customer_id`
- `erp_amount`
- `gateway_amount`
- `amount_difference`
- `erp_currency`
- `gateway_currency`
- `erp_status`
- `gateway_status`
- `exists_in_erp`
- `exists_in_gateway`
- `erp_payment_method`
- `gateway_payment_method`
- `reconciliation_status`
- `ingestion_date`

**Classificações possíveis:**

- `MATCHED`
- `MISSING_IN_ERP`
- `MISSING_IN_GATEWAY`
- `AMOUNT_MISMATCH`
- `STATUS_MISMATCH`

### 2. `agg_reconciliation_summary`

Tabela agregada com os indicadores consolidados da execução.

**Grão:**

- 1 linha por execução

**Campos:**

- `total_orders`
- `matched_count`
- `divergent_count`
- `missing_in_erp_count`
- `missing_in_gateway_count`
- `amount_mismatch_count`
- `status_mismatch_count`
- `match_rate`

---

## Resultado esperado

### Bronze

- `erp_orders_bronze`: **6 registros**
- `gateway_transactions_bronze`: **6 registros**

### Silver

- `erp_orders_silver`: **6 registros**
- `gateway_transactions_silver`: **6 registros**

### Gold principal

- `recon_order_result`: **8 registros**

Distribuição esperada de `reconciliation_status`:

- `MATCHED`: **2**
- `MISSING_IN_ERP`: **2**
- `MISSING_IN_GATEWAY`: **2**
- `AMOUNT_MISMATCH`: **1**
- `STATUS_MISMATCH`: **1**

### Gold agregada

- `agg_reconciliation_summary`: **1 registro**

Valores esperados:

- `total_orders = 8`
- `matched_count = 2`
- `divergent_count = 6`
- `missing_in_erp_count = 2`
- `missing_in_gateway_count = 2`
- `amount_mismatch_count = 1`
- `status_mismatch_count = 1`
- `match_rate = 25.00`

---

## Resultado validado no projeto

Os resultados obtidos no projeto bateram com o esperado:

- Bronze validada
- Silver validada
- `recon_order_result` validada
- `agg_reconciliation_summary` validada

Casos críticos confirmados:

- `O1001` → `MATCHED`
- `O1002` → `MATCHED`
- `O1003` → `AMOUNT_MISMATCH`
- `O1004` → `STATUS_MISMATCH`
- `O1005` → `MISSING_IN_GATEWAY`
- `O1006` → `MISSING_IN_GATEWAY`
- `O1007` → `MISSING_IN_ERP`
- `O1008` → `MISSING_IN_ERP`

---

## Estrutura do repositório

```text
app/
├── .devcontainer/
│   └── devcontainer.json
├── .vscode/
│   └── settings.json
├── data/
│   ├── input/
│   │   ├── erp_orders.csv
│   │   └── gateway_transactions.csv
│   ├── output/
│   │   ├── bronze/
│   │   │   ├── erp_orders/
│   │   │   └── gateway_transactions/
│   │   ├── gold/
│   │   │   ├── agg_reconciliation_summary/
│   │   │   └── recon_order_result/
│   │   └── silver/
│   │       ├── erp_orders/
│   │       └── gateway_transactions/
│   └── tmp/
├── docker/
│   └── Dockerfile
├── notebooks/
│   └── test.ipynb
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── bronze/
│   │   │   ├── erp_orders.yaml
│   │   │   └── gateway_transactions.yaml
│   │   ├── gold/
│   │   │   ├── agg_reconciliation_summary.yaml
│   │   │   └── recon_order_result.yaml
│   │   └── silver/
│   │       ├── erp_orders.yaml
│   │       └── gateway_transactions.yaml
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── all.py
│   │   ├── bronze/
│   │   │   ├── __init__.py
│   │   │   ├── erp_orders.py
│   │   │   └── gateway_transactions.py
│   │   ├── gold/
│   │   │   ├── __init__.py
│   │   │   ├── agg_reconciliation_summary.py
│   │   │   └── recon_order_result.py
│   │   └── silver/
│   │       ├── __init__.py
│   │       ├── erp_orders.py
│   │       └── gateway_transactions.py
│   ├── layers/
│   │   ├── __init__.py
│   │   ├── bronze/
│   │   │   ├── __init__.py
│   │   │   ├── erp_orders.py
│   │   │   └── gateway_transactions.py
│   │   ├── gold/
│   │   │   ├── __init__.py
│   │   │   ├── agg_reconciliation_summary.py
│   │   │   └── recon_order_result.py
│   │   └── silver/
│   │       ├── __init__.py
│   │       ├── erp_orders.py
│   │       └── gateway_transactions.py
│   └── readers/
│       ├── __init__.py
│       ├── bronze/
│       │   ├── __init__.py
│       │   ├── erp_orders.py
│       │   └── gateway_transactions.py
│       ├── gold/
│       │   ├── __init__.py
│       │   ├── agg_reconciliation_summary.py
│       │   └── recon_order_result.py
│       └── silver/
│           ├── __init__.py
│           ├── erp_orders.py
│           └── gateway_transactions.py
├── stagefy/
├── tests/
├── pyproject.toml
└── uv.lock
```

---

## Como executar

Na raiz do projeto, no host/WSL:

```bash
cd "/pyspark-data-reconciliation"
docker compose up -d --build
docker compose exec app bash
```

Depois, dentro do container `app`:

```bash
cd /workspace/app
uv sync
```

O fluxo recomendado para notebooks e execuções é via **Dev Container**:

1. Abrir `/pyspark-data-reconciliation/app` no VS Code
2. Reabrir no Dev Container
3. Selecionar o kernel Python do ambiente do container (ambiente `/.venv` criado com o `uv`)
4. Criar e executar notebooks normalmente

Ajuste os caminhos e comandos conforme a estrutura do seu projeto.

Fluxo esperado:

1. ler os CSVs de entrada
2. construir Bronze
3. construir Silver
4. construir `recon_order_result`
5. construir `agg_reconciliation_summary`
6. salvar os resultados em `output/bronze`, `output/silver` e `output/gold`

Exemplo conceitual:

```bash
python -m src.jobs.all
python -m src.jobs.bronze.erp_orders
python -m src.jobs.silver.gateway_transactions
python -m src.jobs.gold.recon_order_result
```

---

## Principais pontos técnicos demonstrados

Este projeto evidencia:

- leitura de arquivos CSV com PySpark
- arquitetura em camadas Bronze / Silver / Gold
- limpeza e padronização de dados
- cast de tipos e tratamento de datas
- `full outer join`
- comparação entre duas fontes por chave de negócio
- regras de conciliação com precedência
- criação de tabela analítica e tabela agregada
- validação de resultado esperado

---

## Possíveis melhorias futuras

Para manter o projeto enxuto, alguns itens ficaram fora desta versão e podem entrar em uma evolução futura:

- tratamento explícito de duplicidades
- tabela separada de divergências
- regras adicionais de conciliação, como `PAYMENT_METHOD_MISMATCH`
- regras de rejeição de registros inválidos
- mais agregações analíticas
- testes automatizados mais completos
- parametrização por data de execução
