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
    st.info("👉 Clique em **'Carregar Relatório'** para começar!")

# ============ TAB 2: CARREGAR RELATÓRIO ============
with tab2:
    st.markdown('<div class="section-header">Carregar Relatório de Vendas</div>', unsafe_allow_html=True)
    
    st.write("Importe seu relatório de vendas do Mercado Livre em formato Excel ou CSV")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo",
        type=["xlsx", "xls", "csv"],
        help="Arquivo deve conter: SKU, Preço, Quantidade Vendida"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("⏳ Carregando e processando arquivo..."):
                # Carregar arquivo
                processor = MercadoLivreProcessor()
                
                if uploaded_file.name.endswith(".csv"):
                    df = processor.carregar_de_csv(uploaded_file)
                else:
                    # Usar processador que detecta skiprows automaticamente
                    df = processor.carregar_de_excel(uploaded_file)
                
                st.success("✅ Arquivo carregado com sucesso!")
                
                # Mostrar preview
                st.subheader("Preview dos Dados (Primeiras 10 linhas)")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Normalizar relatório
                df_normalizado = processor.normalizar_relatorio_vendas(df)
                
                st.info(f"📊 Dados normalizados: {len(df_normalizado)} linhas processadas")
                
                # Validar
                valido, mensagem = processor.validar_relatorio(df_normalizado)
                
                if valido:
                    st.success(f"✅ {mensagem}")
                    
                    # Agregar por SKU
                    df_agregado = processor.agregar_por_sku(df_normalizado)
                    
                    # Salvar na sessão
                    st.session_state.relatorio_vendas = df_agregado
                    
                    # Mostrar estatísticas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total de SKUs", len(df_agregado))
                    with col2:
                        st.metric("Faturamento Total", f"R$ {df_agregado['Faturamento'].sum():,.2f}")
                    with col3:
                        st.metric("Preço Médio", f"R$ {df_agregado['Preço'].mean():,.2f}")
                    with col4:
                        st.metric("Quantidade Total", int(df_agregado['Quantidade Vendida'].sum()))
                    
                    st.divider()
                    st.info("✅ Relatório pronto! Vá para **'Análise ABC'** para continuar.")
                else:
                    st.error(f"❌ Erro: {mensagem}")
        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.info("💡 Dica: Certifique-se que o arquivo é um relatório válido do Mercado Livre com as colunas: SKU, Preço e Quantidade Vendida")

# ============ TAB 3: ANÁLISE ABC ============
with tab3:
    st.markdown('<div class="section-header">Análise ABC de Produtos</div>', unsafe_allow_html=True)
    
    if st.session_state.relatorio_vendas is None:
        st.warning("⚠️ Carregue um relatório primeiro em **'Carregar Relatório'**")
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
            if not curva_a.empty:
                st.metric("Curva A", f"{int(curva_a['Qtd SKUs'].values[0])} SKUs", 
                         f"R$ {curva_a['Faturamento Total'].values[0]:,.0f}")
            else:
                st.metric("Curva A", "0 SKUs", "R$ 0")
        
        with col2:
            if not curva_b.empty:
                st.metric("Curva B", f"{int(curva_b['Qtd SKUs'].values[0])} SKUs",
                         f"R$ {curva_b['Faturamento Total'].values[0]:,.0f}")
            else:
                st.metric("Curva B", "0 SKUs", "R$ 0")
        
        with col3:
            if not curva_c.empty:
                st.metric("Curva C", f"{int(curva_c['Qtd SKUs'].values[0])} SKUs",
                         f"R$ {curva_c['Faturamento Total'].values[0]:,.0f}")
            else:
                st.metric("Curva C", "0 SKUs", "R$ 0")
        
        # Gráfico de distribuição
        st.subheader("📈 Distribuição de Faturamento")
        
        fig = px.pie(
            resumo,
            values="Faturamento Total",
            names="Curva ABC",
            color="Curva ABC",
            color_discrete_map={"A": "#28a745", "B": "#ffc107", "C": "#dc3545", "Sem Curva": "#6c757d"},
            title="Faturamento por Curva ABC"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Produtos por Curva")
        
        for curva in ["A", "B", "C", "Sem Curva"]:
            df_curva = df_abc[df_abc["Curva ABC"] == curva]
            
            if not df_curva.empty:
                with st.expander(f"Curva {curva} ({len(df_curva)} produtos)"):
                    cols_mostrar = ["SKU", "Descrição", "Preço", "Quantidade Vendida", "Faturamento"]
                    cols_disponiveis = [col for col in cols_mostrar if col in df_curva.columns]
                    st.dataframe(df_curva[cols_disponiveis], use_container_width=True)

# ============ TAB 4: PROMOÇÕES ============
with tab4:
    st.markdown('<div class="section-header">Configurar Promoções</div>', unsafe_allow_html=True)
    
    if st.session_state.dados_processados is None:
        st.warning("⚠️ Execute a **'Análise ABC'** primeiro")
    else:
        st.write("Defina o desconto que deseja aplicar em cada curva ABC")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            desconto_a = st.number_input(
                "Desconto Curva A (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.regras_promocao["A"] * 100,
                step=0.1,
            ) / 100
        
        with col2:
            desconto_b = st.number_input(
                "Desconto Curva B (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.regras_promocao["B"] * 100,
                step=0.1,
            ) / 100
        
        with col3:
            desconto_c = st.number_input(
                "Desconto Curva C (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.regras_promocao["C"] * 100,
                step=0.1,
            ) / 100
        
        with col4:
            desconto_sem = st.number_input(
                "Desconto Sem Curva (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.regras_promocao["Sem Curva"] * 100,
                step=0.1,
            ) / 100
        
        # Atualizar regras
        regras = {
            "A": desconto_a,
            "B": desconto_b,
            "C": desconto_c,
            "Sem Curva": desconto_sem,
        }
        atualizar_regras_promocao(regras)
        
        # Aplicar promoções
        promotion_manager = PromotionManager()
        df_com_promo = promotion_manager.aplicar_promocoes(
            st.session_state.dados_processados,
            regras=regras
        )
        
        st.session_state.dados_com_promocoes = df_com_promo
        
        # Resumo de impacto
        st.subheader("💡 Impacto das Promoções")
        
        relatorio_promo = promotion_manager.gerar_relatorio_promocoes(df_com_promo)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total de Economia",
                f"R$ {relatorio_promo['total_economia']:,.2f}",
                f"{relatorio_promo['produtos_com_promocao']} produtos"
            )
        
        with col2:
            st.metric(
                "Economia Média por Produto",
                f"R$ {relatorio_promo['economia_media']:,.2f}"
            )
        
        with col3:
            st.metric(
                "Produtos com Promoção",
                relatorio_promo['produtos_com_promocao']
            )
        
        # Tabela de promoções
        st.subheader("📊 Detalhes das Promoções")
        
        df_promo_view = df_com_promo[
            df_com_promo["Desconto %"] > 0
        ][["SKU", "Descrição", "Preço", "Preço Promocional", "Desconto %", "Economia R$", "Curva ABC"]].copy()
        
        if not df_promo_view.empty:
            df_promo_view["Preço"] = df_promo_view["Preço"].apply(lambda x: f"R$ {x:.2f}")
            df_promo_view["Preço Promocional"] = df_promo_view["Preço Promocional"].apply(lambda x: f"R$ {x:.2f}")
            df_promo_view["Desconto %"] = df_promo_view["Desconto %"].apply(lambda x: f"{x*100:.1f}%")
            df_promo_view["Economia R$"] = df_promo_view["Economia R$"].apply(lambda x: f"R$ {x:.2f}")
            
            st.dataframe(df_promo_view, use_container_width=True)
        else:
            st.info("Nenhuma promoção configurada. Ajuste os descontos acima.")

# ============ TAB 5: RELATÓRIO FINAL ============
with tab5:
    st.markdown('<div class="section-header">Gerar Relatório Final</div>', unsafe_allow_html=True)
    
    if st.session_state.dados_com_promocoes is None:
        st.warning("⚠️ Configure as **'Promoções'** primeiro")
    else:
        st.write("Relatório pronto para upload no Mercado Livre")
        
        df_final = st.session_state.dados_com_promocoes.copy()
        
        # Preparar dados para exportação
        df_export = df_final[["SKU", "Descrição", "Preço", "Preço Promocional", "Desconto %", "Curva ABC"]].copy()
        df_export.columns = ["SKU/MLB", "Título", "Preço Atual", "Preço Promoção", "Desconto %", "Curva"]
        
        # Preview
        st.subheader("📋 Preview do Relatório")
        st.dataframe(df_export, use_container_width=True)
        
        # Download
        st.subheader("📥 Download")
        
        # Converter para Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_export.to_excel(writer, sheet_name="Promoções", index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar Relatório (Excel)",
            data=output.getvalue(),
            file_name="carblue_promocoes_mercado_livre.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.success("✅ Relatório pronto! Baixe e importe no Mercado Livre.")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.9rem; margin-top: 2rem;">
        <p>Carblue Pricing & Promo Manager v1.0 | Desenvolvido com ❤️ para sua precificação inteligente</p>
    </div>
""", unsafe_allow_html=True)
