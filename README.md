# 🤖 WhatsApp RAG Agent (LangChain + Supabase + Twilio)

Projeto de agente de recuperação aumentada (RAG) com integração de WhatsApp.
Recebe mensagens no WhatsApp, busca respostas em documentos com embeddings no Supabase, e responde automaticamente.

# ⚙️ Stack do Projeto

### 🦜 LangChain (RAG / LLM)

### 🦑 Supabase (PostgreSQL + Vetores + Armazenamento)

### 📞 Twilio (API WhatsApp)

### 🌍 Flask (Webhook API)

### 💬 LangGraph (orquestração de fluxo de conversa)

## 📂 Arquitetura

```textplain


Usuário (WhatsApp)
      |
   Twilio (Webhook)
      |
   webhook.py (Flask)
      |
+-------------+
| Supabase    | <---> Armazena mensagens + documentos com embeddings
| (Postgres)  |
+-------------+
      |
 rag_agent_graph.py
 (LangGraph + RAG)
      |
Resposta via WhatsApp (Twilio)
```

# 🚀 Como rodar o projeto

## 1️⃣ Clone o projeto

```bash
git clone https://github.com/seu-usuario/whatsapp-rag-agent.git
cd whatsapp-rag-agent
```

## 2️⃣ Instale as dependências

```bash
pip install -r requirements.txt
```

## 3️⃣ Configure o .env

Crie um arquivo .env na raiz com suas credenciais:

```ini


SUPABASE_URL=...
SUPABASE_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+seunumero
OPENAI_API_KEY=sk-...
```

## 4️⃣ Configure o Supabase

Crie as tabelas documents e messages

Ative Row Level Security (RLS)

Configure policies de SELECT e INSERT

## 5️⃣ Carregue documentos no Supabase (opcional)

```bash
python load_docling.py
```

## 6️⃣ Exponha o webhook com ngrok

``` bash
ngrok http 5000
```

Copie a URL pública do ngrok e configure no Twilio (Webhook → Messaging → A MESSAGE COMES IN)

```arduino
https://SEU_NGROK_URL/webhook
```

## 7️⃣ Rode o servidor

```bash
python webhook.py
```

## 📱 Testando

Envie uma mensagem no WhatsApp para o número configurado no Twilio:

Exemplo: "Qual é a missão da empresa?"

O agente buscará a resposta nos documentos e responderá automaticamente no WhatsApp. 📩

## 📚 Estrutura do projeto

```graphql
├── src                         # Pasta de recursos
    ├── load_docling.py         # Carrega documentos e gera embeddings
    ├── rag_agent_graph.py      # RAG com LangGraph (agente principal)
    ├── supabase_client.py      # Conexão e queries no Supabase
    ├── webhook.py              # API Flask (Webhook do Twilio)
├── .env                        # variáveis de ambiente
├── requirements.txt            # Dependências do projeto
└── README.md                   # Este arquivo
```
