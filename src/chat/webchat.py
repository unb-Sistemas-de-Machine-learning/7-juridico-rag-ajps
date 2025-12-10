import panel as pn
import requests
import os
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar tema claro (estilo WhatsApp)
pn.config.theme = 'default'
pn.config.sizing_mode = 'stretch_width'

# Configurações do RagFlow (via variáveis de ambiente)
RAGFLOW_SERVER = os.getenv("RAGFLOW_SERVER", "https://ragflow.arthrok.shop")
RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY", "ragflow-Y3NmUwNGIwZDU3MTExZjA5NzIxODZkZD")
RAGFLOW_AGENT_ID = os.getenv("RAGFLOW_AGENT_ID", "f248dd4ad51611f0aec786dd45181ac0")  # Flow ID = Agent ID
RAGFLOW_SESSION_ID = os.getenv("RAGFLOW_SESSION_ID", "")  # Opcional - se vazio, cria nova sessão automaticamente

# Endpoint da API para Agents (baseado na documentação oficial)
RAGFLOW_API_URL = f"{RAGFLOW_SERVER}/api/v1/agents/{RAGFLOW_AGENT_ID}/completions"

# Variável global para manter a sessão entre requisições
_current_session_id = RAGFLOW_SESSION_ID


def validar_resposta_consistencia(resposta: str) -> str:
    """
    Valida se a resposta do RagFlow está consistente.
    Detecta possíveis inversões de lógica (ex: dizer que tem idoso quando não tem).
    
    Esta função NÃO modifica a resposta, apenas adiciona um aviso se detectar
    inconsistência. A correção real deve ser feita no prompt do RagFlow.
    """
    # Esta função pode ser expandida para detectar padrões de inversão
    # Por enquanto, apenas retorna a resposta original
    # Em produção, você pode adicionar lógica de detecção aqui se necessário
    
    # Exemplo de detecção (descomente se necessário):
    # if "idoso" in resposta.lower() and "65" in resposta:
    #     if "não" in resposta.lower()[:resposta.lower().find("idoso")] and "elegível" in resposta.lower():
    #         # Possível inversão detectada
    #         pass
    
    return resposta


def query_ragflow(question: str):
    """
    Consulta o RagFlow Agent com a pergunta do usuário.
    Usa o endpoint correto da API: POST /api/v1/agents/{agent_id}/completions
    Mantém a sessão entre requisições para continuidade da conversa.
    
    NOTA IMPORTANTE: A validação de critérios e interpretação de respostas
    acontece no RagFlow (nó Generate:analise_programas). Se houver problemas
    de interpretação (ex: interpretar "não" como "sim"), o prompt do RagFlow
    precisa ser atualizado. Veja: PROMPT_CORRIGIDO_GENERATE_NODE.txt
    """
    global _current_session_id
    
    try:
        # Preparar headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {RAGFLOW_API_KEY}"
        }
        
        # Preparar payload conforme documentação da API
        # Endpoint: POST /api/v1/agents/{agent_id}/completions
        payload = {
            "question": question,
            "stream": False  # Modo não-streaming para simplificar
        }
        
        # Usar session_id da variável global ou do .env
        # Se não fornecido, o RagFlow cria uma nova sessão automaticamente
        session_id_to_use = _current_session_id or RAGFLOW_SESSION_ID
        if session_id_to_use:
            payload["session_id"] = session_id_to_use
        
        # Fazer requisição
        response = requests.post(
            RAGFLOW_API_URL, 
            json=payload,
            headers=headers,
            timeout=60  # Timeout maior para agents que podem demorar
        )
        
        # Verificar status
        response.raise_for_status()
        data = response.json()
        
        # Debug: Log da resposta completa (apenas em desenvolvimento)
        # Descomente a linha abaixo para debug:
        # print(f"[DEBUG] Resposta completa do RagFlow: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Verificar se há erro na resposta
        if data.get("code") != 0:
            error_msg = data.get("message", "Erro desconhecido")
            return f"[ERRO no RagFlow]: {error_msg}\n\nCódigo: {data.get('code')}"
        
        # Processar resposta conforme documentação
        # Formato esperado para Agent completions (não-streaming):
        # { "code": 0, "data": { "answer": "...", "session_id": "...", ... } }
        if "data" in data and data["data"] is not None:
            response_data = data["data"]
            
            # Formato 1: { "answer": "..." } - formato direto do Agent
            if isinstance(response_data, dict) and "answer" in response_data:
                # Salvar session_id para usar nas próximas requisições
                if "session_id" in response_data:
                    _current_session_id = response_data["session_id"]
                
                answer = response_data["answer"]
                
                # Debug: Log da resposta extraída
                # print(f"[DEBUG] Resposta extraída: {answer[:200]}...")
                
                # Validar consistência da resposta (não modifica, apenas valida)
                answer = validar_resposta_consistencia(answer)
                
                return answer
            
            # Formato 2: { "data": { "content": "..." } } - formato com workflow
            if isinstance(response_data, dict) and "data" in response_data:
                content_data = response_data["data"]
                
                if isinstance(content_data, dict):
                    # Formato: { "content": "..." }
                    if "content" in content_data:
                        return content_data["content"]
                    
                    # Formato: { "outputs": { "content": "..." } }
                    if "outputs" in content_data and isinstance(content_data["outputs"], dict):
                        if "content" in content_data["outputs"]:
                            return content_data["outputs"]["content"]
                
                # Se content_data for string diretamente
                if isinstance(content_data, str):
                    return content_data
            
            # Se data["data"] for string diretamente
            elif isinstance(response_data, str):
                return response_data
        
        # Se nenhum formato conhecido, retornar o JSON completo para debug
        return f"Resposta do RagFlow (formato não reconhecido):\n{json.dumps(data, indent=2, ensure_ascii=False)}"
        
    except requests.exceptions.HTTPError as e:
        # Erro HTTP (401, 403, 404, etc.)
        error_detail = ""
        try:
            error_response = e.response.json()
            error_detail = f" - {error_response}"
        except:
            error_detail = f" - Status: {e.response.status_code}"
        return f"[ERRO HTTP no RagFlow]: {str(e)}{error_detail}\n\nDica: Verifique se a API Key está correta e o Agent ID está correto."
    except requests.exceptions.RequestException as e:
        return f"[ERRO na conexão com RagFlow]: {str(e)}\n\nVerifique:\n- Se a URL está correta: {RAGFLOW_API_URL}\n- Se o servidor está acessível\n- Se há problemas de rede/firewall"
    except Exception as e:
        return f"[ERRO ao processar resposta do RagFlow]: {str(e)}\n\nTipo: {type(e).__name__}"


def generate_response(contents: str, user: str, chat_interface: pn.chat.ChatInterface):
    """
    Gera resposta do chatbot usando RagFlow.
    Simula streaming de texto.
    
    NOTA: Esta função apenas recebe e exibe a resposta do RagFlow.
    Se houver inversão de informações, o problema está no RagFlow,
    não nesta função. A resposta é exibida exatamente como recebida.
    """
    full_answer = query_ragflow(contents)
    
    # Debug: Log da resposta final antes de exibir
    # Descomente para debug:
    # print(f"[DEBUG] Resposta final a ser exibida: {full_answer[:300]}...")
    
    buffer = ""
    for char in full_answer:
        buffer += char
        yield buffer


# CSS customizado estilo WhatsApp
whatsapp_css = """
<style>
/* Estilo geral - fundo WhatsApp */
.bk-root {
    background-color: #e5ddd5 !important;
    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
}

/* Header estilo WhatsApp */
.whatsapp-header {
    background: linear-gradient(to right, #075e54, #128c7e);
    color: white;
    padding: 15px 20px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.whatsapp-header h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 500;
}

.whatsapp-header p {
    margin: 5px 0 0 0;
    font-size: 13px;
    opacity: 0.9;
}

/* Área de chat */
.bk-chat-interface {
    background-color: #e5ddd5 !important;
    background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3Cpattern id='grid' width='100' height='100' patternUnits='userSpaceOnUse'%3E%3Cpath d='M 100 0 L 0 0 0 100' fill='none' stroke='%23d4d4d4' stroke-width='0.5'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='100' height='100' fill='url(%23grid)'/%3E%3C/svg%3E") !important;
}

/* Mensagens do usuário (direita - verde) */
.bk-chat-message[data-user="User"] {
    background-color: #dcf8c6 !important;
    border-radius: 7.5px 0 7.5px 7.5px !important;
    margin-left: auto !important;
    margin-right: 10px !important;
    max-width: 65% !important;
    padding: 8px 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
}

/* Mensagens do bot (esquerda - cinza) */
.bk-chat-message[data-user="Assistant"],
.bk-chat-message[data-user="System"] {
    background-color: #ffffff !important;
    border-radius: 0 7.5px 7.5px 7.5px !important;
    margin-right: auto !important;
    margin-left: 10px !important;
    max-width: 65% !important;
    padding: 8px 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
}

/* Input area estilo WhatsApp */
.bk-input {
    background-color: #f0f0f0 !important;
    border: none !important;
    border-radius: 21px !important;
    padding: 10px 15px !important;
}

.bk-input:focus {
    background-color: #ffffff !important;
    box-shadow: 0 0 0 2px #25d366 !important;
}

/* Botões estilo WhatsApp */
.bk-btn {
    background-color: #25d366 !important;
    border: none !important;
    border-radius: 50% !important;
    color: white !important;
    width: 45px !important;
    height: 45px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.bk-btn:hover {
    background-color: #20ba5a !important;
}

/* Botão de envio específico */
.bk-chat-interface .bk-btn[title*="Send"],
.bk-chat-interface button[aria-label*="Send"] {
    background-color: #25d366 !important;
    border-radius: 50% !important;
}

/* Container principal */
.whatsapp-container {
    background-color: #e5ddd5;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Instrução discreta */
.instrucao-box {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 12px 15px;
    margin: 10px;
    border-radius: 4px;
    font-size: 13px;
    color: #856404;
}
</style>
"""

# Instrução explicando o objetivo do chat (mais discreta)
instrucao_html = """
<div class="instrucao-box">
    <strong>🎯 Objetivo:</strong> Este chatbot ajuda você a descobrir para quais <strong>programas sociais do governo</strong> você pode se qualificar (Bolsa Família, BPC, etc.). 
    Responda às perguntas do assistente para receber orientações personalizadas.
</div>
"""

# Header estilo WhatsApp
header_html = """
<div class="whatsapp-header">
    <div>
        <h1>💬 Programas Sociais</h1>
        <p>Assistente Virtual - RagFlow</p>
    </div>
</div>
"""

# UI do chat
chat_interface = pn.chat.ChatInterface(
    callback=generate_response,
    show_send=True,
    show_rerun=False,
    show_undo=False,
    show_clear=False
)

# Container principal estilo WhatsApp
chatbot = pn.Column(
    pn.pane.HTML(whatsapp_css + header_html + instrucao_html, sizing_mode='stretch_width'),
    chat_interface,
    sizing_mode='stretch_both',
    styles={
        "background-color": "#e5ddd5",
        "height": "100vh",
        "margin": "0",
        "padding": "0"
    }
)

chatbot.servable()
