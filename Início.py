import streamlit as st
from auth_session import run_login_page
import base64
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.markdown("""
    <style>
        /* Torna a sidebar mais escura no tema claro */
        /* Seletor para o container principal da sidebar (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 {
            background-color: #333333; /* Um cinza escuro para a sidebar */
            color: #FFFFFF; /* Cor do texto geral dentro da sidebar para contraste */
        }
        
        /* Estiliza o TEXTO dentro dos ITENS (páginas/links) da sidebar (ATUALIZADO) */
        /* Removido o ':nth-child(1)' para aplicar a todos os itens */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a > span {
            color: #ffffff !important; /* Exemplo: Azul claro para o texto dos links */
            /* Você pode adicionar outras propriedades aqui, como: */
            /* font-weight: bold; */
        }

        /* Estiliza o HOVER (quando o mouse passa por cima) dos itens da sidebar (ATUALIZADO) */
        /* Note que o :hover é aplicado ao <a> pai para que toda a área do link reaja */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover {
            background-color: #555555; /* Um fundo levemente mais claro no hover */
            border-radius: 5px; /* Adiciona bordas arredondadas no hover */
        }
        /* Estiliza o texto do item no HOVER (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover > span {
            color: #00BFFF !important; /* Um azul mais forte no hover para o texto */
        }


        /* Estiliza o item ATIVO (página atualmente selecionada) na sidebar (ATUALIZADO) */
        /* O [aria-current="page"] é aplicado ao <a> pai */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] {
            background-color: #444444; /* Fundo diferente para a página ativa */
        }
        /* Estiliza o texto do item ATIVO (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] > span {
            color: #FFD700 !important; /* Exemplo: Amarelo para a página ativa */
            font-weight: bold; /* Deixa o texto em negrito */
        }

        /* Exemplo para qualquer texto padrão ou título na sidebar que não seja um link (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 p, 
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h1,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h2,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h3,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h4,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h5,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h6 {
            color: #FFFFFF !important;
        }

        /* Estiliza o H1 do título "Contratos - 25/2024-SEMINF" */
        h1[data-testid="stMarkdownContainer"] {
            color: var(--text-color) !important;
        }
        
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Início", page_icon="images/icone-quanta.png", layout="wide", initial_sidebar_state="collapsed")
st.logo("images/logo-quanta-oficial.png", size="large")

def imagem_para_base64(caminho_para_imagem: str) -> str:
    try:
        with open(caminho_para_imagem, "rb") as f:
            dados = f.read()
        return base64.b64encode(dados).decode()
    except FileNotFoundError:
        return ""

is_logged_in = run_login_page()

if is_logged_in:
    st.markdown('<h1 data-testid="stMarkdownContainer">Contratos - 25/2024-SEMINF</h1>', unsafe_allow_html=True)

    colimg1, colimg2, colimg3, colimg4 = st.columns(4)

    with colimg1:
        st.image("images/icone-alocacoes.png", width=190)
        if st.button("Alocações", key="btn_alocacoes"):
            st.switch_page("pages/Alocações.py")
    with colimg2:
        st.image("images/logo-fortaleza.png", width=180)
        if st.button("Monitoramento", key="btn_fortaleza"):
            st.switch_page("pages/Fortaleza_Dashboard.py")
    with colimg3:
        st.image("images/prefeitura-macae.png", width=200)
        if st.button("Assessoria SEMED", key="btn_macae"):
            st.switch_page("pages/Macaé_Dashboard.py")
    with colimg4:
        st.image("images/prefeitura-maricá.png", width=200)
        if st.button("Assessoria CODEMAR", key="btn_marica"):
            st.switch_page("pages/Maricá_Dashboard.py")
    st.divider()

    credentials_dict = st.session_state.get("credentials", {})
    usernames_dict = credentials_dict.get("usernames", {})
    username = st.session_state.get("username")
    user_data = usernames_dict.get(username, {})
    role = user_data.get("role", "comum")

    if role == "admin":
        st.markdown(":orange[:material/crown: Acesso como Administrador]")
    elif role == "comum":
        st.markdown(":blue[:material/account_circle: Bem Vindo!]")