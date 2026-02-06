"""
Módulo para gerenciamento de estado da sessão Streamlit
"""

import streamlit as st
from config import DEFAULT_MARKETPLACES, DEFAULT_REGIMES


def inicializar_sessao():
    """Inicializa variáveis de sessão padrão."""
    
    # Configurações de Marketplace
    if "marketplaces" not in st.session_state:
        st.session_state.marketplaces = DEFAULT_MARKETPLACES.copy()
    
    # Configurações de Regime Tributário
    if "regimes" not in st.session_state:
        # Adicionar custo fixo operacional a cada regime
        regimes_com_custo = {}
        for regime, config in DEFAULT_REGIMES.items():
            regimes_com_custo[regime] = {
                **config,
                "custo_fixo_operacional": 0.0  # Padrão 0
            }
        st.session_state.regimes = regimes_com_custo
    
    # Dados da Base
    if "base_dados" not in st.session_state:
        st.session_state.base_dados = None
    
    # Relatório de Vendas Mercado Livre
    if "relatorio_vendas" not in st.session_state:
        st.session_state.relatorio_vendas = None
    
    # Dados Processados (com Curva ABC)
    if "dados_processados" not in st.session_state:
        st.session_state.dados_processados = None
    
    # Regras de Promoção
    if "regras_promocao" not in st.session_state:
        st.session_state.regras_promocao = {
            "A": 0.0,
            "B": 0.0,
            "C": 0.0,
            "Sem Curva": 0.0,
        }
    
    # Dados com Promoções Aplicadas
    if "dados_com_promocoes" not in st.session_state:
        st.session_state.dados_com_promocoes = None
    
    # Configurações de Margens
    if "margem_bruta_alvo" not in st.session_state:
        st.session_state.margem_bruta_alvo = 30.0
    
    if "margem_liquida_minima" not in st.session_state:
        st.session_state.margem_liquida_minima = 10.0
    
    # % Publicidade
    if "percent_publicidade" not in st.session_state:
        st.session_state.percent_publicidade = 3.0
    
    # Descontos por Curva ABC
    if "desconto_curva_a" not in st.session_state:
        st.session_state.desconto_curva_a = 0.0
    
    if "desconto_curva_b" not in st.session_state:
        st.session_state.desconto_curva_b = 0.0
    
    if "desconto_curva_c" not in st.session_state:
        st.session_state.desconto_curva_c = 0.0
    
    # Dados com Promoções
    if "dados_promocoes" not in st.session_state:
        st.session_state.dados_promocoes = None
    
    # Aba ativa
    if "aba_ativa" not in st.session_state:
        st.session_state.aba_ativa = "home"


def resetar_sessao():
    """Reseta todas as variáveis de sessão."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    inicializar_sessao()


def atualizar_marketplace(nome, config):
    """Atualiza configuração de um marketplace."""
    st.session_state.marketplaces[nome] = config


def atualizar_regime(nome, config):
    """Atualiza configuração de um regime tributário."""
    st.session_state.regimes[nome] = config


def atualizar_regras_promocao(desconto_a, desconto_b, desconto_c):
    """Atualiza regras de promoção."""
    st.session_state.desconto_curva_a = desconto_a
    st.session_state.desconto_curva_b = desconto_b
    st.session_state.desconto_curva_c = desconto_c
    st.session_state.regras_promocao = {
        "A": desconto_a,
        "B": desconto_b,
        "C": desconto_c,
        "Sem Curva": 0.0,
    }


def atualizar_margens(bruta_alvo, liquida_minima, percent_publicidade=None):
    """Atualiza margens alvo e % publicidade."""
    st.session_state.margem_bruta_alvo = bruta_alvo
    st.session_state.margem_liquida_minima = liquida_minima
    if percent_publicidade is not None:
        st.session_state.percent_publicidade = percent_publicidade
