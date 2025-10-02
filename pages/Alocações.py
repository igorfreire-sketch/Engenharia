import streamlit as st
import pandas as pd
import re
import os
from datetime import date
import io
import base64
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

from dotenv import load_dotenv
load_dotenv()

import altair as alt

import gspread
from google.oauth2.service_account import Credentials

from fpdf import FPDF
import matplotlib.pyplot as plt

from AlocacoesGeral.component_graph import bar_chart
from auth_session import protect_page

protect_page()
st.set_page_config(page_title="Dashboard de Alocação", page_icon="images/icone-quanta.png", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Estilos gerais e de botões */
    html, body, .stApp { padding-top: 0px !important; margin-top: 0px !important; }
    .block-container { padding-top: 0px !important; padding-bottom: 0px !important; }
    .main .block-container { padding: 1rem !important; }
    h1 { font-size: 1.8rem !important; }
    h2, h3 { font-size: 1.3rem !important; margin-bottom: 0px !important; }
    h4 { font-size: 1.1rem !important; }
    body, p, div, small { font-size: 0.85rem !important; line-height: 1.2; }
    .stMarkdown { margin-bottom: -15px !important; }
    
    button[data-testid="stBaseButton-primary"] { /* Botões principais (Enviar E-mail, Limpar) */
        background-color: #b21a19 !important; 
        border: 2px solid #b21a19 !important;
        color: white !important; 
        border-radius: 8px !important; padding: 5px !important;
        cursor: pointer !important;
    }

    button[data-testid="stBaseButton-tertiary"] { /* Botões de filtro de categoria */
        background-color: #f08224 !important; border: 2px solid #f08224 !important;
        color: white !important; border-radius: 8px !important; padding: 5px !important;
        cursor: pointer !important;
    }
    button[data-testid="stBaseButton-tertiary"]:active, 
    button[data-testid="stBaseButton-tertiary"]:focus,
    button[data-testid="stBaseButton-tertiary"][aria-pressed="true"] {
        background-color: transparent !important; 
        border: 2px solid #3c3c3b !important; 
        color: #c1c1c1 !important;
    }
    hr { margin-top: 0.5rem !important; margin-bottom: 0.5rem !important; }
</style>
""", unsafe_allow_html=True)

st.logo("images/logo-quanta-oficial.png", size="large")
st.markdown('<h1 style="margin-top: -60px">Alocações</h1>', unsafe_allow_html=True)

emojis = {
    "ESTRUTURA": "🏗️", "ORÇAMENTO": "💵", "HIDROSSANITÁRIO": "💧",
    "PCI/GÁS/AVAC": "🔧🔥", "ELÉTRICO/ENERGIA": "💡", "ENERGIA": "💡",
    "TERRAPLANAGEM": "🟫"
}

def clean_name(s):
    if pd.isna(s): return ""
    return re.sub(r'[^\w\sÀ-ÿ\-]', '', str(s).strip()).replace('_', ' ').strip()

def is_category_row(row, col_name):
    first = str(row[col_name]).strip()
    if not first: return False
    if first.upper() == first and len(first) > 1: return True
    other_cols = [c for c in row.index if c != col_name]
    if all(pd.isna(row[c]) for c in other_cols): return True
    return False

def to_percent(x):
    if pd.isna(x): return 0.0
    try: val = float(x)
    except (ValueError, TypeError): return 0.0
    return round(val * 100, 2) if -1 <= val <= 1 else round(val, 2)

def clean_percent_string(value):
    """Função específica para limpar strings de porcentagem como '100,00%' para o número 100.0"""
    if not isinstance(value, str):
        return 0.0
    try:
        numeric_value = float(value.replace('%', '').strip().replace(',', '.'))
        return numeric_value
    except (ValueError, TypeError):
        return 0.0
    
def remove_symbols(text):
    """Mantém apenas letras, números, acentos e espaços, removendo todos os outros símbolos e emojis."""
    if not isinstance(text, str):
        return text
    return re.sub(r'[^a-zA-Z0-9À-ÿ\s]', '', text)


@st.cache_data(ttl=600)
def load_and_transform(sheet_name="Trabalho"):
    try:
        creds_b64_str = os.environ.get("GOOGLE_CREDENTIALS_B64")
        google_sheet_id = os.environ.get("GOOGLE_SHEET_ID")

        if not creds_b64_str or not google_sheet_id:
            st.error("As variáveis de ambiente GOOGLE_CREDENTIALS_JSON e GOOGLE_SHEET_ID precisam ser configuradas.")
            return pd.DataFrame()

        creds_json_str = base64.b64decode(creds_b64_str).decode('utf-8')
        creds_dict = json.loads(creds_json_str)
        
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)

        spreadsheet = gc.open_by_key(google_sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        all_data = worksheet.get_all_values()

        if not all_data or len(all_data) < 3:
            st.warning("A planilha parece estar vazia ou não tem o formato esperado.")
            return pd.DataFrame()
            
        headers = all_data[1]
        data_rows = all_data[2:]
        df = pd.DataFrame(data_rows, columns=headers)
        
        df = df.loc[:, df.columns != '']
        
        if 'Profissional' in df.columns:
            df = df[df['Profissional'] != '']
        else:
            st.error("Coluna 'Profissional' não encontrada na planilha. Verifique o cabeçalho.")
            return pd.DataFrame()

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Erro: Planilha com ID '{google_sheet_id}' não encontrada. Verifique o ID e as permissões de compartilhamento.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao acessar o Google Sheets: {e}")
        return pd.DataFrame()
    
    column_mapping = {
        'DIsciplinas': 'Categoria', 'Profissional': 'Profissional', '🤖Total': 'TOTAL',
        'Marica': 'CODEMAR', 'Macae': 'SEMED', 'Diversos': 'DIVERSOS'
    }
    df.rename(columns=column_mapping, inplace=True)

    if 'Categoria' in df.columns:
        df['Categoria'] = df['Categoria'].apply(remove_symbols).str.strip()
    if 'Profissional' in df.columns:
        df['Profissional'] = df['Profissional'].apply(remove_symbols).str.strip()
    
    percent_columns = ['TOTAL', 'CODEMAR', 'SEMED', 'DIVERSOS']
    for col in percent_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_percent_string)
            
    final_columns = ['Categoria', 'Profissional', 'TOTAL', 'DIVERSOS', 'CODEMAR', 'SEMED']
    for col in final_columns:
        if col not in df.columns:
            df[col] = 0
            
    return df[final_columns]

def exibir_pessoa_card(pessoa_row):
    with st.container(border=True):
        st.markdown(f"<small><b>{pessoa_row['Profissional']}</b></small>", unsafe_allow_html=True)
        st.caption("TOTAL"); st.progress(int(pessoa_row["TOTAL"]), text=f"{int(pessoa_row['TOTAL'])}%")
        st.caption("DIVERSOS"); st.progress(int(pessoa_row["DIVERSOS"]), text=f"{int(pessoa_row['DIVERSOS'])}%")
        st.caption("CODEMAR"); st.progress(int(pessoa_row['CODEMAR']), text=f"{int(pessoa_row['CODEMAR'])}%")
        st.caption("SEMED"); st.progress(int(pessoa_row['SEMED']), text=f"{int(pessoa_row['SEMED'])}%")

def create_chart_image(df_media):
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df_media['Categoria'], df_media['TOTAL'], color='#f08224')
    ax.set_ylabel('Taxa de Ocupação (%)')
    ax.set_title('Taxa de Ocupação por Disciplina')
    ax.tick_params(axis='x', rotation=45)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}%', va='bottom', ha='center')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

@st.cache_data
def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Relatório de Alocação de Profissionais", 0, 1, "C")
    pdf.ln(5)
    data_emissao = date.today().strftime('%d/%m/%Y')
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Emitido em: {data_emissao}", 0, 1, "C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Profissionais por Disciplina", 0, 1, "L")
    pdf.ln(5)
    for categoria in sorted(df["Categoria"].unique()):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Disciplina: {categoria}", 0, 1, "L")
        profissionais_df = df[df["Categoria"] == categoria]
        pdf.set_font("Helvetica", "", 9)
        for _, row in profissionais_df.iterrows():
            linha_texto = f"  - {row['Profissional']} (CODEMAR: {int(row['CODEMAR'])}%, SEMED: {int(row['SEMED'])}%)"
            pdf.cell(0, 5, linha_texto, 0, 1, "L")
        pdf.ln(3)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Taxa de Ocupação por Disciplina", 0, 1, "C")
    pdf.ln(10)
    media_por_categoria = df.groupby('Categoria').apply(lambda x: ((x['TOTAL'] > 0).sum() / len(x)) * 100 if len(x) > 0 else 0).reset_index(name='TOTAL')
    chart_image = create_chart_image(media_por_categoria)
    pdf.image(chart_image, x=10, y=30, w=190)
    return bytes(pdf.output(dest='S'))

def send_email_with_attachment(subject, body, recipients, attachment_data, attachment_filename):
    """Envia um e-mail com anexo usando a API do SendGrid."""
    try:
        api_key = os.environ.get("SENDGRID_API_KEY")
        sender_email = os.environ.get("SENDER_EMAIL")

        if not all([api_key, sender_email]):
            st.error("SENDGRID_API_KEY e SENDER_EMAIL devem ser configurados no ambiente.")
            return False, []
        message = Mail(
            from_email=sender_email,
            to_emails=recipients,
            subject=subject,
            html_content=body.replace('\n', '<br>'))
        encoded_file = base64.b64encode(attachment_data).decode()
        attachedFile = Attachment(
            FileContent(encoded_file),
            FileName(attachment_filename),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        message.attachment = attachedFile
        sendgrid_client = SendGridAPIClient(api_key)
        response = sendgrid_client.send(message)        
        if response.status_code == 202:
            return True, recipients
        else:
            st.error(f"Erro ao enviar e-mail pelo SendGrid: {response.body}")
            return False, []
    except Exception as e:
        st.error(f"Erro ao conectar com o SendGrid: {e}")
        return False, []
    
def display_occupancy_chart(df):
    """Calcula e exibe o gráfico de Taxa de Ocupação de forma interativa usando Altair."""
    st.subheader("Ocupação por Disciplina")

    chart_data = df.groupby('Categoria').apply(
        lambda x: ((x['TOTAL'] > 0).sum() / len(x)) if len(x) > 0 else 0
    ).reset_index(name='Taxa de Ocupação')

    bars = alt.Chart(chart_data).mark_bar(
        size=60,
        color='#f08224'
    ).encode(
        x=alt.X('Categoria:N', sort=None, title='Disciplina', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Taxa de Ocupação:Q', title='Taxa de Ocupação (%)', axis=alt.Axis(format='%')) # format='%' agora funciona corretamente
    )

    text = bars.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        fontSize=12,
        color='white'
    ).encode(
        text=alt.Text('Taxa de Ocupação:Q', format='.1%')
    )

    final_chart = (bars + text).properties(
        width=700,
        height=400
    )

    st.altair_chart(final_chart, use_container_width=True)


df_transf = load_and_transform()

if not df_transf.empty:
    cats = [str(c) for c in df_transf["Categoria"].unique() if pd.notna(c)]
    if 'filtro_ativo' not in st.session_state:
        st.session_state.filtro_ativo = None
    def set_filtro(categoria): st.session_state.filtro_ativo = categoria
    def clear_filtro(): st.session_state.filtro_ativo = None

    cols_botoes_filtro = st.columns(len(cats))
    for i, cat in enumerate(cats):
        cols_botoes_filtro[i].button(cat, on_click=set_filtro, args=(cat,), use_container_width=True, type="tertiary")

    st.markdown("---")
    st.subheader("Relatórios e Notificações")

    recipients_str = os.environ.get("MASTER_EMAIL_LIST", "")
    master_email_list = [email.strip() for email in recipients_str.split(',') if email.strip()]

    selected_emails = st.multiselect("Selecione os destinatários do relatório:", options=master_email_list, default=master_email_list)

    cols_botoes_acao = st.columns(3)
    pdf_data = generate_pdf_report(df_transf)
    nome_arquivo_pdf = f"relatorio_alocacao_{date.today().strftime('%Y_%m_%d')}.pdf"

    with cols_botoes_acao[0]:
        st.download_button(label="📄 Baixar PDF", data=pdf_data, file_name=nome_arquivo_pdf, mime="application/pdf", use_container_width=True, type="secondary")

    with cols_botoes_acao[1]:
        if st.button("📧 Enviar Relatório Por E-mail", use_container_width=True, type="primary"):
            if not selected_emails:
                st.warning("Nenhum destinatário selecionado. Por favor, selecione ao menos um e-mail.")
            else:
                with st.spinner(f"Enviando relatório para {len(selected_emails)} destinatário(s)..."):
                    data_hoje = date.today().strftime('%d/%m/%Y')
                    email_subject = f"Relatório de Alocação de Profissionais - {data_hoje}"
                    email_body = f"Olá,\n\nSegue em anexo o relatório de alocação de profissionais gerado em {data_hoje}.\n\nAtenciosamente,\nQuanta Sudeste"
                    success, recipients_sent_to = send_email_with_attachment(subject=email_subject, body=email_body, recipients=selected_emails, attachment_data=pdf_data, attachment_filename=nome_arquivo_pdf)
                    if success:
                        st.success(f"E-mail enviado com sucesso para: {', '.join(recipients_sent_to)}")

    with cols_botoes_acao[2]:
        if st.button("Limpar Filtro", use_container_width=True, type="primary"):
            clear_filtro()

    st.markdown("---")

    filtro_selecionado = st.session_state.filtro_ativo
    if filtro_selecionado:
        emoji = emojis.get(filtro_selecionado, '👥')
        st.subheader(f"{emoji} Profissionais em: {filtro_selecionado}")
        grupo_filtrado = df_transf[df_transf["Categoria"] == filtro_selecionado].copy()
        professional_order = df_transf['Profissional'].tolist()
        grupo_filtrado['Profissional'] = pd.Categorical(grupo_filtrado['Profissional'], categories=professional_order, ordered=True)
        grupo_filtrado = grupo_filtrado.sort_values('Profissional')
        with st.container(border=True):
            with st.container(height=630):
                cols_grid = st.columns(4)
                for index, pessoa_row in grupo_filtrado.iterrows():
                    col = cols_grid[index % 4]
                    with col:
                        exibir_pessoa_card(pessoa_row)
    else:
        df_tabela = df_transf.copy()
        df_tabela['CALC_TOTAL'] = df_tabela['DIVERSOS'] + df_tabela['CODEMAR'] + df_tabela['SEMED']
        num_colunas_grid = 3
        cols_grid = st.columns(num_colunas_grid)
        for i, cat in enumerate(cats):
            col = cols_grid[i % num_colunas_grid]
            with col:
                with st.container(border=True):
                    emoji = emojis.get(cat, '👥')
                    st.markdown(f"**{emoji} {cat}**")
                    st.markdown(f"<small>❌ Ocupado | ⭕ Disponível | ✅ Em dia | ⚠️ Atrasos</small>", unsafe_allow_html=True)
                    st.divider()
                    with st.container(height=230):
                        col_layout = [1, 1, 2.5, 1.5, 1, 1.5]
                        header_cols = st.columns(col_layout)
                        header_cols[0].markdown('<div style="text-align: center;"><strong>Status</strong></div>', unsafe_allow_html=True)
                        header_cols[1].markdown('<div style="text-align: center;"><strong>Total</strong></div>', unsafe_allow_html=True)
                        header_cols[2].markdown('<div style="text-align: center;"><strong>Profissional</strong></div>', unsafe_allow_html=True)
                        header_cols[3].markdown('<div style="text-align: center;"><strong>CODEMAR</strong></div>', unsafe_allow_html=True)
                        header_cols[4].markdown('<div style="text-align: center;"><strong>SEMED</strong></div>', unsafe_allow_html=True)
                        header_cols[5].markdown('<div style="text-align: center;"><strong>DIVERSOS</strong></div>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        grupo = df_tabela[df_tabela["Categoria"] == cat]
                        for _, pessoa_row in grupo.iterrows():
                            row_cols = st.columns(col_layout)
                            total = int(pessoa_row['CALC_TOTAL'])
                            progresso = "✅" if total == 100 else "⚠️"
                            status = "⭕" if total == 0 else "❌"
                            row_cols[0].markdown(f"{status}{progresso}")
                            row_cols[1].markdown(f"{int(pessoa_row['TOTAL'])}%")
                            if total == 0:
                                nome_html = f"<div style='font-weight: bold; background-color: #ffe2e2; color: black; padding: 2px; border-radius: 2px; text-align: center'>{pessoa_row['Profissional']}</div>"
                                row_cols[2].markdown(nome_html, unsafe_allow_html=True)
                            else:
                                nome_html = f"<div style='text-align: center'>{pessoa_row['Profissional']}</div>"
                                row_cols[2].markdown(nome_html, unsafe_allow_html=True)
                            row_cols[3].markdown(f'<div style="text-align: center;">{int(pessoa_row["CODEMAR"])}%</div>', unsafe_allow_html=True)
                            row_cols[4].markdown(f'<div style="text-align: center;">{int(pessoa_row["SEMED"])}%</div>', unsafe_allow_html=True)
                            row_cols[5].markdown(f'<div style="text-align: center;">{int(pessoa_row["DIVERSOS"])}%</div>', unsafe_allow_html=True)
    st.divider()
    display_occupancy_chart(df_transf)
    #bar_chart(df_transf)
else:
    st.warning("Nenhum dado para exibir. Verifique se o arquivo da planilha existe e não está vazio.")