from flask import Flask, request, jsonify
from supabase_client import save_message
import os
import requests
from rag_agent_graph import graph, GraphState
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configs (pega do .env ou seta direto)
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Função para responder mensagem no WhatsApp via Twilio API


def send_whatsapp_message(to_number: str, message: str):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

    payload = {
        'From': f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
        'To': f'whatsapp:{to_number}',
        'Body': message
    }

    response = requests.post(
        url,
        data=payload,
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    )
    return response

# Rota para receber mensagens do Twilio


@app.route('/webhook', methods=['POST'])
def webhook():
    # Pega os dados que o Twilio envia
    from_number = request.form.get('From', '')
    body = request.form.get('Body', '')

    print(f"Mensagem recebida de {from_number}: {body}")

    # Salvar no banco
    save_message(from_number, body)

    # Buscar resposta com LangGraph
    result = graph.invoke(GraphState(user_question=body))
    print(result)
    response_message = result['response']

    # Enviar resposta pelo WhatsApp
    send_whatsapp_message(from_number.replace(
        'whatsapp:', ''), response_message)

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(port=5000)
