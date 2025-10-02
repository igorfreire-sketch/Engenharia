import streamlit as st
import pandas as pd
from marica.component_table import show_table
from marica.component_graphbar import show_graph
from marica.component_graphbar_tasks import show_tasks_graphbar
from auth_session import protect_page

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
            
        #acompanhamento-geral-marica {
            margin-top: -40px !important; /* Ajuste o valor conforme necessário */

        }
            
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
    </style>
""", unsafe_allow_html=True)

df = pd.read_excel("data/013A.xlsx")

df = df[[
    "D - N° Guia", "E - Nome Da Tarefa", "G - Inicio","H - Conclusão",
    "% Ideal", "C - % Concluída",
    "K - Responsável", "L - Recurso", "B - Status", 
    "Q - Equipe"
]].copy()

df.columns = [
    "hierarquia", "tarefa", "inicio","conclusao", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "execucao", "equipe"
]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df['inicio'] = df['inicio'].apply(lambda x: x.split(' ')[1] if ' ' in x else x)
df['conclusao'] = df['conclusao'].apply(lambda x: x.split(' ')[1] if ' ' in x else x)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))
df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))

colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info") 
colunas.insert(idx + 1, "barra_info")
df = df[colunas]

st.set_page_config(page_title="Dashboard Maricá", page_icon="images/icone-quanta.png",layout="wide", initial_sidebar_state="collapsed")
st.logo("images/logo-quanta-oficial.png", size="large")

st.markdown('<h1 style="margin-bottom: -30px;margin-top: 20px;">Acompanhamento Geral Maricá</h1>', unsafe_allow_html=True)

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

tab_selecionada = st.radio(
    "Navegação",
    ["📋 Tabela", "🚨 Atrasos Por Área"],
    horizontal=True,
    label_visibility="collapsed",
    key='main_tabs' 
)

if tab_selecionada == '📋 Tabela':
    if "selecao_tabela_marica" not in st.session_state:
        st.session_state.selecao_tabela_marica = None
    if "limpar_selecao_tabela_marica" not in st.session_state:
        st.session_state.limpar_selecao_tabela_marica = False

    limpar = st.session_state.limpar_selecao_tabela_marica
    linha_selecionada = show_table(df.drop(columns=["execucao"]), limpar_selecao=limpar)

    if limpar:
        st.session_state.limpar_selecao_tabela_marica = False

    if linha_selecionada == 0:
        st.session_state.selecao_tabela_marica = None
    elif linha_selecionada:
        st.session_state.selecao_tabela_marica = linha_selecionada

    selecao_valor = st.session_state.get("selecao_tabela_marica")
    selecao_valor = selecao_valor if selecao_valor else "Todos"
    show_graph(df, str(selecao_valor))

if tab_selecionada == '🚨 Atrasos Por Área':
    show_tasks_graphbar(df) 

#with aba_geral:
#    mostrar_tabela_projetos_especificos_aggrid_marica(df)