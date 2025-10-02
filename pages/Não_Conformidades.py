import streamlit as st
import pandas as pd
import html
import plotly.express as px
from modules.data_loader import load_data_from_sheets
from collections import defaultdict
from auth_session import protect_page
import plotly.graph_objects as go

protect_page()

st.set_page_config(
    page_title="Dashboard de Conformidades",
    page_icon="images/icone-quanta.png",
    layout="wide"
)

PALETA_CORES = [
    "#8e44ad", "#e67e22", "#2980b9", "#c0392b", 
    "#27ae60", "#16a085", "#f1c40f", "#d35400",
    "#34495e", "#7f8c8d" 
]

if 'filtro_alteracao_ativo' not in st.session_state:
    st.session_state['filtro_alteracao_ativo'] = None

st.logo("images/logo-quanta-oficial.png", size="large")
st.markdown('<h3 style="margin-top: -80px">Não Conformidades</h3>', unsafe_allow_html=True)

df_conformidades = load_data_from_sheets()

main_filter_col1, main_filter_col2 = st.columns(2, gap="large")

with main_filter_col1:
    st.write("**Filtros Gerais**")
    b1, b2 = st.columns(2)
    b1.button("Macaé", use_container_width=True, type="primary")
    b2.button("Maricá", use_container_width=True, type="primary")
    
    if not df_conformidades.empty:
        lista_os = sorted(df_conformidades['OS'].dropna().unique())
        contrato_selecionado = st.selectbox(
            "Filtrar por OS...", options=lista_os, index=None, placeholder="Selecione uma OS...", label_visibility="collapsed"
        )

with main_filter_col2:
    st.write("**Filtrar por Tipo de Alteração:**")
    COLUNA_ALTERACAO_INTERNO = "Alteração Feita pela Conformidade"
    COLUNA_ALTERACAO_EXTERNO = "Ateração Enviado ao Setor / Contratado"
    
    if not df_conformidades.empty and COLUNA_ALTERACAO_INTERNO in df_conformidades.columns:
        opcoes_filtro = ["Carimbo", "Desenho", "Falta de Arquivo", "Relatório"]
        opcoes_filtro.sort()

        def handle_filter_click(opcao):
            if st.session_state.get('filtro_alteracao_ativo') == opcao:
                st.session_state['filtro_alteracao_ativo'] = None  
            else:
                st.session_state['filtro_alteracao_ativo'] = opcao 
            st.rerun()

        f1_col1, f1_col2 = st.columns(2)
        with f1_col1:
            if st.button(opcoes_filtro[0], key="btn_alt_0", use_container_width=True, type="primary"): handle_filter_click(opcoes_filtro[0])
        with f1_col2:
            if st.button(opcoes_filtro[1], key="btn_alt_1", use_container_width=True, type="primary"): handle_filter_click(opcoes_filtro[1])
        
        f2_col1, f2_col2 = st.columns(2)
        with f2_col1:
            if st.button(opcoes_filtro[2], key="btn_alt_2", use_container_width=True, type="primary"): handle_filter_click(opcoes_filtro[2])
        with f2_col2:
            if st.button(opcoes_filtro[3], key="btn_alt_3", use_container_width=True, type="primary"): handle_filter_click(opcoes_filtro[3])
        
        if st.button("Limpar Filtro ❌", use_container_width=True, type="secondary"):
            st.session_state['filtro_alteracao_ativo'] = None
            st.rerun()
    else:
        st.caption("Aguardando dados para carregar filtros...")

st.markdown("---")

df_visualizacao = df_conformidades.copy()
filtro_ativo = st.session_state.get('filtro_alteracao_ativo')
if filtro_ativo:
    mask_interno = df_visualizacao[COLUNA_ALTERACAO_INTERNO].str.contains(filtro_ativo, na=False)
    mask_externo = df_visualizacao[COLUNA_ALTERACAO_EXTERNO].str.contains(filtro_ativo, na=False)
    df_visualizacao = df_conformidades[mask_interno | mask_externo]
    #st.info(f"Filtro ativo: **{filtro_ativo}**. Mostrando {len(df_visualizacao)} de {len(df_conformidades)} registros.")

COLUNA_DISCIPLINA = "Disciplinas"
COLUNA_TOTAL_INTERNO = "Total Revisado pela Eficiência"
COLUNA_TOTAL_EXTERNO = "Total Revisado pelo Setor / Contratado"
COLUNA_VALORES_INTERNO = "Quantivo Revisado pela Eficiência"
COLUNA_VALORES_EXTERNO = "Quantivo Revisado pelo Setor / Contratado"

df_grafico_disciplinas = pd.DataFrame()
totais_para_lista_lateral = pd.Series(dtype='float64')
df_grafico_grupo = pd.DataFrame()

if not df_visualizacao.empty:
    totais_internos = df_visualizacao.groupby(COLUNA_DISCIPLINA)[COLUNA_TOTAL_INTERNO].sum()
    totais_externos = df_visualizacao.groupby(COLUNA_DISCIPLINA)[COLUNA_TOTAL_EXTERNO].sum()
    
    df_internos_final = totais_internos.reset_index(); df_internos_final.columns = ['Disciplinas', 'Valor']; df_internos_final['Tipo'] = 'Interno'
    df_externos_final = totais_externos.reset_index(); df_externos_final.columns = ['Disciplinas', 'Valor']; df_externos_final['Tipo'] = 'Terceirizado'
    df_grafico_disciplinas = pd.concat([df_internos_final, df_externos_final], ignore_index=True)
    
    if not df_grafico_disciplinas.empty:
        totais_para_lista_lateral = df_grafico_disciplinas.groupby(COLUNA_DISCIPLINA)['Valor'].sum()

    soma_por_tipo_interno = defaultdict(float)
    soma_por_tipo_externo = defaultdict(float)

    for _, row in df_visualizacao.iterrows():
        tipos_str = str(row[COLUNA_ALTERACAO_INTERNO] or '') + '/' + str(row[COLUNA_ALTERACAO_EXTERNO] or '')
        
        valor_interno = row[COLUNA_VALORES_INTERNO]
        valor_externo = row[COLUNA_VALORES_EXTERNO]

        if not tipos_str.strip('/') and (valor_interno + valor_externo) == 0:
            continue

        if valor_interno > 0:
            partes = [p.strip() for p in tipos_str.split('/') if p.strip()]
            for parte in partes:
                soma_por_tipo_interno[parte] += valor_interno

        if valor_externo > 0:
            partes = [p.strip() for p in tipos_str.split('/') if p.strip()]
            for parte in partes:
                soma_por_tipo_externo[parte] += valor_externo

    df_internos_grupo = pd.DataFrame(list(soma_por_tipo_interno.items()), columns=['Grupo', 'Soma']); df_internos_grupo['Tipo'] = 'Interno'
    df_externos_grupo = pd.DataFrame(list(soma_por_tipo_externo.items()), columns=['Grupo', 'Soma']); df_externos_grupo['Tipo'] = 'Terceirizado'
    df_grafico_grupo = pd.concat([df_internos_grupo, df_externos_grupo], ignore_index=True)


custom_css = """
<style>
    .scrollable-container { max-height: 1100px; overflow-y: auto; padding-right: 15px; }
    .discipline-card { padding: 8px 12px; margin-bottom: 8px; border-radius: 8px; color: white; font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .discipline-value { background-color: rgba(255, 255, 255, 0.25); padding: 4px 10px; border-radius: 20px; font-size: 12px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

col_disciplinas, col_graficos = st.columns([1, 4], gap="large")

if not df_visualizacao.empty:
    with col_disciplinas:
        st.write("**Não Conformidades por Disciplina**")
        todas_disciplinas_visiveis = sorted(df_visualizacao['Disciplinas'].dropna().unique())
        mapa_cores_disciplinas = {d: PALETA_CORES[i % len(PALETA_CORES)] for i, d in enumerate(todas_disciplinas_visiveis)}
        
        lista_html_cards = []
        for disciplina in todas_disciplinas_visiveis:
            total = totais_para_lista_lateral.get(disciplina, 0)
            cor = mapa_cores_disciplinas.get(disciplina, "#808080")
            card_html = (
                f'<div class="discipline-card" style="background-color: {cor};">'
                f'<span>{html.escape(disciplina)}</span>'
                #f'<span class="discipline-value">{int(total)}</span>'
                f'</div>'
            )
            lista_html_cards.append(card_html)
        
        todos_os_cards = "".join(lista_html_cards)
        html_final = f'<div class="scrollable-container">{todos_os_cards}</div>'
        st.markdown(html_final, unsafe_allow_html=True)
    
    with col_graficos:
        with st.container(border=True):
            st.subheader("Conformidade por disciplinas")
            if not df_grafico_disciplinas.empty:
                ordem_barras = totais_para_lista_lateral.sort_values(ascending=False).index
                fig = px.bar(
                    df_grafico_disciplinas, x='Disciplinas', y='Valor', color='Tipo',
                    labels={'Valor': 'Total Não Conformidades', 'Tipo': 'Origem'},
                    template='plotly_dark', color_discrete_map={'Interno': '#1ABC9C', 'Terceirizado': '#F1C40F'}
                )
                fig.update_layout(
                    yaxis_title=None, xaxis_title=None, xaxis_rangeslider_visible=True,
                    xaxis={'categoryorder':'array', 'categoryarray': ordem_barras},
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não foram encontrados totais nas colunas de totais.")

        st.write("") 

        linha2_col1, linha2_col2 = st.columns(2, gap="large")

        with linha2_col1:
            with st.container(border=True):
                st.subheader("Grupo de conformidade")
                if not df_grafico_grupo.empty:
                    fig_grupo = px.bar(
                        df_grafico_grupo, x='Grupo', y='Soma', color='Tipo', barmode='group', text_auto=True,
                        labels={'Grupo': '<b>Grupo de Alteração</b>', 'Soma': '<b>Soma de Não Conformidades</b>', 'Tipo': '<b>Origem</b>'},
                        template='plotly_dark', color_discrete_map={'Interno': '#ff25d4', 'Terceirizado': '#40baff'}
                    )
                    fig_grupo.update_layout(yaxis_title=None, xaxis_title=None)
                    
                    if filtro_ativo:
                        try:
                            valor_max = df_grafico_grupo[df_grafico_grupo['Grupo'] == filtro_ativo]['Soma'].max()
                            fig_grupo.add_annotation(
                                x=filtro_ativo,
                                y=valor_max,
                                text="Filtro Ativo",
                                showarrow=True,
                                arrowhead=2,
                                bordercolor="#c7c7c7",
                                borderwidth=2,
                                borderpad=4,
                                bgcolor="#ff7f0e",
                                opacity=0.8,
                                ax=0,
                                ay=-50 
                            )
                        except (ValueError, KeyError):
                            pass
                    
                    st.plotly_chart(fig_grupo, use_container_width=True)
                else:
                    st.info("Nenhuma alteração encontrada nos dados selecionados.")

        with linha2_col2:
            with st.container(border=True):
                st.subheader("Total de Não Conformidades")
                total_interno_geral = totais_internos.sum()
                total_externo_geral = totais_externos.sum()
                total_geral = total_interno_geral + total_externo_geral
                
                df_rosca = pd.DataFrame({'Tipo': ['Interno', 'Terceirizado'], 'Total': [total_interno_geral, total_externo_geral]})
                if df_rosca['Total'].sum() > 0:
                    fig_rosca = px.pie(
                        df_rosca, names='Tipo', values='Total', hole=0.6, template='plotly_dark',
                        color_discrete_map={'Interno': '#1ABC9C', 'Terceirizado': '#F1C40F'}
                    )
                    fig_rosca.update_traces(textinfo='percent+label', textposition='outside')
                    fig_rosca.update_layout(showlegend=False, annotations=[dict(text=f'{int(total_geral)}', x=0.5, y=0.5, font_size=30, showarrow=False)])
                    st.plotly_chart(fig_rosca, use_container_width=True)
                else:
                    st.info("Não há valores de não conformidade para exibir.")
else:
    st.info("Nenhum dado para exibir. Verifique os filtros ou a fonte de dados.")