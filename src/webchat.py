import panel as pn
import requests

pn.config.theme = 'dark'


# --- Função que conversa com o RAGflow ---
def query_ragflow(question: str):
    url = "http://localhost:8000/api/v1/rag/chat"  # coloque o seu endpoint

    payload = {
        "query": question,
        "stream": False  # se quiser streaming real via SSE podemos ativar depois
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    data = response.json()

    # RAGflow + Gemini deve retornar algo como:
    # { "answer": "texto final" }
    return data.get("answer", "[sem resposta do RAGflow]")


def generate_response(contents: str, user: str, chat_interface: pn.chat.ChatInterface):

    full_answer = query_ragflow(contents)

    buffer = ""
    for char in full_answer:
        buffer += char
        yield buffer


# UI do chat
chat_interface = pn.chat.ChatInterface(callback=generate_response)
chat_interface.send("Olá! Como posso ajudar?", user="System", avatar="🤖", respond=False)

chatbot = pn.Column(
    pn.pane.Markdown("# Chatbot RAGflow + Gemini Pro ✨"),
    chat_interface,
    styles={"padding": "15px", "border": "1px solid white"},
)

chatbot.servable()
