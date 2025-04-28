from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
import openai
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# Carregar configs
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar clientes
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY
embeddings_model = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Salvar mensagem bruta no Supabase
def save_message(user_number: str, message: str):
    response = supabase.table("messages").insert({
        "user_number": user_number,
        "message": message
    }).execute()
    return response

# Gerar e salvar embedding de um texto no Supabase
def save_document(text: str, metadata: dict = {}):
    embedding = embeddings_model.embed_query(text)
    
    # Inserir no banco (supondo tabela 'documents' com coluna 'embedding' como vetor 1536)
    response = supabase.table("documents").insert({
        "content": text,
        "embedding": embedding,
        "metadata": metadata
    }).execute()
    return response

# Buscar documentos similares a uma query
def search_similar_documents(query: str, top_k: int = 3):
    query_embedding = embeddings_model.embed_query(query)
    
    # Buscar usando pgvector no Supabase
    response = supabase.rpc(
        'match_documents',  # Essa função você terá que criar no Supabase (já explico como)
        {
            "query_embedding": query_embedding,
            "match_count": top_k     # Quantos resultados trazer
        }
    ).execute()
    return response.data
