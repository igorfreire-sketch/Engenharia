import streamlit as st
import pandas as pd 
from auth_session import protect_page

from fortaleza.component_table import show_table

st.markdown("""
    <style>
        /* Ajusta o padding e margem gerais da aplicação */
        html, body {
            padding-top: 0px !important;
            margin-top: -80px !important;
        }
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
            
        #monitoramento-fortaleza {
            margin-top: -40px !important; /* Ajuste o valor conforme necessário */ 
        }
            
        /* Estilos da Sidebar */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 {
            background-color: #333333;
            color: #FFFFFF;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a > span {
            color: #ffffff !important;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover {
            background-color: #555555;
            border-radius: 5px;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover > span {
            color: #00BFFF !important;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] {
            background-color: #444444;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] > span {
            color: #FFD700 !important;
            font-weight: bold;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 p, 
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h1,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h2,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h3,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h4,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h5,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h6 {
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Monitoramento Fortaleza", page_icon="images/icone-quanta.png", layout="wide", initial_sidebar_state="collapsed")
st.logo("images/logo-quanta-oficial.png", size="large")

protect_page()

@st.cache_data
def load_data():
    df = pd.read_excel("data/Monitoramento Equipe Quanta-07 09 2025.xlsx")

    required_columns = {
        #"ITEM": "indice", 
        "COORDENADOR RESPONSÁVEL": "responsavel",
        "CONTRATO": "contrato",
        "Nº CTO": "numero contrato",
        #"TIPO DE CONTRATO": "tipo do contrato",
        "RESPONSÁVEL PELO  PRODUTO": "responsavel do produto",
        "RESPONSÁVEL PELA TAREFA": "responsavel da tarefa",
        "FUNÇÃO": "funcao",
        "EQUIPE TERCEIRAZADA": "equipe terceirizada",
        "STATUS": "status",
        #"DETALHAMENTO DO STATUS": "detalhamento do status",
        "DATA INÍCIAL": "inicio",
        "DATA FINAL": "termino",
        "PENCENTUAL ALOCAÇÃO": "percentual"
    }

    df_filtrado = df.rename(columns=lambda col: col.strip())[list(required_columns.keys())].copy()
    df_filtrado.rename(columns=required_columns, inplace=True)
    df = df_filtrado
    return df

df = load_data()

st.markdown('<h1 style="margin-bottom: -30px;margin-top: 20px;">Monitoramento Fortaleza</h1>', unsafe_allow_html=True)

tab_table = st.radio(
    "Navegação",
    ["📋 Tabela"],
    horizontal=True,
    label_visibility="collapsed",
    key='main_tabs' 
)

if tab_table == '📋 Tabela':
    show_table(df)