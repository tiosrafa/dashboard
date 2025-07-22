import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from datetime import datetime
import os

# --- Configurações da Página ---
st.set_page_config(layout="wide", page_title="Dashboard Financeiro")

# --- Nome do arquivo para persistência dos dados ---
# Este será o arquivo onde seus dados serão salvos/carregados
DADOS_EXCEL_PADRAO = "dados_financeiros.xlsx"

# --- Funções para Processamento de Dados ---
def carregar_dados_xls(arquivo):
    """Carrega dados de um arquivo Excel, renomeia colunas e garante tipos corretos."""
    try:
        df = pd.read_excel(arquivo)
        
        # --- ATENÇÃO: SUBSTITUA COM OS NOMES REAIS DAS SUAS COLUNAS DO EXCEL ---
        # Exemplo: Se no seu Excel as colunas forem 'Data do Gasto', 'Item', 'Valor Pago'
        # Você faria:
        # df = df.rename(columns={
        #     'Data do Gasto': 'Data',
        #     'Item': 'Categoria',
        #     'Valor Pago': 'Valor'
        # })
        # Por enquanto, vou manter os placeholders para você substituir
        df = df.rename(columns={
            'SuaColunaDeData': 'Data',
            'SuaColunaDeCategoria': 'Categoria',
            'SuaColunaDeValor': 'Valor'
        })
        
        # Converte a coluna 'Data' para o formato datetime
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce') # 'coerce' transforma erros em NaT (Not a Time)
        
        # Garante que 'Valor' seja numérico
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0) # 'coerce' para NaN em erros, preenche NaN com 0
        
        # Remove linhas onde as colunas essenciais ('Data', 'Categoria', 'Valor') são inválidas
        df = df.dropna(subset=['Data', 'Categoria', 'Valor'])
        
        st.session_state.df_gastos = df
        st.success("Dados do Excel carregados com sucesso!")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

def salvar_dados_xls(df, filename=DADOS_EXCEL_PADRAO):
    """Salva o DataFrame atual em um arquivo Excel para persistência."""
    try:
        df.to_excel(filename, index=False)
        st.sidebar.success(f"Dados salvos em {filename}!")
    except Exception as e:
        st.sidebar.error(f"Erro ao salvar os dados: {e}")

# --- Inicialização de Dados na session_state ---
# Verifica se os dados já existem na session_state para evitar recarregar a cada interação
if 'df_gastos' not in st.session_state:
    if os.path.exists(DADOS_EXCEL_PADRAO):
        # Tenta carregar os dados salvos anteriormente
        try:
            df_carregado = pd.read_excel(DADOS_EXCEL_PADRAO)
            # Garante que 'Data' é datetime e 'Valor' é numérico ao carregar
            df_carregado['Data'] = pd.to_datetime(df_carregado['Data'], errors='coerce')
            df_carregado['Valor'] = pd.to_numeric(df_carregado['Valor'], errors='coerce').fillna(0)
            st.session_state.df_gastos = df_carregado.dropna(subset=['Data', 'Categoria', 'Valor'])
            st.sidebar.success(f"Dados carregados de '{DADOS_EXCEL_PADRAO}' na inicialização.")
        except Exception as e:
            st.sidebar.warning(f"Não foi possível carregar dados de '{DADOS_EXCEL_PADRAO}': {e}. Usando dados de exemplo.")
            # Se der erro ao carregar o arquivo existente, usa dados de exemplo
            st.session_state.df_gastos = pd.DataFrame({
                'Data': pd.to_datetime(['2025-01-15', '2025-01-20', '2025-02-10', '2025-02-25', '2025-03-05', '2025-03-05']),
            'Categoria': ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Contas', 'Steam'],
            'Valor': [500.00, 200.00, 1200.00, 300.00, 450.00, 50]
            })
    else:
        # Se o arquivo não existe, usa dados de exemplo
        st.session_state.df_gastos = pd.DataFrame({
            'Data': pd.to_datetime(['2025-01-15', '2025-01-20', '2025-02-10', '2025-02-25', '2025-03-05', '2025-03-05']),
            'Categoria': ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Contas', 'Steam'],
            'Valor': [500.00, 200.00, 1200.00, 300.00, 450.00, 50]
        })

if 'salario' not in st.session_state:
    st.session_state.salario = 3000.00
if 'page' not in st.session_state:
    st.session_state.page = "home" # Define a página inicial padrão

# --- Barra Lateral (Controles) ---
st.sidebar.title("Controles do Dashboard")

# Botão Página Inicial
if st.sidebar.button("Página Inicial"):
    st.session_state.page = "home"

st.sidebar.markdown("---") # Separador visual

# --- Entrada para Salário ---
st.sidebar.subheader("Ajustar Salário")
novo_salario = st.sidebar.number_input(
    "Defina seu Salário Mensal (R$)",
    min_value=0.0,
    value=float(st.session_state.salario), # Garante que é float para o widget
    step=100.0,
    format="%.2f",
    key="input_salario"
)
if novo_salario != st.session_state.salario:
    st.session_state.salario = novo_salario
    st.sidebar.success(f"Salário atualizado para R$ {novo_salario:,.2f}")

st.sidebar.markdown("---")

# --- Formulário para Inserir Novos Gastos ---
st.sidebar.subheader("Registrar Novo Gasto")
with st.sidebar.form("form_novo_gasto"):
    data_gasto = st.date_input("Data do Gasto", value=datetime.today())
    categoria_gasto = st.selectbox(
        "Categoria",
        options=['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Contas', 'Educação', 'Saúde', 'Outros'],
        index=0 # Define a opção padrão
    )
    valor_gasto = st.number_input("Valor (R$)", min_value=0.01, step=1.0, format="%.2f")
    
    submetido = st.form_submit_button("Adicionar Gasto")
    if submetido:
        # Cria um novo DataFrame com o gasto
        novo_df = pd.DataFrame([{
            'Data': pd.to_datetime(data_gasto),
            'Categoria': categoria_gasto,
            'Valor': valor_gasto
        }])
        # Concatena com o DataFrame existente e reinicia o índice
        st.session_state.df_gastos = pd.concat([st.session_state.df_gastos, novo_df], ignore_index=True)
        st.sidebar.success("Gasto adicionado com sucesso!")
        salvar_dados_xls(st.session_state.df_gastos) # Salva os dados atualizados

st.sidebar.markdown("---")

# --- Carregar Dados XLS (continua na barra lateral) ---
st.sidebar.subheader("Carregar Dados do Excel")
arquivo_upload = st.sidebar.file_uploader("Carregar arquivo XLS/XLSX", type=["xls", "xlsx"], key="file_uploader_xls")
if arquivo_upload is not None:
    carregar_dados_xls(arquivo_upload)
    salvar_dados_xls(st.session_state.df_gastos) # Salva os dados carregados do novo arquivo

# --- Conteúdo Principal do Dashboard ---
if st.session_state.page == "home":
    st.title("💸 Controle Financeiro")
    st.write("Bem-vindo ao seu controle de gastos e salários!")

    # --- Métricas Principais (Total Gastos, Salário, Saldo) ---
    col1, col2, col3 = st.columns(3)

    total_gastos = st.session_state.df_gastos['Valor'].sum() if not st.session_state.df_gastos.empty else 0
    saldo = st.session_state.salario - total_gastos
    saldo_cor = "green" if saldo >= 0 else "red"

    with col1:
        st.markdown(
            f"""
            <div style="background-color:#ffe0b2;padding:15px;border-radius:10px;text-align:center;">
                <h3>Total de Gastos</h3>
                <h1>R$ {total_gastos:,.2f}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color:#c8e6c9;padding:15px;border-radius:10px;text-align:center;">
                <h3>Salário Mensal</h3>
                <h1>R$ {st.session_state.salario:,.2f}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div style="background-color:#e0f2f7;padding:15px;border-radius:10px;text-align:center;">
                <h3>Saldo Atual</h3>
                <h1 style="color:{saldo_cor};">R$ {saldo:,.2f}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")

    # --- Gráficos de Barras lado a lado ---
    chart_col1, chart_col2 = st.columns(2)

    # Gráfico de Gastos por Categoria
    with chart_col1:
        st.subheader("Gastos por Categoria")
        if not st.session_state.df_gastos.empty:
            fig_cat, ax_cat = plt.subplots(figsize=(10, 6))
            df_agrupado_categoria = st.session_state.df_gastos.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
            
            ax_cat.bar(df_agrupado_categoria.index, df_agrupado_categoria.values, color='skyblue')
            ax_cat.set_xlabel("Categoria")
            ax_cat.set_ylabel("Valor (R$)")
            ax_cat.set_title("Distribuição de Gastos por Categoria")
            ax_cat.yaxis.set_major_formatter(mtick.FormatStrFormatter('R$%.2f'))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_cat)
        else:
            st.info("Sem dados de gastos para exibir o gráfico por categoria.")
    
    # Gráfico de Gastos por Mês
    with chart_col2:
        st.subheader("Gastos por Mês")
        if not st.session_state.df_gastos.empty:
            fig_mes, ax_mes = plt.subplots(figsize=(10, 6))
            
            # Garante que a coluna 'Data' é datetime antes de usar .dt
            df_para_mes = st.session_state.df_gastos.copy() # Crie uma cópia para evitar SettingWithCopyWarning
            df_para_mes['Mes_Ano'] = df_para_mes['Data'].dt.to_period('M')
            df_agrupado_mes = df_para_mes.groupby('Mes_Ano')['Valor'].sum().sort_values()
            
            ax_mes.bar(df_agrupado_mes.index.astype(str), df_agrupado_mes.values, color='lightcoral')
            ax_mes.set_xlabel("Mês/Ano")
            ax_mes.set_ylabel("Valor (R$)")
            ax_mes.set_title("Gastos Mensais")
            ax_mes.yaxis.set_major_formatter(mtick.FormatStrFormatter('R$%.2f'))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_mes)
        else:
            st.info("Sem dados de gastos para exibir o gráfico mensal.")
    
    st.markdown("---")

    # --- Tabela de Gastos Detalhada e Editável ---
    st.subheader("Detalhes dos Gastos (Clique duas vezes para editar)")
    # `st.data_editor` permite que o usuário edite a tabela diretamente
    # num_rows="dynamic" permite adicionar/remover linhas
    edited_df = st.data_editor(st.session_state.df_gastos, num_rows="dynamic", key="gastos_editor")
    
    # Se o DataFrame foi editado, atualize a session_state e salve
    if not edited_df.equals(st.session_state.df_gastos):
        st.session_state.df_gastos = edited_df.copy() # Use .copy() para evitar SettingWithCopyWarning
        # Garante que as colunas 'Data' e 'Valor' mantêm o tipo correto após a edição
        st.session_state.df_gastos['Data'] = pd.to_datetime(st.session_state.df_gastos['Data'], errors='coerce')
        st.session_state.df_gastos['Valor'] = pd.to_numeric(st.session_state.df_gastos['Valor'], errors='coerce').fillna(0)
        # Remova linhas incompletas que podem surgir de edição manual com `st.data_editor`
        st.session_state.df_gastos = st.session_state.df_gastos.dropna(subset=['Data', 'Categoria', 'Valor'])
        st.success("Tabela de gastos atualizada!")
        salvar_dados_xls(st.session_state.df_gastos) # Salva as alterações
