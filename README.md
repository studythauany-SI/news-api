# News API

API de notícias desenvolvida com FastAPI e Supabase.

## 🚀 Como rodar o projeto localmente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Inicie o servidor:
```bash
uvicorn main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000`

## 🌐 Como hospedar no Render

### Pré-requisitos
- Conta no [Render](https://render.com) (gratuita)
- Conta no [Supabase](https://supabase.com) com projeto criado
- Repositório Git (GitHub, GitLab ou Bitbucket)

### Passo a Passo

#### 1. Preparar o repositório

Certifique-se de que seu repositório contém os seguintes arquivos:
- `main.py` (código da aplicação)
- `requirements.txt` (dependências)
- Arquivo `.env` **não deve estar no repositório** (use apenas localmente)

#### 2. Criar Web Service no Render

1. Acesse [https://dashboard.render.com](https://dashboard.render.com)
2. Clique em **"New +"** e selecione **"Web Service"**
3. Conecte seu repositório Git (autorize o acesso se necessário)
4. Selecione o repositório do projeto `news`

#### 3. Configurar o Web Service

Preencha as seguintes informações:

- **Name**: `news-api` (ou nome de sua preferência)
- **Region**: Escolha a região mais próxima (ex: `Oregon (US West)`)
- **Branch**: `main` (ou sua branch principal)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

#### 4. Configurar Variáveis de Ambiente

Na seção **Environment Variables**, adicione as seguintes variáveis:

| Key | Value |
|-----|-------|
| `SUPABASE_URL` | Sua URL do Supabase (ex: `https://xxx.supabase.co`) |
| `SUPABASE_ANON_KEY` | Sua chave anônima do Supabase |
| `TABLE_NEWS` | `news` (nome da tabela) |

**Como obter as credenciais do Supabase:**
1. Acesse seu projeto no [Supabase](https://app.supabase.com)
2. Vá em **Settings** → **API**
3. Copie a **URL** e a **anon/public key**

#### 5. Selecionar o Plano

- Escolha o plano **Free** para começar
- Clique em **"Create Web Service"**

#### 6. Aguardar o Deploy

- O Render irá automaticamente:
  1. Clonar seu repositório
  2. Instalar as dependências
  3. Iniciar a aplicação
- Acompanhe os logs em tempo real
- O primeiro deploy pode levar alguns minutos

#### 7. Acessar sua API

Após o deploy bem-sucedido:
- Sua API estará disponível em: `https://news-api.onrender.com` (substitua pelo nome que você escolheu)
- Acesse a documentação interativa em: `https://news-api.onrender.com/docs`

### ⚙️ Configurações Adicionais

#### Auto-Deploy
Por padrão, o Render faz deploy automático quando você faz push para a branch configurada. Para desabilitar:
1. Vá em **Settings** do seu Web Service
2. Desative **"Auto-Deploy"**

#### Domínio Personalizado
1. Vá em **Settings** → **Custom Domain**
2. Adicione seu domínio
3. Configure os registros DNS conforme as instruções

#### Monitoramento
- Acesse a aba **"Logs"** para ver logs em tempo real
- Acesse a aba **"Metrics"** para ver uso de CPU e memória

### 🔧 Solução de Problemas

#### Erro: "Application failed to start"
- Verifique se o comando de start está correto: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Confirme que todas as variáveis de ambiente estão configuradas

#### Erro: "RuntimeError: Configure SUPABASE_URL e SUPABASE_ANON_KEY"
- Verifique se as variáveis de ambiente `SUPABASE_URL` e `SUPABASE_ANON_KEY` estão configuradas corretamente no Render

#### Aplicação fica "suspensa" no plano gratuito
- O plano gratuito do Render suspende a aplicação após 15 minutos de inatividade
- A primeira requisição após a suspensão pode levar ~30 segundos para "acordar" o serviço

### 📝 Notas Importantes

- O plano gratuito do Render tem **750 horas/mês** de uso
- A aplicação pode ficar lenta após períodos de inatividade (cold start)
- Para produção, considere usar um plano pago para melhor performance

### 🔄 Atualizações

Para atualizar sua aplicação:
1. Faça commit e push das alterações no repositório
2. O Render detectará automaticamente e iniciará um novo deploy
3. Acompanhe o progresso na aba **"Events"**

