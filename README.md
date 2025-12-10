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
git clone https://github.com/unb-Sistemas-de-Machine-learning/JurisSocial.git

cd JurisSocial
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

