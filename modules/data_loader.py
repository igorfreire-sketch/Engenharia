import streamlit as st
import pandas as pd
import gspread
import os
import json
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

@st.cache_data(ttl=600)
def load_data_from_sheets():
    try:
        creds_info = None
        is_production = os.getenv('RENDER') == 'true'

        if is_production:
            creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if not creds_json_str:
                st.error("Erro em produção: A variável de ambiente 'GOOGLE_CREDENTIALS_JSON' não foi encontrada.")
                return pd.DataFrame()
            try:
                creds_info = json.loads(creds_json_str)
            except json.JSONDecodeError:
                st.error("Erro em produção: Falha ao decodificar o JSON das credenciais.")
                return pd.DataFrame()
        else:
            # st.info("Rodando em ambiente de desenvolvimento (Local).") # Removido para interface mais limpa
            creds_path = os.getenv("GCP_CREDENTIALS_PATH")
            if not creds_path or not os.path.exists(creds_path):
                st.error(f"Erro de desenvolvimento: Verifique a variável 'GCP_CREDENTIALS_PATH' no .env e o caminho do arquivo.")
                return pd.DataFrame()
            with open(creds_path) as f:
                creds_info = json.load(f)

        if not creds_info:
            st.error("Não foi possível carregar as credenciais do Google.")
            return pd.DataFrame()

        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        gc = gspread.authorize(creds)

        spreadsheet_ids_str = os.getenv("CONFORMIDADES_SHEET_IDS")
        if not spreadsheet_ids_str:
            st.error("Variável CONFORMIDADES_SHEET_IDS não encontrada no .env.")
            return pd.DataFrame()
        
        spreadsheet_ids = [id.strip() for id in spreadsheet_ids_str.split(',')]
        all_dataframes = []

        for sheet_id in spreadsheet_ids:
            try:
                spreadsheet = gc.open_by_key(sheet_id)
            except gspread.exceptions.SpreadsheetNotFound:
                st.warning(f"Planilha com ID '{sheet_id}' não encontrada ou compartilhada."); continue

            for worksheet in spreadsheet.worksheets():
                os_name = worksheet.title
                data = worksheet.get_all_values()
                
                if len(data) > 1:
                    # LÓGICA DE LEITURA SIMPLIFICADA PARA A NOVA PLANILHA
                    headers = data[0]
                    cleaned_headers = [h.strip() for h in headers]
                    df_page = pd.DataFrame(data[1:], columns=cleaned_headers)

                    # Converte todas as colunas numéricas para o tipo correto
                    numeric_cols = [
                        "Quantivo Revisado pela Eficiência", "Quantivo Revisado pelo Setor / Contratado",
                        "Total Revisado pela Eficiência", "Total Revisado pelo Setor / Contratado",
                        "Total sem não conformidades", "Total Analisado"
                    ]
                    for col in numeric_cols:
                        if col in df_page.columns:
                            df_page[col] = pd.to_numeric(df_page[col], errors='coerce').fillna(0)
            
                    df_page['OS'] = os_name
                    df_page['Planilha_Origem_ID'] = sheet_id
                    all_dataframes.append(df_page)

        if not all_dataframes:
            st.warning("Nenhum dado foi processado."); return pd.DataFrame()

        consolidated_df = pd.concat(all_dataframes, ignore_index=True)
        # Remove linhas onde a coluna 'Disciplina' está vazia
        consolidated_df.dropna(subset=['Disciplinas'], inplace=True)
        consolidated_df = consolidated_df[consolidated_df['Disciplinas'] != '']
        
        return consolidated_df

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os dados: {e}"); return pd.DataFrame()