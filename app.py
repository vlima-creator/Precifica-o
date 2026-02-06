"""
Aplicativo Streamlit para Precificação e Gestão de Promoções - Carblue
Integra toda a lógica da planilha V3 com processamento de relatórios do Mercado Livre
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

from session_manager import inicializar_sessao, atualizar_regras_promocao, atualizar_margens
from pricing_calculator import PricingCalculator
from abc_classifier import ABCClassifier
from promotion_manager import PromotionManager
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
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
st.write("Precificação inteligente + Gestão de Promoções para Mercado Livre")

# Abas principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Home",
    "📥 Carregar Relatório",
    "📊 Análise ABC",
    "🎯 Promoções",
    "📋 Relatório Final"
])

# ============ TAB 1: HOME ============
with tab1:
    st.markdown('<div class="section-header">Bem-vindo ao Carblue!</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Como Funciona
        
        1. **Carregar Relatório**: Importe seu relatório de vendas do Mercado Livre (últimos 30, 60 ou 180 dias)
        
        2. **Análise ABC**: O sistema classifica seus produtos em Curva A (80%), B (15%) e C (5%) baseado em faturamento
        
        3. **Configurar Promoções**: Defina descontos específicos para cada curva
        
        4. **Gerar Relatório**: Exporte arquivo pronto para upload no Mercado Livre
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Funcionalidades
        
        - ✅ Precificação automática baseada em custos e margens
        - ✅ Classificação ABC inteligente
        - ✅ Cálculo de descontos seguros
        - ✅ Validação de saúde de precificação
        - ✅ Relatórios prontos para Mercado Livre
        - ✅ Análise de oportunidades
        """)
    
    st.divider()
    
    st.markdown("### 📝 Próximos Passos")
    st.info("👉 Carregue um relatório no **Sidebar** para começar!")

# ============ TAB 2: CARREGAR RELATÓRIO ============
with tab2:
    st.markdown('<div class="section-header">Relatório de Vendas</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None:
        st.info("📥 Carregue um relatório no **Sidebar** para começar")
    else:
        df_vendas = st.session_state.relatorio_vendas.copy()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de SKUs", len(df_vendas))
        with col2:
            st.metric("Faturamento", f"R$ {df_vendas['Faturamento'].sum():,.2f}")
        with col3:
            st.metric("Quantidade", int(df_vendas['Quantidade Vendida'].sum()))
        
        st.divider()
        st.subheader("Dados Carregados")
        st.dataframe(df_vendas, use_container_width=True)

# ============ TAB 3: ANÁLISE ABC ============
with tab3:
    st.markdown('<div class="section-header">Análise ABC de Produtos</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None:
        st.warning("⚠️ Carregue um relatório primeiro no **Sidebar**")
    else:
        df_vendas = st.session_state.relatorio_vendas.copy()
        
        # Classificar ABC
        classifier = ABCClassifier()
        df_abc = classifier.classificar_produtos(df_vendas, faturamento_col="Faturamento")
        
        st.session_state.dados_processados = df_abc
        
        # Resumo ABC
        st.subheader("📊 Resumo por Curva")
        resumo = classifier.gerar_resumo_abc(df_abc)
        
        col1, col2, col3 = st.columns(3)
        
        curva_a = resumo[resumo["Curva ABC"] == "A"]
        curva_b = resumo[resumo["Curva ABC"] == "B"]
        curva_c = resumo[resumo["Curva ABC"] == "C"]
        
        with col1:
            st.metric(
                "Curva A",
                f"{len(curva_a)} SKUs",
                f"R$ {curva_a['Faturamento'].sum():,.2f}"
            )
        
        with col2:
            st.metric(
                "Curva B",
                f"{len(curva_b)} SKUs",
                f"R$ {curva_b['Faturamento'].sum():,.2f}"
            )
        
        with col3:
            st.metric(
                "Curva C",
                f"{len(curva_c)} SKUs",
                f"R$ {curva_c['Faturamento'].sum():,.2f}"
            )
        
        st.divider()
        
        # Gráfico de distribuição
        st.subheader("📈 Distribuição de Faturamento")
        
        fig_pie = px.pie(
            resumo,
            values="Faturamento",
            names="Curva ABC",
            color="Curva ABC",
            color_discrete_map={"A": "#28a745", "B": "#ffc107", "C": "#dc3545"},
            title="Faturamento por Curva ABC"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        
        # Tabela detalhada
        st.subheader("📋 Produtos por Curva")
        
        curva_filtro = st.selectbox(
            "Filtrar por Curva",
            ["Todas", "A", "B", "C"]
        )
        
        if curva_filtro == "Todas":
            df_exibir = df_abc.sort_values("Faturamento", ascending=False)
        else:
            df_exibir = df_abc[df_abc["Curva ABC"] == curva_filtro].sort_values("Faturamento", ascending=False)
        
        st.dataframe(df_exibir, use_container_width=True)

# ============ TAB 4: PROMOÇÕES ============
with tab4:
    st.markdown('<div class="section-header">Configurar Promoções</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None:
        st.warning("⚠️ Carregue um relatório primeiro no **Sidebar**")
    else:
        st.markdown("""
        Defina os descontos que deseja aplicar em cada curva ABC.
        O sistema calculará automaticamente o impacto nas margens.
        """)
        
        st.subheader("💰 Descontos por Curva")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            desconto_a = st.slider(
                "Desconto Curva A (%)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.desconto_curva_a,
                step=0.5,
                key="desconto_a_slider"
            )
        
        with col2:
            desconto_b = st.slider(
                "Desconto Curva B (%)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.desconto_curva_b,
                step=0.5,
                key="desconto_b_slider"
            )
        
        with col3:
            desconto_c = st.slider(
                "Desconto Curva C (%)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.desconto_curva_c,
                step=0.5,
                key="desconto_c_slider"
            )
        
        # Atualizar regras
        atualizar_regras_promocao(desconto_a, desconto_b, desconto_c)
        
        st.divider()
        
        # Processar dados com promoções
        df_abc = st.session_state.dados_processados.copy()
        
        promotion_manager = PromotionManager()
        df_com_promocoes = promotion_manager.aplicar_descontos(
            df_abc,
            desconto_a / 100,
            desconto_b / 100,
            desconto_c / 100
        )
        
        # Resumo de impacto
        st.subheader("📊 Impacto das Promoções")
        
        col1, col2, col3 = st.columns(3)
        
        economia_total = (df_com_promocoes['Desconto'] * df_com_promocoes['Quantidade Vendida']).sum()
        
        with col1:
            st.metric(
                "Economia Total",
                f"R$ {economia_total:,.2f}",
                delta=f"{(economia_total / df_com_promocoes['Faturamento'].sum() * 100):.2f}%"
            )
        
        with col2:
            st.metric(
                "Produtos com Promoção",
                int((df_com_promocoes['Desconto'] > 0).sum())
            )
        
        with col3:
            st.metric(
                "Economia Média",
                f"R$ {economia_total / (df_com_promocoes['Desconto'] > 0).sum():,.2f}"
            )
        
        st.divider()
        
        # Tabela com promoções
        st.subheader("📋 Produtos com Promoções")
        
        df_promocoes = df_com_promocoes[df_com_promocoes['Desconto'] > 0].sort_values("Faturamento", ascending=False)
        
        st.dataframe(df_promocoes, use_container_width=True)
        
        # Salvar para próxima aba
        st.session_state.dados_promocoes = df_com_promocoes

# ============ TAB 5: RELATÓRIO FINAL ============
with tab5:
    st.markdown('<div class="section-header">Relatório Final</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None:
        st.warning("⚠️ Carregue um relatório primeiro no **Sidebar**")
    elif st.session_state.dados_promocoes is None:
        st.warning("⚠️ Configure as promoções primeiro na aba **'Promoções'**")
    else:
        st.markdown("""
        Seu relatório está pronto para download e upload no Mercado Livre.
        Ele contém todos os produtos com os descontos configurados.
        """)
        
        df_final = st.session_state.dados_promocoes.copy()
        
        # Estatísticas finais
        st.subheader("📊 Resumo Final")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de SKUs", len(df_final))
        with col2:
            st.metric("Faturamento Original", f"R$ {df_final['Faturamento'].sum():,.2f}")
        with col3:
            economia = (df_final['Desconto'] * df_final['Quantidade Vendida']).sum()
            st.metric("Economia Total", f"R$ {economia:,.2f}")
        with col4:
            st.metric("Faturamento com Promoção", f"R$ {(df_final['Faturamento'] - (df_final['Desconto'] * df_final['Quantidade Vendida'])).sum():,.2f}")
        
        st.divider()
        
        # Tabela final
        st.subheader("📋 Dados para Upload")
        st.dataframe(df_final, use_container_width=True)
        
        st.divider()
        
        # Download
        st.subheader("📥 Download")
        
        # Preparar arquivo para download
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_final.to_excel(writer, sheet_name="Relatório", index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar Relatório (Excel)",
            data=output.getvalue(),
            file_name="relatorio_promocoes_mercado_livre.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.info("✅ Arquivo pronto para upload no Mercado Livre!")
