from supabase_client import search_similar_documents
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Instancia o modelo OpenAI (gpt-3.5-turbo por padrão)
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.2  # Respostas mais diretas
)

def generate_answer_with_rag(user_question: str) -> str:
    """
    Faz busca vetorizada no Supabase + gera resposta com o LLM
    """

    # Busca os documentos relevantes
    search_results = search_similar_documents(user_question)
    context = "\n\n".join([doc['doc_content'] for doc in search_results])

    if not context:
        return "Desculpe, não encontrei informações relevantes para sua pergunta."

    # Monta o prompt para o LLM
    messages = [
        SystemMessage(content="Você é um assistente inteligente que responde baseando-se apenas nos documentos fornecidos."),
        HumanMessage(content=f"Documentos disponíveis:\n{context}\n\nPergunta do usuário: {user_question}\n\nBaseando-se apenas nos documentos acima, responda da forma mais útil possível.")
    ]

    # Gera resposta
    response = llm(messages)

    return response.content
