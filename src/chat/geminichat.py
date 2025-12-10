import panel as pn
from google import genai
import os
from dotenv import load_dotenv

pn.config.theme = 'dark'
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key) 
except Exception as e:
    print(f"Erro ao configurar a API Key. Certifique-se de que GEMINI_API_KEY está definida. Detalhes: {e}")
    pass

def query_gemini(question: str):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=question
        )
        return response.text
        
    except Exception as e:
        return f"[ERRO na API do Gemini]: {e}"


def generate_response(contents: str, user: str, chat_interface: pn.chat.ChatInterface):

    full_answer = query_gemini(contents) 

    buffer = ""
    for char in full_answer:
        buffer += char
        yield buffer


# UI do chat
chat_interface = pn.chat.ChatInterface(callback=generate_response)
chat_interface.send("Olá! Estou conectado ao Gemini Pro! Como posso ajudar?", user="System", avatar="🤖", respond=False)

chatbot = pn.Column(
    pn.pane.Markdown("# Chatbot Gemini Pro ✨"),
    chat_interface,
    styles={"padding": "15px", "border": "1px solid white"},
)

# 3. Rodar o Panel
# Execute este script e acesse o endereço fornecido no terminal (geralmente http://localhost:5006)
chatbot.servable()