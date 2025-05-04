# rag_agent_graph.py

import os
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langchain.schema import SystemMessage, HumanMessage
from dataclasses import dataclass
from supabase_client import search_similar_documents

# Configura o LLM
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-3.5-turbo",
    temperature=0.2
)

# Estado do gráfico


@dataclass
class GraphState:
    user_question: str
    context: str = ""
    response: str = ""

# Função que decide se busca documentos ou não


def decide(state: GraphState):
    question = state.user_question.lower()
    trigger_words = ["documento", "informação", "dados",
                     "conteúdo", "base", "inventário", "estoque"]

    if any(word in question for word in trigger_words):
        print("Decisão: Buscar documentos (RAG)")
        return "do_rag"
    else:
        print("Decisão: Responder direto sem RAG")
        return "do_direct"

# Função que busca documentos e gera resposta com contexto


def do_rag(state: GraphState):
    question = state.user_question
    search_results = search_similar_documents(question)

    context = "\n\n".join([doc['doc_content'] for doc in search_results])
    if not context:
        context = "Nenhuma informação relevante foi encontrada."

    messages = [
        SystemMessage(
            content="Você é um assistente inteligente que responde baseando-se apenas nos documentos fornecidos."),
        HumanMessage(
            content=f"Documentos disponíveis:\n{context}\n\nPergunta do usuário: {question}\n\nBaseando-se apenas nos documentos acima, responda da forma mais útil possível.")
    ]
    response = llm(messages)

    return GraphState(
        user_question=question,
        context=context,
        response=response.content
    )

# Função que responde diretamente sem buscar documentos


def do_direct(state: GraphState):
    question = state.user_question
    messages = [
        SystemMessage(
            content="Você é um assistente útil que responde perguntas diretamente."),
        HumanMessage(content=question)
    ]
    response = llm(messages)

    return GraphState(
        user_question=question,
        context="",
        response=response.content
    )

# Função finaliza e retorna resposta


def finalize(state: GraphState):
    return state


# Monta o fluxo
workflow = StateGraph(GraphState)

workflow.add_node("do_rag", do_rag)
workflow.add_node("do_direct", do_direct)

workflow.set_conditional_entry_point(decide, {
    "do_rag": "do_rag",
    "do_direct": "do_direct"
})

workflow.add_edge("do_rag", END)
workflow.add_edge("do_direct", END)

graph = workflow.compile()
