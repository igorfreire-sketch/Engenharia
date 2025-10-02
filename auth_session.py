import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
import os

load_dotenv()
COOKIE_SECRET = os.getenv("KEY_COOKIE")

def initialize_authenticator():
    """
    Busca as credenciais (do cache ou do BD) e cria um NOVO objeto Authenticator.
    O objeto em si não é armazenado no session_state, permitindo que a
    validação do cookie ocorra em cada recarregamento de página.
    """
    from users import get_all_users_for_auth

    if "credentials" not in st.session_state:
        try:
            user_credentials = get_all_users_for_auth()
            if not user_credentials:
                st.error("Erro: Nenhuma credencial encontrada no banco de dados.")
                st.stop()
            st.session_state["credentials"] = {"usernames": user_credentials}
        except Exception as e:
            st.error(f"Erro ao acessar o banco de dados para autenticação: {e}")
            st.stop()
    authenticator = stauth.Authenticate(
        st.session_state["credentials"], 
        "meu_app_cookie",
        COOKIE_SECRET,
        7
    )
    
    return authenticator

def display_error_page():
    """Exibe uma página de erro padrão para acesso não autorizado."""
    st.logo("images/logo-quanta-oficial.png", size="large")
    st.markdown("""
    <div style='text-align: center; font-size: 60px;'>⚠️🔐</div>
    <div style='text-align: center; font-size: 20px; margin-top: 10px;'>
        <strong>Acesso Negado</strong><br>
        Você não está logado ou não tem permissão para acessar essa página.
    </div>
    <div style='display: flex; justify-content: center; margin-top: 30px;'>
        <a href="/" target="_self">
            <button style='
                padding: 10px 25px; font-size: 18px; background-color: #f63366;
                color: white; border: none; border-radius: 8px; cursor: pointer;'>
                Ir para a tela de Login
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

def render_logout_button(authenticator):
    """Renderiza o botão de logout na sidebar."""
    if authenticator and st.session_state.get("authentication_status"):
        with st.sidebar:
            st.success(f"Bem-vindo(a), {st.session_state.get('name', '')}")
            authenticator.logout("Sair", "sidebar")
            st.markdown("""
            <style>
            button[data-testid="stBaseButton-secondary"] div p {
                font-size: 15px !important;
                font-weight: bold;
            }

            button[data-testid="stBaseButton-secondary"] {
                padding: 0px !important;
                background-color: #f08224 !important;
                color: white !important;              
                border-radius: 8px !important;
                border: none !important;
                width: 220px !important;
            }
                        
            button[kind="secondary"][data-testid="stBaseButton-secondary"]:focus,
            button[kind="secondary"][data-testid="stBaseButton-secondary"]:active,
            button[kind="secondary"][data-testid="stBaseButton-secondary"][aria-pressed="true"] {
                background-color: black !important;
                border: 2px solid orange !important;
                color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)

def run_login_page():
    authenticator = initialize_authenticator()
    authenticator.login()

    if st.session_state.get("authentication_status"):
        render_logout_button(authenticator)
        return True
    elif st.session_state.get("authentication_status") is False:
        st.error("Usuário ou senha incorretos.")
        return False
    elif st.session_state.get("authentication_status") is None:
        st.warning("Por favor, informe seu usuário e senha.")
        return False
    return False

def protect_page():
    """
    Protege uma página de forma robusta para aplicações multipáginas.

    Esta função executa a verificação do cookie em cada carregamento de página
    sem exibir o formulário de login em páginas protegidas.
    """
    authenticator = initialize_authenticator()

    st.markdown("""
        <style>
            [data-testid="stForm"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    authenticator.login()

    if not st.session_state.get("authentication_status"):
        display_error_page()
        st.stop()
    else:
        render_logout_button(authenticator)