"""
Configurações e constantes do aplicativo de precificação Carblue
"""

# Configurações padrão de Marketplaces
DEFAULT_MARKETPLACES = {
    "Mercado Livre": {"comissao": 0.14, "custo_fixo": 6.0, "taxa_devolucao": 0.02},  # Padrão Clássico
    "Shopee": {"comissao": 0.20, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Amazon": {"comissao": 0.15, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Magalu": {"comissao": 0.18, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Outros": {"comissao": 0.18, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
}

# Configurações de tipos de anúncio para Mercado Livre
MERCADO_LIVRE_AD_TYPES = {
    "Clássico": {"comissao": 0.14, "custo_fixo": 6.0},
    "Premium": {"comissao": 0.19, "custo_fixo": 6.0},
}

# Configurações de Regimes Tributários
DEFAULT_REGIMES = {
    "Simples Nacional": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.04},
    "Lucro Presumido": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.13},
    "Lucro Real": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.18},
    "MEI": {"ibs": 0.0, "cbs": 0.0, "impostos_encargos": 0.0},
}

# Limites de Curva ABC (baseado em % de faturamento acumulado)
CURVA_ABC_LIMITS = {
    "A": 0.80,  # 80% do faturamento
    "B": 0.95,  # 15% do faturamento (80% + 15%)
    "C": 1.00,  # 5% do faturamento (95% + 5%)
}

# Status de Saúde da Precificação
STATUS_SAUDAVEL = "🟢 Saudável"
STATUS_ALERTA = "🟡 Alerta"
STATUS_PREJUIZO = "🔴 Prejuízo/Abaixo"

# Colunas esperadas no relatório do Mercado Livre
MERCADO_LIVRE_COLUMNS = [
    "SKU",
    "Título",
    "Custo Produto",
    "Frete",
    "Preço Atual",
    "Tipo de Anúncio",  # Opcional
]

# Colunas da Base de Dados interna
BASE_DADOS_COLUMNS = [
    "SKU/MLB",
    "Descrição",
    "Marketplace",
    "Regime Tributário",
    "Custo Produto (R$)",
    "Frete (R$)",
    "Preço Base (R$)",
    "Vendas/Mês",
    "Curva ABC",
    "Margem Bruta (%)",
    "Margem Líquida (%)",
    "Ads (%)",
]
