# PySpark Lab — Template de stack por projeto

Template de ambiente local para desenvolvimento com **PySpark + Docker + uv + VS Code Dev Container**.

## 1. Objetivo

Este repositório entrega uma stack local pronta para uso, com:

- infraestrutura Spark dedicada ao projeto
- container `app` preparado para desenvolvimento
- integração com `uv`
- integração com VS Code Dev Container

A proposta é fornecer um **ambiente base**, não um framework de aplicação.

O usuário pode:

- criar a própria `SparkSession`
- definir seus próprios paths
- usar ou não `src/`, `tests`, `notebooks`
- organizar o projeto da forma que preferir

## 2. Arquitetura

A stack possui 3 serviços:

- `spark-master`
- `spark-worker`
- `app`

### `spark-master`
Responsável pelo cluster manager do Spark.

### `spark-worker`
Executa as tarefas distribuídas do cluster.

### `app`
Ambiente de desenvolvimento e execução do projeto, contendo:

- Python 3.10
- `uv`
- dependências Python do projeto
- código-fonte
- notebooks
- testes

## 3. Estrutura de pastas

```text
<path-do-projeto>/
├─ compose.yaml
├─ .env.example
├─ .gitignore
├─ README.md
├─ infra/
│  └─ spark/
│     └─ conf/
└─ app/
   ├─ docker/
   │  └─ Dockerfile
   ├─ .devcontainer/
   │  └─ devcontainer.json
   ├─ pyproject.toml
   ├─ uv.lock
   ├─ src/
   ├─ tests/
   ├─ notebooks/
   └─ data/
```

As pastas dentro de `app/` são fornecidas como **estrutura inicial sugerida**, mas não são obrigatórias.

## 4. Filosofia da stack

Esta stack é um **template de ambiente**, não um framework de aplicação.

Ela entrega:

- cluster Spark local
- container `app` com Python 3.10
- `uv` como gerenciador de dependências
- integração com VS Code Dev Container
- estrutura inicial de diretórios

Ela **não obriga**:

- uso de `settings.py`
- uso de `src/`
- uso de `jobs/`
- uso de paths específicos
- uso de uma forma única de criar `SparkSession`

## 5. Pré-requisitos

- Docker Desktop
- WSL2
- VS Code
- extensão Dev Containers

## 6. Imagens base

### Infra Spark
- `apache/spark:3.5.8-scala2.12-java17-python3-ubuntu`

### App
- `python:3.10-slim-bookworm`

## 7. Dependências Python base

### Principais
- `pyspark==3.5.8`
- `pandas<3`
- `openpyxl`

### Dev
- `autopep8`
- `flake8`
- `rope`
- `pylint`
- `ipykernel`
- `ruff`
- `pytest`

## 8. Convenções de caminhos no README

Nos exemplos abaixo:

- substitua `<path-do-projeto>` pelo diretório onde você baixou ou clonou esta stack
- `/workspace/app` é o caminho **dentro do container `app`**

Exemplo:

- no host/WSL: `cd "<path-do-projeto>"`
- dentro do container: `cd /workspace/app`

## 9. Como subir a stack pela primeira vez

Na raiz do projeto, no host/WSL:

```bash
cd "<path-do-projeto>"
docker compose up -d --build
docker compose exec app bash
```

Depois, dentro do container `app`:

```bash
cd /workspace/app
uv sync
```

### Validação rápida do ambiente

Depois do `uv sync`, você pode validar se o PySpark está funcional com um teste simples num arquivo `.py` ou em um notebook:

```python
from pyspark.sql import SparkSession

spark = SparkSession.Builder().getOrCreate()

spark.range(5).show()
```

Se o comando executar normalmente, o ambiente base está funcional.

## 10. Uso diário do Docker

### Subir a stack
```bash
cd "<path-do-projeto>"
docker compose up -d
```

### Entrar no app
```bash
cd "<path-do-projeto>"
docker compose exec app bash
```

### Derrubar a stack
```bash
cd "<path-do-projeto>"
docker compose down
```

### Parar sem remover containers
```bash
cd "<path-do-projeto>"
docker compose stop
```

### Subir novamente após stop
```bash
cd "<path-do-projeto>"
docker compose start
```

## 11. Fluxo com `uv`

O gerenciamento Python do projeto dentro de `app/` pode ser feito com `uv`.

Exemplos:

### Sincronizar dependências
```bash
uv sync
```

### Adicionar dependência
```bash
uv add pyspark
```

### Rodar script simples
```bash
uv run python main.py
```

### Rodar módulo
```bash
uv run python -m meu_modulo
```

A forma de organização do código fica a critério do usuário.

## 12. VS Code e notebooks

O fluxo recomendado para notebooks é via **Dev Container**.

### Fluxo recomendado
1. Abrir `<path-do-projeto>/app` no VS Code
2. Reabrir no Dev Container
3. Selecionar o kernel Python do ambiente do container (ambiente `/.venv` criado com o `uv`)
4. Criar e executar notebooks normalmente

## 13. Volumes

### No serviço `app`
- `./app -> /workspace/app`
- `./app/data -> /shared-data`

### No serviço `spark-worker`
- `./app/data -> /shared-data`

O uso desses caminhos dentro do projeto fica a critério do usuário.

## 14. Múltiplas stacks ao mesmo tempo

O template foi pensado para permitir múltiplas stacks independentes, desde que as portas expostas no host não entrem em conflito.

Todas as portas expostas no host devem ser únicas.

Isso vale tanto:
- entre stacks diferentes rodando ao mesmo tempo
- quanto dentro da própria stack

Exemplo incorreto:
- `SPARK_MASTER_UI_PORT=8082`
- `SPARK_WORKER_UI_PORT=8082`

Exemplo correto:
- `SPARK_MASTER_UI_PORT=8082`
- `SPARK_MASTER_PORT=7078`
- `SPARK_WORKER_UI_PORT=8083`

### O que é automático
- nomes de containers
- nomes de networks
- nomes de volumes

### O que pode precisar de ajuste
Somente as **portas host** expostas no `.env`, se duas stacks forem executadas ao mesmo tempo e houver conflito.

### Exemplo de `.env`
```env
SPARK_MASTER_UI_PORT=8080
SPARK_MASTER_PORT=7077
SPARK_WORKER_UI_PORT=8081

SPARK_WORKER_MEMORY=2G
SPARK_WORKER_CORES=2
```

Se existir conflito com outra stack, ajuste apenas as portas host.

## 15. Reset da stack

### Rebuild normal
```bash
cd "<path-do-projeto>"
docker compose up -d --build
```

### Reset mais forte
```bash
cd "<path-do-projeto>"
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d
```

### Reset total
```bash
cd "<path-do-projeto>"
docker compose down -v --remove-orphans
docker compose build --no-cache
docker compose up -d
docker compose exec app bash -lc "cd /workspace/app && uv sync"
```

## 16. Troubleshooting

### 1. `uv` não encontrado no WSL
Use o `uv` **dentro do container `app`**, não no host WSL.

Exemplo:

```bash
cd "<path-do-projeto>"
docker compose exec app bash
```

### 2. Notebook não encontra imports
Confirme que:

- o projeto está aberto no Dev Container
- o kernel selecionado é o Python do container (ambiente `/.venv` criado com o `uv`)
- o código está sendo executado no mesmo ambiente do `uv`

### 3. Mudanças no Dockerfile não refletiram
Force rebuild:

```bash
cd "<path-do-projeto>"
docker compose up -d --build
```

Se necessário:

```bash
cd "<path-do-projeto>"
docker compose build --no-cache
docker compose up -d
```

### 4. Warning do Hadoop no início do job
O warning abaixo é esperado em ambiente local/containerizado:

```text
WARN NativeCodeLoader: Unable to load native-hadoop library for your platform...
```

Isso não invalida a stack se os jobs estiverem executando normalmente.

## 17. O que este template entrega

- ambiente local para PySpark
- infraestrutura Spark dedicada ao projeto
- container `app` pronto para desenvolvimento
- integração com `uv`
- integração com Dev Container
- estrutura inicial de diretórios

## 18. O que este template não impõe

- uma arquitetura obrigatória de código
- uma convenção obrigatória de paths
- uma implementação obrigatória de `SparkSession`
- um conjunto obrigatório de jobs, readers, writers ou notebooks

## 19. Próximos passos possíveis

- criar sua própria `SparkSession`
- definir sua própria camada de configuração
- estruturar o projeto em `src/`
- criar notebooks e pipelines próprios
- usar a stack como base para novos projetos independentes
