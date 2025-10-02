import streamlit as st
import plotly.express as px
import textwrap

def show_graph(df, selection_value):
    df = df.copy()
    df['hierarquia'] = df['hierarquia'].astype(str).str.strip()
    df['nivel'] = df['hierarquia'].apply(lambda x: x.count('.') + 1)

    if selection_value == "Todos":
        df_plot = df[df['hierarquia'].str.count(r'\.') == 0].copy()
    else:
        current_level = str(selection_value).count('.') + 1
        next_level = current_level + 1
        df_plot = df[
            (df['hierarquia'] == selection_value) |
            ((df['hierarquia'].str.startswith(selection_value + '.')) & (df['hierarquia'].str.count(r'\.') + 1 == next_level))
        ].copy()
    
    if df_plot['previsto'].max() <= 1:
        df_plot['previsto'] *= 100
    if df_plot['concluido'].max() <= 1:
        df_plot['concluido'] *= 100
    
    st.markdown('<h3 style="margin-bottom: -50px;margin-top: -10px;">Comparativo de Projetos</h3>', unsafe_allow_html=True)

    if df_plot.empty:
        st.info("Nenhum subtópico encontrado para esse item")
        return
    
    altura_por_item = 10
    altura_total = max(230, len(df_plot) * altura_por_item)
    
    max_chars = 25

    def abreviar_nome(nome, max_chars):
        if len(nome) > max_chars:
            return nome[:max_chars - 3] + "..."
        return nome
        
    df_plot["tarefa_curta"] = df_plot["tarefa"].apply(lambda x: abreviar_nome(x, max_chars))

    df_plot["tarefa_curta"] = df_plot["tarefa_curta"].apply(lambda x: "<br>".join(textwrap.wrap(x, 15)))

    fig = px.bar(
        df_plot, x="tarefa_curta", y=["previsto", "concluido"],
        labels={"value": "Percentual", "variable": "Tipo"},
        hover_data={"tarefa": True, "tarefa_curta": False},
        barmode="group", height=altura_total,
        color_discrete_map={"previsto": "#f08224", "concluido": "#3c3c3b"}
    )

    fig.update_layout(
        yaxis=dict(range=[0,100], tickformat=".0f", title="Percentual (%)"),
        xaxis_title="Tarefa", legend_title="", bargap=0.8,margin=dict(b=2)
    )

    fig.update_xaxes(tickangle=0, tickfont=dict(size=11))

    with st.container():
        st.markdown("""
            <div style="padding: 2px;">
        """, unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)