import streamlit as st
import pandas as pd
import time

from auth_session import protect_page
from macae.component_table import show_table
from macae.component_graphbar import show_graph
from macae.component_graphbar_tasks import show_tasks_graph
from macae.component_overall import show_overall_table

protect_page()

st.markdown("""
    <style>
        /* Ajusta o padding e margem gerais da aplicação */
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
            
        #acompanhamento-geral-macae {
            margin-top: -40px !important;
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

st.set_page_config(page_title="Dashboard Macaé", page_icon="images/icone-quanta.png",layout="wide", initial_sidebar_state="collapsed")
st.logo("images/logo-quanta-oficial.png", size="large")

@st.cache_data 
def carregar_dados():
    df = pd.read_excel("data/ProjectEmExcel_MKE.xlsx")

    df.dropna(subset=['Nome da Tarefa'], inplace=True)

    colunas_necessarias = {
        "Número da estrutura de tópicos": "hierarquia",
        "Nome da Tarefa": "tarefa",
        "Início": "inicio",
        "Término": "termino",
        "%concluida prev. (Número10)": "previsto",
        "% concluída": "concluido",
        "Responsável 01": "responsavel 1",
        "Responsável 02": "responsavel 2",
        "Nomes dos recursos": "nome dos recursos",
        "Exe.": "execucao",
        "Terceirizadas": "terceiros"
    }
    
    df_filtered = df.rename(columns=lambda col: col.strip())[list(colunas_necessarias.keys())].copy()
    df_filtered.rename(columns=colunas_necessarias, inplace=True)
    df = df_filtered
    
    df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
    df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
    df["terceiros"] = pd.to_numeric(df["terceiros"], errors="coerce").fillna(0)
    
    df['inicio'] = df['inicio'].astype(str)
    df['termino'] = df['termino'].astype(str)

    df['inicio'] = df['inicio'].apply(lambda x: x.split(' ')[1] if ' ' in x else x)
    df['termino'] = df['termino'].apply(lambda x: x.split(' ')[1] if ' ' in x else x)

    df["inicio"] = pd.to_datetime(df["inicio"], format='%d/%m/%y', errors='coerce').dt.strftime('%d/%m/%Y')
    df["termino"] = pd.to_datetime(df["termino"], format='%d/%m/%y', errors='coerce').dt.strftime('%d/%m/%Y')
    
    df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

    df["barra_info"] = df.apply(lambda row: {
        "concluido": round(row["concluido"] * 100),
        "previsto": round(row["previsto"])
    }, axis=1).apply(lambda x: str(x).replace("'", '"'))

    columns = list(df.columns)
    idx = columns.index("concluido")
    columns.remove("barra_info")
    columns.insert(idx + 1, "barra_info")
    df = df[columns]
    return df

df = carregar_dados()

st.markdown('<h1 style="margin-bottom: -30px;margin-top: 20px;">Acompanhamento Geral Macaé</h1>', unsafe_allow_html=True)

tab_selecionada = st.radio(
    "Navegação",
    ["📋 Tabela", "🚨 Atrasos Por Área", "ℹ️ Avanço Geral"],
    horizontal=True,
    label_visibility="collapsed",
    key='main_tabs' 
)

if tab_selecionada == "📋 Tabela":
    if "selecao_tabela_macae" not in st.session_state:
        st.session_state.selecao_tabela_macae = None
    if "limpar_selecao_tabela_macae" not in st.session_state:
        st.session_state.limpar_selecao_tabela_macae = False

    limpar = st.session_state.limpar_selecao_tabela_macae
    
    colunas_para_remover = ["execucao", "terceiros"]
    df_tabela_geral = df.drop(columns=[col for col in colunas_para_remover if col in df.columns])
    linha_selecionada = show_table(df_tabela_geral, clear_selection=limpar)

    if limpar:
        st.session_state.limpar_selecao_tabela_macae = False

    if linha_selecionada == 0:
        st.session_state.selecao_tabela_macae = None
    elif linha_selecionada:
        st.session_state.selecao_tabela_macae = linha_selecionada

    selecao_valor = st.session_state.get("selecao_tabela_macae")

    if selecao_valor in ["0", "0.0"]:
        selecao_para_grafico = "Todos"
    else:
        selecao_para_grafico = selecao_valor if selecao_valor else "Todos"
    
    with st.spinner("Carregando gráfico, por favor aguarde..."):
        time.sleep(1)
        show_graph(df, str(selecao_para_grafico))

elif tab_selecionada == "🚨 Atrasos Por Área":
    show_tasks_graph(df)

elif tab_selecionada == "ℹ️ Avanço Geral":
    st.markdown("<h6 style='text-align: left;'>LEGENDA: ✅ Concluído /❕Possui Terceirizados / ❗ Não Iniciados Atrasados com Terceirizados / - Não Iniciados Internos</h3>", unsafe_allow_html=True)
    show_overall_table(df)