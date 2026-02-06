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
        st.session_state.regimes = DEFAULT_REGIMES.copy()
    
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


def atualizar_regras_promocao(regras):
    """Atualiza regras de promoção."""
    st.session_state.regras_promocao = regras


def atualizar_margens(bruta_alvo, liquida_minima):
    """Atualiza margens alvo."""
    st.session_state.margem_bruta_alvo = bruta_alvo
    st.session_state.margem_liquida_minima = liquida_minima
