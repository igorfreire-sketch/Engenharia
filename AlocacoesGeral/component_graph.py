import streamlit as st
import plotly.express as px
import pandas as pd

def bar_chart(df):
    st.subheader("Percentual Médio de Avanço por Área (CODEMAR vs SEMED)")

    if df.empty or 'CODEMAR' not in df.columns or 'SEMED' not in df.columns:
        st.warning("Dados insuficientes para gerar o gráfico comparativo.")
        return
    category_order = df['Categoria'].unique().tolist()

    grouped_avg = df.groupby(df["Categoria"].fillna("Sem Categoria"))[['CODEMAR', 'SEMED']].mean().reset_index()

    df_long = pd.melt(grouped_avg,
                    id_vars='Categoria',
                    value_vars=['CODEMAR', 'SEMED'],
                    var_name='Fonte de Alocação',
                    value_name='Percentual Médio')
    
    fig = px.bar(
        df_long,
        x="Categoria",
        y="Percentual Médio",
        color="Fonte de Alocação",
        barmode='group',
        color_discrete_map={"CODEMAR": "#f08224", "SEMED": "#3c3c3b"},
        text_auto=True,
    )

    fig.update_xaxes(categoryorder='array', categoryarray=category_order)

    fig.update_traces(texttemplate='%{y:.0f}%', textposition='outside')
    
    fig.update_layout(
        yaxis_title="",
        xaxis_title="Área",
        legend_title="Fonte",
        margin=dict(t=50, b=50),
        bargap=0.6,
        yaxis=dict(range=[0, 100])
    )

    st.plotly_chart(fig, use_container_width=True)