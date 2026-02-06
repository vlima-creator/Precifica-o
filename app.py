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

# Configurar página
st.set_page_config(
    page_title="Carblue Pricing Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar sessão
inicializar_sessao()

# Estilos customizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .status-saudavel { color: #28a745; font-weight: bold; }
    .status-alerta { color: #ffc107; font-weight: bold; }
    .status-prejuizo { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
st.sidebar.markdown("# ⚙️ Configurações")

# Marketplaces
with st.sidebar.expander("📊 Marketplaces", expanded=False):
    st.subheader("Taxas de Comissão")
    
    for marketplace, config in st.session_state.marketplaces.items():
        col1, col2 = st.columns(2)
        with col1:
            comissao = st.number_input(
                f"{marketplace} - Comissão (%)",
                value=config["comissao"] * 100,
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"comissao_{marketplace}",
            ) / 100
        with col2:
            taxa_fixa = st.number_input(
                f"{marketplace} - Taxa Fixa (R$)",
                value=config["custo_fixo"],
                min_value=0.0,
                step=0.1,
                key=f"taxa_fixa_{marketplace}",
            )
        
        st.session_state.marketplaces[marketplace]["comissao"] = comissao
        st.session_state.marketplaces[marketplace]["custo_fixo"] = taxa_fixa

# Regimes Tributários
with st.sidebar.expander("🏛️ Regimes Tributários", expanded=False):
    st.subheader("Configurações de Impostos e Custos")
    
    for regime, config in st.session_state.regimes.items():
        with st.container():
            st.write(f"**{regime}**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ibs = st.number_input(
                    f"{regime} - IBS (%)",
                    value=config.get("ibs", 0.0) * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    key=f"ibs_{regime}",
                ) / 100
            with col2:
                cbs = st.number_input(
                    f"{regime} - CBS (%)",
                    value=config.get("cbs", 0.0) * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    key=f"cbs_{regime}",
                ) / 100
            with col3:
                impostos = st.number_input(
                    f"{regime} - Impostos (%)",
                    value=config.get("impostos_encargos", 0.0) * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=f"impostos_{regime}",
                ) / 100
            with col4:
                custo_fixo_op = st.number_input(
                    f"{regime} - Custo Fixo Op. (R$)",
                    value=config.get("custo_fixo_operacional", 0.0),
                    min_value=0.0,
                    step=0.1,
                    key=f"custo_fixo_op_{regime}",
                )
            
            st.session_state.regimes[regime]["ibs"] = ibs
            st.session_state.regimes[regime]["cbs"] = cbs
            st.session_state.regimes[regime]["impostos_encargos"] = impostos
            st.session_state.regimes[regime]["custo_fixo_operacional"] = custo_fixo_op
            st.divider()

# Margens Alvo
with st.sidebar.expander("📈 Margens e Publicidade", expanded=False):
    st.subheader("Defina suas margens")
    
    margem_bruta = st.slider(
        "Margem Bruta Alvo (%)",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.margem_bruta_alvo,
        step=1.0,
    )
    
    margem_liquida = st.slider(
        "Margem Líquida Mínima (%)",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.margem_liquida_minima,
        step=1.0,
    )
    
    percent_pub = st.slider(
        "% Publicidade",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.get("percent_publicidade", 3.0),
        step=0.1,
    )
    
    atualizar_margens(margem_bruta, margem_liquida, percent_pub)

# Carregar Relatório
with st.sidebar.expander("📥 Carregar Relatório", expanded=True):
    st.subheader("Importar Vendas")
    
    st.markdown("""
    **Formato esperado:**
    - SKU/MLB
    - Descrição
    - Custo Produto (R$)
    - Frete (R$)
    - Preço Atual (R$)
    """)
    
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
                    st.success(f"✅ {len(df_agregado)} SKUs carregados")
                else:
                    st.error(f"❌ {mensagem}")
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============ MAIN CONTENT ============
st.markdown('<div class="main-header">💰 Carblue Pricing Manager</div>', unsafe_allow_html=True)
st.write("Precificação inteligente baseada em seus dados")

# Verificar se há relatório carregado
if st.session_state.relatorio_vendas is None:
    st.warning("⚠️ Nenhum relatório carregado. Por favor, carregue um arquivo no Sidebar.")
    st.stop()

# Abas principais
tab1, tab2, tab3 = st.tabs([
    "🏠 Home",
    "🧮 Calculadora de Precificação",
    "📊 Simulador de Preço Alvo"
])

# ============ TAB 1: HOME ============
with tab1:
    st.markdown('<div class="section-header">Bem-vindo ao Carblue!</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Seu Relatório
        
        **Status:** ✅ Carregado
        
        - **SKUs:** """ + str(len(st.session_state.relatorio_vendas)) + """
        - **Faturamento Total:** R$ """ + f"{st.session_state.relatorio_vendas['Preço Atual'].sum():,.2f}" + """
        - **Quantidade:** """ + str(int(st.session_state.relatorio_vendas.get('Quantidade Vendida', pd.Series([0])).sum())) + """
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Próximos Passos
        
        1. **Calculadora de Precificação**
           - Selecione Marketplace e Regime
           - Veja a saúde de cada produto
        
        2. **Simulador de Preço Alvo**
           - Veja os preços sugeridos
           - Identifique oportunidades
        """)

# ============ TAB 2: CALCULADORA DE PRECIFICAÇÃO ============
with tab2:
    st.markdown('<div class="section-header">Calculadora de Precificação</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Selecione o Marketplace e Regime Tributário para calcular a precificação de seus produtos.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        marketplace_selecionado = st.selectbox(
            "Marketplace",
            options=list(st.session_state.marketplaces.keys()),
            key="calc_marketplace"
        )
    
    with col2:
        regime_selecionado = st.selectbox(
            "Regime Tributário",
            options=list(st.session_state.regimes.keys()),
            key="calc_regime"
        )
    
    # Calcular
    if st.button("🧮 Calcular Precificação", key="calc_button", use_container_width=True):
        with st.spinner("Calculando..."):
            calc = PricingCalculatorV2(
                marketplaces=st.session_state.marketplaces,
                regimes=st.session_state.regimes,
                margem_bruta_alvo=st.session_state.margem_bruta_alvo,
                margem_liquida_minima=st.session_state.margem_liquida_minima,
                percent_publicidade=st.session_state.percent_publicidade
            )
            
            df_resultado = calc.calcular_dataframe(
                st.session_state.relatorio_vendas,
                marketplace_selecionado,
                regime_selecionado
            )
            
            st.session_state.df_calculadora = df_resultado
    
    # Exibir resultado
    if "df_calculadora" in st.session_state:
        st.divider()
        st.subheader("📋 Resultado da Calculadora")
        
        df_calc = st.session_state.df_calculadora
        
        # Métricas resumidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            saudaveis = len(df_calc[df_calc["Status"] == "🟢 Saudável"])
            st.metric("🟢 Saudáveis", saudaveis)
        
        with col2:
            alertas = len(df_calc[df_calc["Status"] == "🟡 Alerta"])
            st.metric("🟡 Alertas", alertas)
        
        with col3:
            prejuizos = len(df_calc[df_calc["Status"] == "🔴 Prejuízo/Abaixo"])
            st.metric("🔴 Prejuízos", prejuizos)
        
        with col4:
            lucro_total = df_calc["Lucro R$"].sum()
            st.metric("💰 Lucro Total", f"R$ {lucro_total:,.2f}")
        
        st.divider()
        
        # Tabela detalhada
        st.subheader("📊 Detalhamento por Produto")
        
        # Colunas para exibir
        colunas_exibir = [
            "SKU", "Descrição", "Preço Atual (R$)", "Custo Produto", "Frete",
            "Comissão", "Impostos", "Publicidade", "Lucro R$", "Margem Bruta %", "Status"
        ]
        
        df_exibir = df_calc[colunas_exibir].copy()
        
        # Formatar valores monetários
        for col in ["Preço Atual (R$)", "Custo Produto", "Frete", "Comissão", "Impostos", "Publicidade", "Lucro R$"]:
            df_exibir[col] = df_exibir[col].apply(lambda x: f"R$ {x:.2f}")
        
        df_exibir["Margem Bruta %"] = df_exibir["Margem Bruta %"].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(df_exibir, use_container_width=True, hide_index=True)
        
        # Download
        st.divider()
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_calc.to_excel(writer, sheet_name="Calculadora", index=False)
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar Resultado (Excel)",
            data=output.getvalue(),
            file_name="calculadora_precificacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ============ TAB 3: SIMULADOR DE PREÇO ALVO ============
with tab3:
    st.markdown('<div class="section-header">Simulador de Preço Alvo</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Veja os preços sugeridos baseado em suas margens alvo e configurações.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        marketplace_sim = st.selectbox(
            "Marketplace",
            options=list(st.session_state.marketplaces.keys()),
            key="sim_marketplace"
        )
    
    with col2:
        regime_sim = st.selectbox(
            "Regime Tributário",
            options=list(st.session_state.regimes.keys()),
            key="sim_regime"
        )
    
    # Simular
    if st.button("📊 Simular Preços", key="sim_button", use_container_width=True):
        with st.spinner("Simulando..."):
            sim = PriceSimulator(
                marketplaces=st.session_state.marketplaces,
                regimes=st.session_state.regimes,
                margem_bruta_alvo=st.session_state.margem_bruta_alvo,
                margem_liquida_minima=st.session_state.margem_liquida_minima,
                percent_publicidade=st.session_state.percent_publicidade
            )
            
            df_resultado_sim = sim.calcular_dataframe(
                st.session_state.relatorio_vendas,
                marketplace_sim,
                regime_sim
            )
            
            st.session_state.df_simulador = df_resultado_sim
    
    # Exibir resultado
    if "df_simulador" in st.session_state:
        st.divider()
        st.subheader("📊 Resultado da Simulação")
        
        df_sim = st.session_state.df_simulador
        
        # Métricas resumidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            preco_medio = df_sim["Preço Sugerido"].mean()
            st.metric("Preço Médio Sugerido", f"R$ {preco_medio:,.2f}")
        
        with col2:
            preco_promo_medio = df_sim["Preço Promo Limite"].mean()
            st.metric("Preço Promo Médio", f"R$ {preco_promo_medio:,.2f}")
        
        with col3:
            lucro_bruto_total = df_sim["Lucro Bruto"].sum()
            st.metric("Lucro Bruto Total", f"R$ {lucro_bruto_total:,.2f}")
        
        with col4:
            lucro_liquido_total = df_sim["Lucro Líquido"].sum()
            st.metric("Lucro Líquido Total", f"R$ {lucro_liquido_total:,.2f}")
        
        st.divider()
        
        # Tabela detalhada
        st.subheader("📊 Detalhamento por Produto")
        
        # Colunas para exibir
        colunas_exibir_sim = [
            "SKU", "Descrição", "Preço Sugerido", "Preço Promo Limite",
            "Margem Bruta %", "Margem Líquida %", "Lucro Bruto", "Lucro Líquido"
        ]
        
        df_exibir_sim = df_sim[colunas_exibir_sim].copy()
        
        # Formatar valores monetários
        for col in ["Preço Sugerido", "Preço Promo Limite", "Lucro Bruto", "Lucro Líquido"]:
            df_exibir_sim[col] = df_exibir_sim[col].apply(lambda x: f"R$ {x:.2f}")
        
        df_exibir_sim["Margem Bruta %"] = df_exibir_sim["Margem Bruta %"].apply(lambda x: f"{x:.2f}%")
        df_exibir_sim["Margem Líquida %"] = df_exibir_sim["Margem Líquida %"].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(df_exibir_sim, use_container_width=True, hide_index=True)
        
        # Download
        st.divider()
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_sim.to_excel(writer, sheet_name="Simulador", index=False)
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar Resultado (Excel)",
            data=output.getvalue(),
            file_name="simulador_preco_alvo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
