import json
from datetime import datetime
import sqlite3
import streamlit as st
from groq import Groq

# =========================================================
# BANCO DE DADOS (FUNÇÕES DEVEM FICAR NO TOPO)
# =========================================================

def init_db():
    conn = sqlite3.connect("nexus_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def salvar_mensagem(role, content):
    conn = sqlite3.connect("nexus_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversas (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def carregar_mensagens():
    conn = sqlite3.connect("nexus_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM conversas ORDER BY id ASC")
    linhas = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in linhas]

init_db()

init_db()

# Inicializa o session_state com segurança se a chave ainda não existir
if "messages" not in st.session_state:
    st.session_state.messages = carregar_mensagens()
    
# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Nexus AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# TEMAS VISUAIS (TOTALMENTE ESCUROS E ALTO CONTRASTE)
# =========================================================

THEMES = {
    "Roxo Cósmico": {
        "background": "#0a0612",
        "sidebar_bg": "#0f091a",
        "accent": "#c084fc",
        "user_bg": "#4c1d95",
        "bot_bg": "#1e1035",
        "input_bg": "#180e29",
        "border": "#a855f7"
    },
    "Neon Azul": {
        "background": "#070a12",
        "sidebar_bg": "#0b0f19",
        "accent": "#38bdf8",
        "user_bg": "#1e3a8a",
        "bot_bg": "#111827",
        "input_bg": "#0f172a",
        "border": "#3b82f6"
    },
    "Verde Cyber": {
        "background": "#030d0b",
        "sidebar_bg": "#041410",
        "accent": "#34d399",
        "user_bg": "#065f46",
        "bot_bg": "#09241d",
        "input_bg": "#064e3b",
        "border": "#10b981"
    },
    "Vermelho Dark": {
        "background": "#0d0306",
        "sidebar_bg": "#140509",
        "accent": "#fb7185",
        "user_bg": "#881337",
        "bot_bg": "#240a10",
        "input_bg": "#4c0519",
        "border": "#f43f5e"
    },
    "Oceano Profundo": {
        "background": "#030c12",
        "sidebar_bg": "#05131a",
        "accent": "#22d3ee",
        "user_bg": "#164e63",
        "bot_bg": "#09222e",
        "input_bg": "#083344",
        "border": "#06b6d4"
    }
}

# =========================================================
# ESTADO DA APLICAÇÃO
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = 1

if "theme" not in st.session_state:
    st.session_state.theme = "Roxo Cósmico"

theme = THEMES.get(st.session_state.theme, THEMES["Roxo Cósmico"])

# =========================================================
# PAINEL LATERAL
# =========================================================

with st.sidebar:
    st.markdown("## ◈ NEXUS AI")
    st.caption("Painel de Controle")

    st.divider()

    selected_theme = st.selectbox(
        "Tema Visual",
        options=list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme)
    )

    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.divider()

    st.markdown("### Conversa")
    st.caption(f"Mensagens nesta conversa: **{len(st.session_state.messages)}**")

    if st.button("＋ Nova Conversa", use_container_width=True):
        if st.session_state.messages:
            st.session_state.conversations.append({
                "id": st.session_state.conversation_id,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "messages": list(st.session_state.messages)
            })
            st.session_state.conversation_id += 1

        st.session_state.messages = []
        st.rerun()

    if st.button("Limpar Conversa Atual", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("### Histórico")

    if not st.session_state.conversations:
        st.caption("Nenhuma conversa anterior salva nesta sessão.")
    else:
        for conversation in reversed(st.session_state.conversations):
            with st.expander(f"Conversa {conversation['id']} · {conversation['date']}"):
                for message in conversation["messages"]:
                    role = "Você" if message["role"] == "user" else "Nexus"
                    st.markdown(f"**{role}:** {message['content']}")

                if st.button("Abrir Conversa", key=f"open_{conversation['id']}", use_container_width=True):
                    if st.session_state.messages:
                        st.session_state.conversations.append({
                            "id": st.session_state.conversation_id,
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "messages": list(st.session_state.messages)
                        })

                    st.session_state.messages = list(conversation["messages"])
                    st.session_state.conversations = [
                        item for item in st.session_state.conversations
                        if item["id"] != conversation["id"]
                    ]
                    st.session_state.conversation_id = conversation["id"]
                    st.rerun()

    st.divider()

    st.markdown("### Exportar")

    export_data = {
        "assistant": "Nexus AI",
        "conversation": st.session_state.messages
    }

    st.download_button(
        "Baixar conversa (.json)",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name="nexus_conversa.json",
        mime="application/json",
        use_container_width=True
    )

    st.caption("O histórico é mantido durante a sessão atual.")

# =========================================================
# CSS PROFUNDO (ELIMINAÇÃO DE TODAS AS ÁREAS BRANCAS)
# =========================================================

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* 1. FUNDO GERAL ESCURO (Remove topo branco e laterais) */
    html, body, [data-testid="stAppViewContainer"], .stApp, header, [data-testid="stHeader"] {{
        background-color: {theme["background"]} !important;
        color: #ffffff !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* 2. BARRA LATERAL */
    [data-testid="stSidebar"] {{
        background-color: {theme["sidebar_bg"]} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}

    [data-testid="stSidebar"] * {{
        color: #f1f5f9 !important;
    }}

    /* 3. CAIXA DE CHAT INFERIOR (Chat Input & Container do fundo) */
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"], div[data-testid="stChatInput"] {{
        background-color: {theme["background"]} !important;
    }}

    /* Caixa onde se digita */
    div[data-testid="stChatInput"] {{
        border: 2px solid {theme["border"]} !important;
        border-radius: 14px !important;
        background-color: {theme["input_bg"]} !important;
    }}

    /* ÁREA DE TEXTO DIGITADO DA CAIXA DE CHAT */
    div[data-testid="stChatInput"] textarea {{
        color: #ffffff !important;
        background-color: transparent !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #94a3b8 !important;
    }}

    /* 4. BALÕES DE MENSAGENS */
    [data-testid="stChatMessage"] {{
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }}

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        background-color: {theme["user_bg"]} !important;
    }}

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: {theme["bot_bg"]} !important;
    }}

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] div, 
    [data-testid="stChatMessage"] span {{
        color: #ffffff !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }}

    /* 5. SELECTBOX DO MENU LATERAL (Corrigindo fundo branco do menu) */
    div[data-baseweb="select"] > div {{
        background-color: {theme["sidebar_bg"]} !important;
        color: #ffffff !important;
        border-color: {theme["border"]} !important;
    }}

    div[data-baseweb="popover"] div {{
        background-color: {theme["sidebar_bg"]} !important;
        color: #ffffff !important;
    }}

    /* 6. CABEÇALHO DO NEXUS AI */
    .nexus-header {{
        padding: 24px 28px;
        margin-bottom: 24px;
        border: 1px solid {theme["border"]};
        border-radius: 16px;
        background: {theme["sidebar_bg"]};
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    }}

    .nexus-logo {{
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 3px;
        color: {theme["accent"]};
        margin-bottom: 6px;
    }}

    .nexus-title {{
        font-size: 36px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
    }}

    .nexus-description {{
        color: #cbd5e1;
        font-size: 15px;
        line-height: 1.5;
    }}

    .nexus-status {{
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        margin-top: 14px;
        border-radius: 20px;
        color: {theme["accent"]};
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid {theme["accent"]};
        font-size: 12px;
        font-weight: 600;
    }}

    /* BOTÕES */
    .stButton > button, .stDownloadButton > button {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        font-weight: 600 !important;
    }}

    .stButton > button:hover, .stDownloadButton > button:hover {{
        border-color: {theme["accent"]} !important;
        background-color: {theme["accent"]}33 !important;
        color: #ffffff !important;
    }}

    footer, #MainMenu {{
        visibility: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CABEÇALHO PRINCIPAL
# =========================================================

st.markdown(
    """
    <div class="nexus-header">
        <div class="nexus-logo">N / SYSTEM</div>
        <div class="nexus-title">Nexus AI</div>
        <div class="nexus-description">
            Assistente de Inteligência Artificial avançado.<br>
            Respostas objetivas, raciocínio estruturado e comunicação profissional.
        </div>
        <div class="nexus-status">● Sistema Online</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# CONFIGURAÇÃO RIGOROSA DO MODELO DA IA
# =========================================================

SYSTEM_PROMPT = """
Você é o NEXUS AI, um sistema computacional de inteligência artificial estrito, profissional, sério e extremamente objetivo.

DIRETRIZES COMPORTAMENTAIS OBRIGATÓRIAS:
1. Responda estritamente em letras minúsculas em todas as circunstâncias.
2. Utilize exclusivamente o idioma português brasileiro.
3. Mantenha um tom estritamente neutro, sério e formal.
4. PROIBIDO ABSOLUTAMENTE: participar de jogos (como pedra, papel e tesoura), brincadeiras, apostas, conversas fiadas, piadas, elogios ou reações emocionais.
5. Se o usuário tentar iniciar um jogo ou brincadeira, recuse imediatamente com uma frase séria e direta, por exemplo: "não participo de jogos ou brincadeiras. como posso auxiliar em uma tarefa técnica?".
6. Responda diretamente ao cerne da questão, sem introduções ou cordialidades excessivas.
"""

# =========================================================
# EXIBIÇÃO DAS MENSAGENS
# =========================================================

if not st.session_state.messages:
    st.markdown("### Nova Conversa")
    st.caption("Envie uma mensagem abaixo para iniciar.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================================================
# CONEXÃO GROQ & PROCESSAMENTO
# =========================================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.warning("A chave da Groq não foi encontrada. Configure `GROQ_API_KEY` em `.streamlit/secrets.toml`.")
    st.stop()

client = Groq(api_key=api_key)

if prompt := st.chat_input("digite sua mensagem para o nexus..."):
  # salva a sua mensagem no banco de dados
  salvar_mensagem("user", prompt)
  st.session_state.messages.append({"role": "user", "content": prompt})

  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    with st.spinner("processando solicitação..."):
      try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *st.session_state.messages,
            ],
            temperature=0.2,
            max_completion_tokens=4096,
        )

        answer = (
            response.choices[0].message.content
            or "não foi possível gerar uma resposta."
        )

        st.markdown(answer)

        # salva a resposta da ia no banco de dados
        salvar_mensagem("assistant", answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

      except Exception as error:
        st.error(
            "não foi possível obter uma resposta da ia. verifique a conexão."
        )
        st.caption(f"detalhes técnicos: {error}")