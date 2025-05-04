from langgraph.graph import StateGraph, END
from langgraph.prebuilt import chat_agent_executor
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from supabase_client import search_similar_documents
from langchain_community.chat_message_histories import RedisChatMessageHistory
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Instancia o LLM
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.2
)

# Define ferramentas que o agente pode usar


@tool
def search_docs_tool(query: str) -> str:
    """Busca informações relevantes nos documentos armazenados."""
    results = search_similar_documents(query)
    if not results:
        return "Nenhuma informação encontrada."
    return "\n\n".join([doc['doc_content'] for doc in results])


# Conjunto de ferramentas
tools = [search_docs_tool]
tool_executor = chat_agent_executor(tools)

# Define o estado inicial


class AgentState:
    user_message: str
    agent_response: str = None
    tool_calls: list = []
    tool_results: list = []
    session_id: str = None

# Função do LLM decidir o que fazer


def llm_decide(state):
    user_input = state["user_message"]
    session_id = state["session_id"]

    # Recupera histórico
    if session_id:
        history = RedisChatMessageHistory(
            session_id=session_id,
            url=REDIS_URL
        )
        chat_history = history.messages
    else:
        chat_history = []

    # Decide o próximo passo baseado no contexto
    messages = chat_history + [{"role": "user", "content": user_input}]
    response = llm.invoke(messages)

    if "busque" in response.content.lower() or "documento" in response.content.lower():
        # Se o modelo indicar necessidade de buscar documentos
        return {"tool_calls": [ToolInvocation(tool="search_docs_tool", input=user_input)]}
    else:
        return {"agent_response": response.content}

# Função para executar ferramentas


def execute_tools(state):
    tool_calls = state["tool_calls"]
    tool_outputs = tool_executor.invoke(tool_calls)
    return {"tool_results": tool_outputs}

# Finaliza com uma resposta ao usuário


def finalize(state):
    if state.get("tool_results"):
        return {"agent_response": state["tool_results"][0]}
    return {"agent_response": state["agent_response"]}


# Cria o LangGraph
graph = StateGraph(AgentState)

graph.add_node("decide", llm_decide)
graph.add_node("execute", execute_tools)
graph.add_node("finalize", finalize)

graph.set_entry_point("decide")
graph.add_edge("decide", "execute")
graph.add_edge("execute", "finalize")
graph.add_edge("finalize", END)

langgraph_app = graph.compile()

# Função principal que você pode importar no webhook


def run_langgraph(user_input: str, session_id: str):
    result = langgraph_app.invoke(
        {"user_message": user_input, "session_id": session_id})
    return result["agent_response"]
