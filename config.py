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

# Tabelas de Taxa Fixa do Mercado Livre por Faixa de Preço (2025)
# Aplicada quando preço <= 79 reais
MERCADO_LIVRE_TAXA_FIXA = {
    "Produtos Comuns": [
        {"min": 0.0, "max": 29.0, "taxa_fixa": 6.25},
        {"min": 29.0, "max": 50.0, "taxa_fixa": 6.50},
        {"min": 50.0, "max": 79.0, "taxa_fixa": 6.75},
    ],
    "Livros": [
        {"min": 0.0, "max": 29.0, "taxa_fixa": 3.00},
        {"min": 29.0, "max": 50.0, "taxa_fixa": 3.50},
        {"min": 50.0, "max": 79.0, "taxa_fixa": 4.00},
    ],
}

# Limite para aplicacao da taxa fixa
MERCADO_LIVRE_LIMITE_TAXA_FIXA = 79.0

# Tabelas de Comissao e Subsidio Pix da Shopee por Faixa de Preco (2025)
SHOPEE_FAIXAS_PRECO = [
    {
        "min": 0.0,
        "max": 79.99,
        "comissao_percent": 0.20,
        "comissao_fixa": 4.0,
        "subsidio_pix_percent": 0.0,
        "descricao": "Ate R$ 79,99"
    },
    {
        "min": 80.0,
        "max": 99.99,
        "comissao_percent": 0.14,
        "comissao_fixa": 16.0,
        "subsidio_pix_percent": 0.05,
        "descricao": "R$ 80,00 - R$ 99,99"
    },
    {
        "min": 100.0,
        "max": 199.99,
        "comissao_percent": 0.14,
        "comissao_fixa": 20.0,
        "subsidio_pix_percent": 0.05,
        "descricao": "R$ 100,00 - R$ 199,99"
    },
    {
        "min": 200.0,
        "max": 499.99,
        "comissao_percent": 0.14,
        "comissao_fixa": 26.0,
        "subsidio_pix_percent": 0.05,
        "descricao": "R$ 200,00 - R$ 499,99"
    },
    {
        "min": 500.0,
        "max": float('inf'),
        "comissao_percent": 0.14,
        "comissao_fixa": 26.0,
        "subsidio_pix_percent": 0.08,
        "descricao": "Acima de R$ 500,00"
    },
]

# Configurações de Regimes Tributários
DEFAULT_REGIMES = {
    "Simples Nacional": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.04},
    "Lucro Presumido": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.13},
    "Lucro Real": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.18},
    "MEI": {"ibs": 0.0, "cbs": 0.0, "impostos_encargos": 0.0},
}

# Custos Operacionais (agora em seção separada)
DEFAULT_CUSTO_FIXO_OPERACIONAL = 0.0  # %
DEFAULT_TAXA_DEVOLUCAO = 0.0  # %

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
    "Publicidade (%)",
]
