from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd

def show_table(df_original):
    df = df_original.copy()

    colunas = list(df.columns)
    df = df[colunas]

    if 'numero contrato' in df.columns:
        df['numero contrato'] = df['numero contrato'].astype(str).replace('nan', '')

    df['inicio'] = pd.to_datetime(df['inicio'], errors='coerce')
    df['termino'] = pd.to_datetime(df['termino'], errors='coerce')
    df['inicio'] = df['inicio'].apply(lambda x: x.strftime('%d/%m/%y') if pd.notna(x) else '')
    df['termino'] = df['termino'].apply(lambda x: x.strftime('%d/%m/%y') if pd.notna(x) else '')
    df['barra_info'] = df['percentual']

    task_responsible_renderer_jscode = JsCode("""
        function(params) {
            // Verifica se os dados da linha e o status existem para evitar erros
            if (!params.data || !params.data.status) {
                return params.value; // Retorna o valor original se não houver status
            }

            // Pega o valor original da célula (o nome do responsável)
            const originalValue = params.value;
            // Pega o valor da coluna 'status' da mesma linha e normaliza
            const status = params.data.status.toLowerCase();

            // Se o status for "em andamento com atraso", adiciona o emoji na frente do nome
            if (status === 'em andamento com atraso') {
                return '🟠 ' + originalValue;
            } else if (status === 'concluído') {
                return '🟢 ' + originalValue;
            } else if (status === 'standby') {
                return '🔵 ' + originalValue;
            } else if (status === 'em andamento') {
                return '🔃 ' + originalValue;
            }
            
            // Caso contrário, apenas retorna o nome original
            return originalValue;
        }
    """)

    percentage_formatter = JsCode("""
        function(params) {
            if (params.value === null || params.value === undefined || params.value === '') {
                return ''; // Retorna vazio se não houver valor
            }
            // Formata o número como porcentagem
            return (params.value * 100).toFixed(0) + '%';
        }
    """)

    status_style_jscode = JsCode("""
        function(params) {
            // Estilo base para garantir o alinhamento central em todas as células
            var style = { 'textAlign': 'center' };
            
            if (params.value == null || params.value === '') { // == null checa por null e undefined
                style.backgroundColor = '#6c757d'; // Cinza Escuro para 'sem informação'
                style.color = 'white';
                return style;
            }
                                 
            var status = String(params.value).toLowerCase();

            if (status === 'standby') {
                style.backgroundColor = '#007bff'; // Azul
                style.color = 'white';
            } else if (status === 'concluído') {
                style.backgroundColor = '#28a745'; // Verde
                style.color = 'white';
            } else if (status === 'em andamento') {
                style.backgroundColor = '#add8e6'; // Azul Claro
                style.color = 'black';
            } else if (status === 'não iniciado') {
                // Fundo transparente com texto branco 
                style.backgroundColor = 'transparent'; 
                style.color = 'white';
            } else if (status === 'em andamento com atraso') {
                style.backgroundColor = '#ffc107'; // Laranja/Âmbar
                style.color = 'black';
            } else if (status === 'sem informação') {
                style.backgroundColor = '#6c757d'; // Cinza Escuro
                style.color = 'white';
            }
            
            return style;
        }
    """)

    barra_progress_renderer = JsCode("""
    function(params) {
        let data;
        try {
            data = JSON.parse(params.value);
        } catch {
            data = { percentual: 0 };
        }

        const concluido = params.data.percentual * 100 || 0;

        if (concluido >= 100) {
            params.eGridCell.innerHTML = `
                <div style="text-align: center; font-weight: bold; color: #2ebe00; margin-top: 2px;">
                    Finalizado ✅
                </div>
            `;
            return;
        }

        let color = '#7f9bff';

        const width = Math.min(Math.max(concluido, 0), 100);

        params.eGridCell.innerHTML = `
            <div style="width: 100%; background-color: #ddd; border-radius: 5px; height: 16px; margin-top: 5px;">
                <div style="width: ${width}%; background-color: ${color}; height: 16px; border-radius: 5px;"></div>
            </div>
        `;
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df)

    #gb.configure_column("indice", header_name="Índice", cellStyle={"textAlign": "center"}, minWidth=100,maxWidth=120)
    gb.configure_column("responsavel", header_name="Responsável", cellStyle={"textAlign": "center"}, minWidth=130,maxWidth=140)
    gb.configure_column("contrato", header_name="Contrato", cellStyle={"textAlign": "center"}, minWidth=250,maxWidth=260)
    gb.configure_column("numero contrato", header_name="N° Contrato", cellStyle={"textAlign": "center"}, minWidth=120,maxWidth=140)
    #gb.configure_column("tipo do contrato", header_name="Tipo do Contrato", cellStyle={"textAlign": "center"}, minWidth=160, maxWidth=210)
    gb.configure_column("responsavel do produto", header_name="Responsável Produto", cellStyle={"textAlign": "center"}, minWidth=185,maxWidth=187)
    gb.configure_column("responsavel da tarefa", header_name="Responsável Tarefa", cellStyle={"textAlign": "center"}, minWidth=200,maxWidth=201,cellRenderer=task_responsible_renderer_jscode )
    gb.configure_column("funcao", header_name="Função", cellStyle={"textAlign": "center"}, minWidth=160,maxWidth=165)
    gb.configure_column("equipe terceirizada", header_name="Equipe Terceirizada", cellStyle={"textAlign": "center"}, minWidth=150, maxWidth=165)
    gb.configure_column("status", header_name="Status", cellStyle=status_style_jscode, minWidth=100, maxWidth=140)
    #gb.configure_column("detalhamento do status", header_name="Detalhamento Status", cellStyle={"textAlign": "center"}, minWidth=200,maxWidth=250)
    gb.configure_column("inicio", header_name="Início", cellStyle={"textAlign": "center"}, minWidth=80, maxWidth=100)
    gb.configure_column("termino", header_name="Término", cellStyle={"textAlign": "center"}, minWidth=80, maxWidth=100)
    gb.configure_column("percentual", header_name="Total", cellStyle={"textAlign": "center"}, minWidth=90, maxWidth=92,valueFormatter=percentage_formatter)
    gb.configure_column("barra_info", header_name="Progresso", cellRenderer=barra_progress_renderer,  minWidth=90, maxWidth=130)

    AgGrid(
        df,
        gridOptions=gb.build(),
        height=700,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        enable_row_selection=True,
        return_df=True,
        custom_css={
            ".ag-cell": {
                "font-size": "12px",
                "font-weight": "600",
                "line-height": "22px",
                "font-family": "'Raleway', sans-serif",
                "border-top": "2px solid black",
                "border-left": "2px solid black", 
                "border-right": "2px solid black", 
                "border-bottom": "2px solid black"
            },
            ".ag-header-cell-text": {
                "font-size": "14px"
            },
            ".ag-header-cell-label": {
                "justify-content": "center",
                "align-items": "center"
            },
            ".selected-row": {
                "background-color": "#394867 !important",
                "color": "white !important"
            }
        },
    )