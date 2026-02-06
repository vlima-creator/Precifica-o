"""
Aplicativo Streamlit para Precificação - Carblue
Novo fluxo: Relatório → Calculadora → Simulador
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

from session_manager import inicializar_sessao, atualizar_margens
from pricing_calculator_v2 import PricingCalculatorV2
from price_simulator import PriceSimulator
from mercado_livre_processor import MercadoLivreProcessor

# ============ FUNÇÕES DE FORMATAÇÃO ============
def formatar_moeda(valor):
    """Formata valor em reais no padrão brasileiro: R$ 1.234,50"""
    if pd.isna(valor) or valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_percentual(valor):
    """Formata percentual no padrão brasileiro: 12,50%"""
    if pd.isna(valor) or valor is None:
        return "0,00%"
    return f"{valor:.2f}%".replace(".", ",")

def formatar_percentual_1casa(valor):
    """Formata percentual com 1 casa decimal: 12,5%"""
    if pd.isna(valor) or valor is None:
        return "0,0%"
    return f"{valor:.1f}%".replace(".", ",")

def formatar_excel_profissional(df, nome_sheet="Relatorio"):
    """Formata um DataFrame para Excel com estilos profissionais"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils.dataframe import dataframe_to_rows
        
        wb = Workbook()
        ws = wb.active
        ws.title = nome_sheet
        
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                
                if r_idx == 1:
                    cell.font = Font(bold=True, color="FFFFFF", size=11)
                    cell.fill = PatternFill(start_color="556B2F", end_color="556B2F", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    if r_idx % 2 == 0:
                        cell.fill = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
                    if isinstance(value, (int, float)):
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                        cell.number_format = '#,##0.00'
                
                thin_border = Border(
                    left=Side(style="thin", color="CCCCCC"),
                    right=Side(style="thin", color="CCCCCC"),
                    top=Side(style="thin", color="CCCCCC"),
                    bottom=Side(style="thin", color="CCCCCC")
                )
                cell.border = thin_border
        
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        ws.freeze_panes = "A2"
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    except ImportError:
        buffer = BytesIO()
        df.to_excel(buffer, index=False, sheet_name=nome_sheet)
        buffer.seek(0)
        return buffer

# Configurar página
st.set_page_config(
    page_title="Precifica-o | Minimalista",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar sessão
inicializar_sessao()

# Estilos customizados
st.markdown("""
    <style>
    /* Tema Minimalista - Preto & Verde Militar */
    .stApp {
        background-color: #000000;
        color: #E8E8E8;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .status-saudavel { color: #6B8E23; font-weight: bold; }
    .status-alerta { color: #fbbf24; font-weight: bold; }
    .status-prejuizo { color: #f87171; font-weight: bold; }
    
    .config-section {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }

    /* Estilização Premium Dark para o Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #ffffff;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        font-size: 0.85rem !important;
        color: #cbd5e1;
    }
    [data-testid="stSidebar"] .stExpander {
        border: none !important;
        background-color: transparent !important;
        margin-bottom: 0.4rem !important;
    }
    [data-testid="stSidebar"] .stExpander details {
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        background-color: #0f172a !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stExpander details:hover {
        border-color: #334155 !important;
        background-color: #1e293b !important;
    }
    [data-testid="stSidebar"] .stExpander summary p {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
    }
    /* Ajuste de inputs no sidebar para Dark Mode */
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        font-size: 0.8rem !important;
        background-color: #020617 !important;
        color: #ffffff !important;
        border-color: #1e293b !important;
    }
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.75rem !important;
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        border-color: #1e293b !important;
    }
    /* Estilo para Tabs no Dark Mode */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre;
        background-color: #1e293b;
        border-radius: 4px 4px 0px 0px;
        color: #94a3b8;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #334155 !important;
        color: #ffffff !important;
    }
    /* Remover tarja branca no topo */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
        color: #ffffff !important;
    }
    /* Corrigir legibilidade do File Uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: #0f172a !important;
        border: 1px dashed #334155 !important;
    }
    [data-testid="stFileUploadDropzone"] p, 
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small {
        color: #ffffff !important;
    }
    /* Corrigir botões de upload e outros botões secundários */
    .stButton button {
        background-color: #556B2F !important;
        color: #ffffff !important;
        border: 1px solid #556B2F !important;
    }
    .stButton button:hover {
        background-color: #6B8E23 !important;
        border-color: #6B8E23 !important;
        color: #ffffff !important;
    }
    
    /* PENTE FINO: Legibilidade Global */
    /* Forçar cor de texto em todos os parágrafos e spans */
    p, span, label, li, .stMarkdown {
        color: #fafafa !important;
    }
    /* Ajustar métricas */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
    }
    /* Ajustar tabelas e dataframes */
    .stDataFrame, [data-testid="stTable"] {
        background-color: #0f172a !important;
    }
    /* Ajustar legendas e captions */
    .stCaption, small {
        color: #94a3b8 !important;
    }
    /* Ajustar inputs globais (fora do sidebar também) */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-color: #334155 !important;
    }
    /* Ajustar Sliders */
    .stSlider [data-baseweb="slider"] {
        background-color: transparent !important;
    }
    /* Ajustar Warnings e Infos */
    .stAlert {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }
    /* Ajustar Divisores */
    hr {
        border-color: #334155 !important;
    }
    /* Forçar cor branca em títulos de expanders fora do sidebar */
    .stExpander summary p {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
st.sidebar.markdown("# ⚙️ CONFIGURAÇÕES")
st.sidebar.markdown("---")

# 1. MARKETPLACES
with st.sidebar.expander("Marketplaces", expanded=False):
    for marketplace, config in st.session_state.marketplaces.items():
        st.markdown(f"**{marketplace}**")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            comissao = st.number_input(
                "Comissão (%)",
                value=config["comissao"] * 100,
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"comissao_{marketplace}",
            ) / 100
        
        with col2:
            taxa_fixa = st.number_input(
                "Taxa Fixa (R$)",
                value=config["custo_fixo"],
                min_value=0.0,
                step=0.1,
                key=f"taxa_fixa_{marketplace}",
            )
        
        st.session_state.marketplaces[marketplace]["comissao"] = comissao
        st.session_state.marketplaces[marketplace]["custo_fixo"] = taxa_fixa
        
        st.markdown("")
        st.divider()

# 2. REGIMES TRIBUTÁRIOS
with st.sidebar.expander("Regimes Tributários", expanded=False):
    for regime, config in st.session_state.regimes.items():
        st.markdown(f"**{regime}**")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            ibs = st.number_input(
                "IBS (%)",
                value=config.get("ibs", 0.0) * 100,
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                key=f"ibs_{regime}",
            ) / 100
        
        with col2:
            cbs = st.number_input(
                "CBS (%)",
                value=config.get("cbs", 0.0) * 100,
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                key=f"cbs_{regime}",
            ) / 100
        
        with col3:
            impostos = st.number_input(
                "Impostos (%)",
                value=config.get("impostos_encargos", 0.0) * 100,
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"impostos_{regime}",
            ) / 100
        
        st.session_state.regimes[regime]["ibs"] = ibs
        st.session_state.regimes[regime]["cbs"] = cbs
        st.session_state.regimes[regime]["impostos_encargos"] = impostos
        
        st.markdown("")
        st.divider()

# 3. MARGENS E PUBLICIDADE
with st.sidebar.expander("Margens e Publicidade", expanded=False):
    
    # Garantir que os valores sao validos
    valor_margem_bruta = float(st.session_state.get("margem_bruta_alvo", 30.0)) if st.session_state.get("margem_bruta_alvo") is not None else 30.0
    valor_margem_liquida = float(st.session_state.get("margem_liquida_minima", 10.0)) if st.session_state.get("margem_liquida_minima") is not None else 10.0
    valor_publicidade = float(st.session_state.get("percent_publicidade", 3.0)) if st.session_state.get("percent_publicidade") is not None else 3.0
    
    margem_bruta = st.slider(
        "Margem Bruta Alvo (%)",
        min_value=0.0,
        max_value=100.0,
        value=valor_margem_bruta,
        step=1.0,
        key="slider_margem_bruta"
    )
    st.caption(f"Margem Bruta: {formatar_percentual_1casa(margem_bruta)}")
    
    st.markdown("")
    
    margem_liquida = st.slider(
        "Margem Líquida Mínima (%)",
        min_value=0.0,
        max_value=100.0,
        value=valor_margem_liquida,
        step=1.0,
        key="slider_margem_liquida"
    )
    st.caption(f"Margem Líquida: {formatar_percentual_1casa(margem_liquida)}")
    
    st.markdown("")
    
    percent_pub = st.slider(
        "Percentual de Publicidade",
        min_value=0.0,
        max_value=100.0,
        value=valor_publicidade,
        step=0.1,
        key="slider_publicidade"
    )
    st.caption(f"Publicidade: {formatar_percentual_1casa(percent_pub)}")
    
    atualizar_margens(margem_bruta, margem_liquida, percent_pub)

# 4. CUSTOS OPERACIONAIS
with st.sidebar.expander("Custos Operacionais", expanded=False):
    
    custo_fixo_op = st.number_input(
        "Custo Fixo Operacional (R$)",
        value=st.session_state.get("custo_fixo_operacional", 0.0),
        min_value=0.0,
        step=0.1,
    )
    st.caption("Custo fixo mensal (aluguel, salários, etc.)")
    
    st.markdown("")
    
    taxa_devolucao = st.number_input(
        "Taxa de Devoluções e Trocas (%)",
        value=st.session_state.get("taxa_devolucao", 0.0) * 100,
        min_value=0.0,
        max_value=100.0,
        step=0.1,
    ) / 100
    st.caption("Percentual de perdas com devoluções")
    
    st.session_state.custo_fixo_operacional = custo_fixo_op
    st.session_state.taxa_devolucao = taxa_devolucao

# 5. CARREGAR RELATÓRIO
with st.sidebar.expander("Carregar Relatório de Vendas", expanded=False):
    
    st.markdown("""
    **Formato esperado:**
    - **A:** SKU/MLB
    - **B:** Título
    - **C:** Custo Produto (R$)
    - **D:** Frete (R$)
    - **E:** Preço Atual (R$)
    - **F:** Tipo de Anúncio (opcional)
    """)
    
    st.markdown("")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo",
        type=["xlsx", "xls", "csv"],
        help="Relatório de vendas do Mercado Livre",
        key="sidebar_upload"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("⏳ Processando..."):
                processor = MercadoLivreProcessor()
                
                if uploaded_file.name.endswith(".csv"):
                    df = processor.carregar_de_csv(uploaded_file)
                else:
                    df = processor.carregar_de_excel(uploaded_file)
                
                df_normalizado = processor.normalizar_relatorio_vendas(df)
                valido, mensagem = processor.validar_relatorio(df_normalizado)
                
                if valido:
                    df_agregado = processor.agregar_por_sku(df_normalizado)
                    st.session_state.relatorio_vendas = df_agregado
                    st.success(f"✅ {len(df_agregado)} SKUs carregados com sucesso!")
                else:
                    st.error(f"❌ {mensagem}")
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============ ABAS PRINCIPAIS ============
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["🏠 Home", "🧮 Calculadora de Precificação", "📊 Simulador de Preço Alvo"])

# ============ ABA 1: HOME ============
with tab1:
    st.markdown('<div class="main-header">💰 Dominador De Preços</div>', unsafe_allow_html=True)
    st.markdown("**Gestão Completa de Preços, Margens e Promoções**")
    st.markdown("---")
    
    st.markdown("""
    ### 📃 Como Funciona
    
    O **Dominador De Preços** ajuda você a precificar seus produtos de forma inteligente e automática.
    
    **Passo 1: Configurar** ⚙️
    - Defina as taxas de comissão dos marketplaces
    - Configure os regimes tributários
    - Estabeleça suas margens alvo
    - Defina custos operacionais e devoluções
    
    **Passo 2: Carregar Relatório** 📥
    - Importe seu relatório de vendas com: SKU, Título, Custo, Frete, Preço Atual
    - Opcionalmente, adicione o Tipo de Anúncio (Clássico/Premium para Mercado Livre)
    
    **Passo 3: Calcular Precificação** 🧮
    - Selecione o Marketplace e Regime Tributário
    - O sistema calcula automaticamente todos os custos
    - Veja o status de saúde de cada produto
    
    **Passo 4: Simular Preços** 📊
    - Veja os preços sugeridos para atingir suas margens
    - Compare preço normal vs. preço promocional
    - Analise o lucro esperado
    
    ---
    
    ### 🎯 Status de Saúde
    - 🟢 **Saudável**: Margem acima do alvo
    - 🟡 **Alerta**: Margem entre alvo e mínima
    - 🔴 **Prejuízo**: Margem abaixo do mínimo
    """)

# ============ ABA 2: CALCULADORA ============
with tab2:
    st.markdown('<div class="section-header">Calculadora de Precificação</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None or st.session_state.relatorio_vendas.empty:
        st.warning("⚠️ Nenhum relatório carregado. Carregue um arquivo no Sidebar.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            marketplace = st.selectbox(
                "Selecione o Marketplace",
                options=list(st.session_state.marketplaces.keys()),
                key="calc_marketplace"
            )
        
        with col2:
            regime = st.selectbox(
                "Selecione o Regime Tributário",
                options=list(st.session_state.regimes.keys()),
                key="calc_regime"
            )
        
        if st.button("🔄 Calcular Precificação", use_container_width=True):
            try:
                calculator = PricingCalculatorV2(
                    marketplaces=st.session_state.marketplaces,
                    regimes=st.session_state.regimes,
                    margem_bruta_alvo=st.session_state.margem_bruta_alvo,
                    margem_liquida_minima=st.session_state.margem_liquida_minima,
                    percent_publicidade=st.session_state.get("percent_publicidade", 3.0),
                    custo_fixo_operacional=st.session_state.get("custo_fixo_operacional", 0.0),
                    taxa_devolucao=st.session_state.get("taxa_devolucao", 0.0),
                )
                
                df_resultado = calculator.calcular_dataframe(
                    st.session_state.relatorio_vendas,
                    marketplace,
                    regime
                )
                
                st.session_state.resultado_calculadora = df_resultado
                st.success("✅ Cálculo realizado com sucesso!")
            
            except Exception as e:
                st.error(f"❌ Erro ao calcular: {str(e)}")
        
        if "resultado_calculadora" in st.session_state:
            df_resultado = st.session_state.resultado_calculadora
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de SKUs", len(df_resultado))
            with col2:
                st.metric("Margem Média", formatar_percentual_1casa(df_resultado['Margem Bruta %'].mean()))
            with col3:
                st.metric("Lucro Total", formatar_moeda(df_resultado['Lucro R$'].sum()))
            with col4:
                saudaveis = len(df_resultado[df_resultado['Status'] == '🟢 Saudável'])
                st.metric("Produtos Saudáveis", f"{saudaveis}/{len(df_resultado)}")
            
            st.divider()
            
            # Tabela
            st.markdown("**Detalhes da Precificação**")
            st.dataframe(df_resultado, use_container_width=True, hide_index=True)
            
            # Download
            excel_buffer = formatar_excel_profissional(df_resultado, "Calculadora")
            
            st.download_button(
                label="Baixar Resultado (Excel)",
                data=excel_buffer,
                file_name="calculadora_precificacao.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ============ ABA 3: SIMULADOR ============
with tab3:
    st.markdown('<div class="section-header">Simulador de Preço Alvo</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None or st.session_state.relatorio_vendas.empty:
        st.warning("⚠️ Nenhum relatório carregado. Carregue um arquivo no Sidebar.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            marketplace = st.selectbox(
                "Selecione o Marketplace",
                options=list(st.session_state.marketplaces.keys()),
                key="sim_marketplace"
            )
        
        with col2:
            regime = st.selectbox(
                "Selecione o Regime Tributário",
                options=list(st.session_state.regimes.keys()),
                key="sim_regime"
            )
        
        if st.button("📊 Simular Preços", use_container_width=True):
            try:
                simulator = PriceSimulator(
                    marketplaces=st.session_state.marketplaces,
                    regimes=st.session_state.regimes,
                    margem_bruta_alvo=st.session_state.margem_bruta_alvo,
                    margem_liquida_minima=st.session_state.margem_liquida_minima,
                    percent_publicidade=st.session_state.get("percent_publicidade", 3.0),
                    custo_fixo_operacional=st.session_state.get("custo_fixo_operacional", 0.0),
                    taxa_devolucao=st.session_state.get("taxa_devolucao", 0.0),
                )
                
                df_simulacao = simulator.calcular_dataframe(
                    st.session_state.relatorio_vendas,
                    marketplace,
                    regime
                )
                
                st.session_state.resultado_simulador = df_simulacao
                st.success("✅ Simulação realizada com sucesso!")
            
            except Exception as e:
                st.error(f"❌ Erro ao simular: {str(e)}")
        
        if "resultado_simulador" in st.session_state:
            df_simulacao = st.session_state.resultado_simulador
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Preço Médio Sugerido", formatar_moeda(df_simulacao['Preço Sugerido'].mean()))
            with col2:
                st.metric("Preço Promo Médio", formatar_moeda(df_simulacao['Preço Promo Limite'].mean()))
            with col3:
                st.metric("Lucro Bruto Total", formatar_moeda(df_simulacao['Lucro Bruto'].sum()))
            with col4:
                st.metric("Lucro Líquido Total", formatar_moeda(df_simulacao['Lucro Líquido'].sum()))
            
            st.divider()
            
            # Tabela
            st.markdown("**Simulação de Preços**")
            st.dataframe(df_simulacao, use_container_width=True, hide_index=True)
            
            # Download
            excel_buffer = formatar_excel_profissional(df_simulacao, "Simulador")
            
            st.download_button(
                label="Baixar Simulacao (Excel)",
                data=excel_buffer,
                file_name="simulador_preco_alvo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
