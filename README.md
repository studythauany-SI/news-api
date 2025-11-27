📰 News API – FastAPI + Supabase

API REST para criação, listagem, edição e exclusão de notícias, integrada ao Supabase (Auth + Database).

🚀 Tecnologias

FastAPI

Supabase (Auth, RLS, PostgREST)

HTTPX

Pydantic

Uvicorn

📂 Estrutura
news/
 ├── main.py
 ├── schemas.py
 ├── supabase_client.py
 ├── requirements.txt
 ├── .env.example
 └── README.md

🔧 Configuração

Crie um .env baseado no .env.example:

SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_ANON_KEY="xxxxx"
SUPABASE_SERVICE_ROLE_KEY="xxxxx"
TABLE_NEWS="news"


Instalação:

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


Executar:

uvicorn main:app --reload


Swagger: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

🔐 Autenticação

Gerar token:

POST /login
{
  "email": "seu_email",
  "password": "sua_senha"
}


Use o token no botão Authorize do Swagger.

📌 Endpoints Principais

POST /news – Criar notícia

GET /news – Listar notícias do usuário

GET /news/{id} – Buscar notícia

PUT /news/{id} – Atualizar notícia

DELETE /news/{id} – Excluir notícia
