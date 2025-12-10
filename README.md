# JurisSocial
## Agente Jurídico para Programas Sociais

Este projeto demonstra a integração do **Gemini API (Google AI)** com a biblioteca **Panel**, criando uma interface de chat interativa que responde em tempo real.

---

## Requisitos

Antes de iniciar, certifique-se de ter instalado:

- Python 3.9 ou superior
- Pip (gerenciador de pacotes)

---

## 1. Instalação

### 1Clone ou baixe este repositório

```bash
git clone https://github.com/unb-Sistemas-de-Machine-learning/Grupo-8-JurisSocial-docs.git

cd Grupo-8-JurisSocial-ajps
```

### Criar ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/MacOS
.venv\Scripts\activate      # Windows
```

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Criar .Env com as variáveis de Ambiente
```bash
# Exemplo de configuração para RagFlow
RAGFLOW_SERVER=https://seu-servidor-ragflow.exemplo
RAGFLOW_API_KEY=insira_sua_api_key_aqui
RAGFLOW_AGENT_ID=insira_seu_agent_id_aqui
RAGFLOW_SESSION_ID=
```

## 2. ChatBot

### Acessar Pasta 
```bash
cd src/chat
```

### Executando o projeto
```bash
panel serve webchat.py --autoreload
```

### Localhost
```bash
http://localhost:5006
```

