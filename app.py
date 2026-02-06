"""
Aplicativo Streamlit para Precificação e Gestão de Promoções - Carblue
Integra toda a lógica da planilha V3 com processamento de relatórios do Mercado Livre
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
    page_title="Carblue Pricing & Promo Manager",
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

# Sidebar
st.sidebar.markdown("# ⚙️ Configurações")

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

with st.sidebar.expander("🏛️ Regimes Tributários", expanded=False):
    st.subheader("Configurações de Impostos")
    
    for regime, config in st.session_state.regimes.items():
        with st.container():
            st.write(f"**{regime}**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                ibs = st.number_input(
                    f"{regime} - IBS (%)",
                    value=config["ibs"] * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    key=f"ibs_{regime}",
                ) / 100
            with col2:
                cbs = st.number_input(
                    f"{regime} - CBS (%)",
                    value=config["cbs"] * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    key=f"cbs_{regime}",
                ) / 100
            with col3:
                impostos = st.number_input(
                    f"{regime} - Impostos e Encargos (%)",
                    value=config["impostos_encargos"] * 100,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key=f"impostos_{regime}",
                ) / 100
            
            st.session_state.regimes[regime]["ibs"] = ibs
            st.session_state.regimes[regime]["cbs"] = cbs
            st.session_state.regimes[regime]["impostos_encargos"] = impostos
            st.divider()

with st.sidebar.expander("📈 Margens Alvo", expanded=False):
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
    
    atualizar_margens(margem_bruta, margem_liquida)

with st.sidebar.expander("📥 Carregar Relatório", expanded=True):
    st.subheader("Importar Vendas")
    
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

# Main Content
st.markdown('<div class="main-header">💰 Carblue Pricing & Promo Manager</div>', unsafe_allow_html=True)
st.write("Precificação inteligente para Mercado Livre")

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
        ### 🎯 Como Funciona
        
        **Calculadora de Precificação:**
        - Insira SKU, Marketplace e Preço de Venda
        - Sistema calcula automaticamente custos, comissões e impostos
        - Visualize margem e status de saúde da precificação
        
        **Simulador de Preço Alvo:**
        - Defina a margem desejada
        - Sistema sugere o preço ideal
        - Veja limite de promoção segura
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Funcionalidades
        
        - ✅ Cálculo automático de custos
        - ✅ Margens em tempo real
        - ✅ Simulação de preços
        - ✅ Status de saúde (🟢 🟡 🔴)
        - ✅ Limite de desconto máximo
        - ✅ Relatórios para exportar
        """)
    
    st.divider()
    
    st.markdown("### 📝 Próximos Passos")
    st.info("👉 Vá para **'Calculadora de Precificação'** ou **'Simulador de Preço Alvo'** para começar!")

# ============ TAB 2: CALCULADORA DE PRECIFICAÇÃO ============
with tab2:
    st.markdown('<div class="section-header">Calculadora de Precificação</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Calcule a precificação de seus produtos com base em custos, comissões e impostos.
    """)
    
    # Opção 1: Entrada manual
    st.subheader("📝 Entrada Manual")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sku_input = st.text_input("SKU", value="", key="calc_sku")
    
    with col2:
        marketplace_input = st.selectbox(
            "Marketplace",
            options=list(st.session_state.marketplaces.keys()),
            key="calc_marketplace"
        )
    
    with col3:
        regime_input = st.selectbox(
            "Regime Tributário",
            options=list(st.session_state.regimes.keys()),
            key="calc_regime"
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        preco_venda = st.number_input(
            "Preço Venda (R$)",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key="calc_preco"
        )
    
    with col2:
        custo_produto = st.number_input(
            "Custo Produto (R$)",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key="calc_custo"
        )
    
    with col3:
        frete = st.number_input(
            "Frete (R$)",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key="calc_frete"
        )
    
    with col4:
        ads_percent = st.number_input(
            "Ads (%)",
            value=0.0,
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            key="calc_ads"
        )
    
    # Calcular
    if st.button("🧮 Calcular", key="calc_button"):
        if sku_input and preco_venda > 0:
            calc = PricingCalculatorV2(
                marketplaces=st.session_state.marketplaces,
                regimes=st.session_state.regimes,
                margem_bruta_alvo=st.session_state.margem_bruta_alvo,
                margem_liquida_minima=st.session_state.margem_liquida_minima
            )
            
            resultado = calc.calcular_linha(
                sku=sku_input,
                marketplace=marketplace_input,
                preco_venda=preco_venda,
                custo_produto=custo_produto,
                frete=frete,
                regime_tributario=regime_input,
                ads_percent=ads_percent
            )
            
            st.session_state.ultimo_calculo = resultado
    
    # Exibir resultado
    if "ultimo_calculo" in st.session_state:
        st.divider()
        st.subheader("📊 Resultado do Cálculo")
        
        resultado = st.session_state.ultimo_calculo
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Lucro (R$)", f"R$ {resultado['Lucro R$']:.2f}")
        with col2:
            st.metric("Margem (%)", f"{resultado['Margem %']:.2f}%")
        with col3:
            st.metric("Desconto Máx. (%)", f"{resultado['Desconto Máx. (%)']:.2f}%")
        with col4:
            st.metric("Status", resultado['Status'])
        
        st.divider()
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento")
        
        df_resultado = pd.DataFrame([resultado])
        st.dataframe(df_resultado, use_container_width=True)
    
    # Opção 2: Upload de arquivo
    st.divider()
    st.subheader("📤 Upload de Arquivo")
    
    st.markdown("""
    Carregue um arquivo Excel ou CSV com múltiplos produtos.
    Colunas esperadas: SKU, Marketplace, Preço Venda (R$), Custo Produto, Frete, Regime Tributário, Ads (%)
    """)
    
    uploaded_calc = st.file_uploader(
        "Escolha um arquivo",
        type=["xlsx", "xls", "csv"],
        key="calc_upload"
    )
    
    if uploaded_calc is not None:
        try:
            if uploaded_calc.name.endswith(".csv"):
                df_input = pd.read_csv(uploaded_calc)
            else:
                df_input = pd.read_excel(uploaded_calc)
            
            st.info(f"📊 {len(df_input)} linhas carregadas")
            
            if st.button("🧮 Calcular Todos", key="calc_all_button"):
                calc = PricingCalculatorV2(
                    marketplaces=st.session_state.marketplaces,
                    regimes=st.session_state.regimes,
                    margem_bruta_alvo=st.session_state.margem_bruta_alvo,
                    margem_liquida_minima=st.session_state.margem_liquida_minima
                )
                
                df_resultado = calc.calcular_dataframe(df_input)
                st.session_state.df_calculadora = df_resultado
            
            if "df_calculadora" in st.session_state:
                st.divider()
                st.subheader("📋 Resultados")
                st.dataframe(st.session_state.df_calculadora, use_container_width=True)
                
                # Download
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    st.session_state.df_calculadora.to_excel(writer, sheet_name="Calculadora", index=False)
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Resultado (Excel)",
                    data=output.getvalue(),
                    file_name="calculadora_precificacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

# ============ TAB 3: SIMULADOR DE PREÇO ALVO ============
with tab3:
    st.markdown('<div class="section-header">Simulador de Preço Alvo</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Simule preços baseado na margem desejada. O sistema calcula o preço sugerido e o limite de promoção.
    """)
    
    # Opção 1: Entrada manual
    st.subheader("📝 Entrada Manual")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sku_sim = st.text_input("SKU", value="", key="sim_sku")
    
    with col2:
        margem_alvo_sim = st.slider(
            "Margem Alvo (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.margem_bruta_alvo,
            step=1.0,
            key="sim_margem"
        )
    
    with col3:
        st.empty()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        custo_prod_sim = st.number_input(
            "Custo Produto (R$)",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key="sim_custo"
        )
    
    with col2:
        frete_sim = st.number_input(
            "Frete (R$)",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key="sim_frete"
        )
    
    with col3:
        taxa_fixa_sim = st.number_input(
            "Taxa Fixa (R$)",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key="sim_taxa"
        )
    
    with col4:
        st.empty()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        comissao_sim = st.number_input(
            "Comissão (%)",
            value=15.0,
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            key="sim_comissao"
        )
    
    with col2:
        impostos_sim = st.number_input(
            "Impostos (%)",
            value=8.0,
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            key="sim_impostos"
        )
    
    with col3:
        ads_sim = st.number_input(
            "Ads (%)",
            value=2.0,
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            key="sim_ads"
        )
    
    with col4:
        st.empty()
    
    # Simular
    if st.button("📊 Simular", key="sim_button"):
        if sku_sim and custo_prod_sim > 0:
            sim = PriceSimulator(
                marketplaces=st.session_state.marketplaces,
                regimes=st.session_state.regimes,
                margem_liquida_minima=st.session_state.margem_liquida_minima
            )
            
            resultado_sim = sim.simular_preco_unico(
                sku=sku_sim,
                custo_produto=custo_prod_sim,
                frete=frete_sim,
                taxa_fixa=taxa_fixa_sim,
                comissao_percent=comissao_sim,
                impostos_percent=impostos_sim,
                ads_percent=ads_sim,
                margem_alvo_percent=margem_alvo_sim
            )
            
            st.session_state.ultima_simulacao = resultado_sim
    
    # Exibir resultado
    if "ultima_simulacao" in st.session_state:
        st.divider()
        st.subheader("📊 Resultado da Simulação")
        
        resultado_sim = st.session_state.ultima_simulacao
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Preço Sugerido", f"R$ {resultado_sim['Preço Sugerido']:.2f}")
        with col2:
            st.metric("Lucro Estimado", f"R$ {resultado_sim['Lucro Estimado']:.2f}")
        with col3:
            st.metric("Preço Promo Limite", f"R$ {resultado_sim['Preço Promo Limite']:.2f}")
        with col4:
            st.metric("Lucro Promo", f"R$ {resultado_sim['Lucro Promo']:.2f}")
        
        st.divider()
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento")
        
        df_resultado_sim = pd.DataFrame([resultado_sim])
        st.dataframe(df_resultado_sim, use_container_width=True)
    
    # Opção 2: Upload de arquivo
    st.divider()
    st.subheader("📤 Upload de Arquivo")
    
    st.markdown("""
    Carregue um arquivo Excel ou CSV com múltiplos produtos.
    Colunas esperadas: SKU, Custo Produto, Frete, Taxa Fixa, Comissão (%), Impostos (%), Ads (%)
    """)
    
    uploaded_sim = st.file_uploader(
        "Escolha um arquivo",
        type=["xlsx", "xls", "csv"],
        key="sim_upload"
    )
    
    if uploaded_sim is not None:
        try:
            if uploaded_sim.name.endswith(".csv"):
                df_input_sim = pd.read_csv(uploaded_sim)
            else:
                df_input_sim = pd.read_excel(uploaded_sim)
            
            st.info(f"📊 {len(df_input_sim)} linhas carregadas")
            
            if st.button("📊 Simular Todos", key="sim_all_button"):
                sim = PriceSimulator(
                    marketplaces=st.session_state.marketplaces,
                    regimes=st.session_state.regimes,
                    margem_liquida_minima=st.session_state.margem_liquida_minima
                )
                
                df_resultado_sim = sim.calcular_dataframe(df_input_sim, margem_alvo_sim)
                st.session_state.df_simulador = df_resultado_sim
            
            if "df_simulador" in st.session_state:
                st.divider()
                st.subheader("📋 Resultados")
                st.dataframe(st.session_state.df_simulador, use_container_width=True)
                
                # Download
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    st.session_state.df_simulador.to_excel(writer, sheet_name="Simulador", index=False)
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Resultado (Excel)",
                    data=output.getvalue(),
                    file_name="simulador_preco_alvo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
