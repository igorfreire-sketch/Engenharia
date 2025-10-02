import streamlit as st
import plotly.express as px
import pandas as pd

def show_tasks_graphbar(df):
    st.subheader("🚨 Atrasos e Conclusões por Área Técnica")

    df["execucao"] = pd.to_numeric(df["execucao"], errors="coerce").fillna(-1).astype(int)
    df["responsavel 1"] = df["responsavel 1"].fillna("").str.strip()
    df["responsavel 2"] = df["responsavel 2"].fillna("").str.strip()

    df_atrasadas = df[df["execucao"] == 2]
    areas_atrasadas = pd.concat([
        df_atrasadas[["responsavel 1"]].rename(columns={"responsavel 1": "Área"}),
        df_atrasadas[["responsavel 2"]].rename(columns={"responsavel 2": "Área"})
    ])  

    contagem_atrasadas = areas_atrasadas[areas_atrasadas["Área"] != ""].value_counts().reset_index(name="Quantidade")
    contagem_atrasadas["Status"] = "Atrasadas"

    df_concluidas = df[df["execucao"] == 0]
    areas_concluidas = pd.concat([
        df_concluidas[["responsavel 1"]].rename(columns={"responsavel 1": "Área"}),
        df_concluidas[["responsavel 2"]].rename(columns={"responsavel 2": "Área"})
    ])

    contagem_concluidas = areas_concluidas[areas_concluidas["Área"] != ""].value_counts().reset_index(name="Quantidade")
    contagem_concluidas["Status"] = "Concluídas"

    df_comparativo = pd.concat([contagem_atrasadas, contagem_concluidas])

    fig = px.bar(
        df_comparativo,
        x="Área",
        y="Quantidade",
        color="Status",
        barmode="group",
        text="Quantidade",
        labels={"Área": "Área Técnica", "Quantidade": "Qtd.de Tarefas"},
        height=400,
        color_discrete_map={
            "Atrasadas": "#FF0000",
            "Concluídas": "#00ff13"
        }
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Área Técnica/Responsável",
        yaxis_title="Quantidade",
        bargap=0.2,
        margin=dict(t=10),
        legend_title_text="Status da Tarefa",
    )

    st.plotly_chart(fig, use_container_width=True)