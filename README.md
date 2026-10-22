# MLOPS Intent Classifier

API REST construída com **FastAPI** para classificação de intenções em mensagens de texto. Na inicialização, o serviço carrega artefatos de modelos treinados a partir do **Weights & Biases (W&B)**, executa inferência com **TensorFlow / Keras** (*Universal Sentence Encoder Multilingual*) e registra as predições no **MongoDB**.

![Arquitetura da API](docs/arquitetura.svg)

## Estrutura do Projeto

```text
MLOPS_Intent_Classifier/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── src/
│   ├── app.py
│   ├── modules/
│   │   └── intent_classifier/
│   │       ├── controller.py
│   │       ├── service.py
│   │       ├── model.py
│   │       └── intent_classifier.py
│   └── shared/
│       └── database/
│           └── engine.py
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

## Pré-requisitos

- Python 3.11 (ou Conda / Miniconda)
- Docker e Docker Compose
- Conta e chave de API no [Weights & Biases](https://wandb.ai)
- Instância MongoDB (MongoDB Atlas ou servidor local)

## Configuração de Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto a partir do modelo `.env.example`:

```bash
cp .env.example .env
```

Preencha as variáveis no `.env`:

```env
WANDB_API_KEY=wandb_v1_...
WANDB_PROJECT=mlops-2026-2
WANDB_MODELS=seu_usuario/mlops-2026-2/confusion-clf:v0
MONGO_URL=mongodb+srv://usuario:senha@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

| Variável | Obrigatória | Descrição |
| :--- | :--- | :--- |
| `WANDB_API_KEY` | Sim | Chave de autenticação da conta no W&B. |
| `WANDB_PROJECT` | Sim | Nome do projeto no W&B (`mlops-2026-2`). |
| `WANDB_MODELS` | Sim | Caminho do(s) artefato(s) no formato `entidade/projeto/artefato:versao` (separados por vírgula caso haja mais de um). |
| `MONGO_URL` | Sim | String de conexão do MongoDB. |
| `MONGO_DB` | Não | Nome do banco de dados (padrão: `intent_classifier`). |
| `MONGO_PRED_COLLECTION` | Não | Nome da coleção de predições (padrão: `predictions`). |

## Como Executar

### Opção 1: Com Docker Compose

Com o Docker em execução e o arquivo `.env` configurado na raiz:

```bash
docker compose up --build
```

Para rodar em segundo plano e acompanhar os logs do container:

```bash
docker compose up -d
docker logs -f mlops-container
```

Para encerrar o container:

```bash
docker compose down
```

### Opção 2: Ambiente Local (Conda)

```bash
conda create -n mlops-2026-2 python=3.11 -y
conda activate mlops-2026-2
pip install -r requirements.txt
uvicorn src.app:app --port 8000
```

## Endpoints da API

Com a aplicação rodando, a documentação interativa (Swagger UI) fica disponível em `http://localhost:8000/docs`.

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | Health check da aplicação (`{"status": "ok"}`). |
| `GET` | `/docs` | Interface Swagger UI. |
| `POST` | `/predictions` | Recebe um texto, executa os modelos carregados e salva o resultado no MongoDB. |
| `GET` | `/predictions` | Lista as últimas predições registradas no banco (parâmetro opcional `limit`, padrão `20`). |

### Exemplo de Requisição (`POST /predictions`)

```bash
curl -X POST http://localhost:8000/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "id": "lab-001",
    "nome": "Douglas Nunes",
    "text": "eu não estou entendendo nada"
  }'
```

Exemplo de resposta (`200 OK`):

```json
{
  "confusion-clf": {
    "intent": "confusion",
    "probs": {
      "certainty": 0.2660113573074341,
      "confusion": 0.6385301947593689,
      "neutral_statement": 0.09545843303203583
    }
  },
  "message": {
    "id": "lab-001",
    "nome": "Douglas Nunes",
    "text": "eu não estou entendendo nada",
    "timestamp": "2026-10-21T20:07:18.168962+00:00"
  }
}
```

## Testes

Para executar a suíte de testes automatizados (unitários e de integração):

```bash
pip install -r requirements-dev.txt
pytest
```
