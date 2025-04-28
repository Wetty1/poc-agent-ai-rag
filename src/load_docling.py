import os
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def read_docling_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text, max_tokens=500):
    """
    Divide o texto em pedaços menores para caber no limite do modelo
    """
    sentences = text.split(". ")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for sentence in sentences:
        tokens = len(sentence.split())  # estimativa simples: 1 palavra ~ 1 token
        if current_tokens + tokens > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
            current_tokens = tokens
        else:
            current_chunk += sentence + ". "
            current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def generate_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def upload_chunk_to_supabase(content, embedding, metadata=None):
    data = {
        "content": content,
        "embedding": embedding,
        "metadata": metadata or {},
    }
    response = supabase.table("documents").insert(data).execute()
    return response

def process_docling_file(file_path):
    text = read_docling_file(file_path)
    chunks = chunk_text(text)

    print(f"Dividindo {file_path} em {len(chunks)} pedaços...")

    for i, chunk in enumerate(chunks):
        print(f"Processando chunk {i+1}/{len(chunks)}...")
        embedding = generate_embedding(chunk)
        upload_chunk_to_supabase(chunk, embedding, metadata={"source_file": os.path.basename(file_path)})

    print(f"Arquivo {file_path} carregado com sucesso no Supabase!")

if __name__ == "__main__":
    folder_path = "./docling_files"  # Pasta onde estão seus arquivos

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            process_docling_file(os.path.join(folder_path, filename))
