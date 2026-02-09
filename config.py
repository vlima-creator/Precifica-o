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

# Tabelas de Custo Operacional do Mercado Livre por Peso e Preço (Válido a partir de 02/03/2026)
# Aplicada para Logística Full, Coleta e Agências quando preço <= 79 reais
MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO = {
    "Produtos Comuns": [
        {
            "peso_min_kg": 0.0,
            "peso_max_kg": 0.3,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 5.65},
                {"preco_max": 48.99, "custo": 6.55},
                {"preco_max": 78.99, "custo": 7.75},
            ]
        },
        {
            "peso_min_kg": 0.3,
            "peso_max_kg": 0.5,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 5.95},
                {"preco_max": 48.99, "custo": 6.65},
                {"preco_max": 78.99, "custo": 7.85},
            ]
        },
        {
            "peso_min_kg": 0.5,
            "peso_max_kg": 1.0,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 6.05},
                {"preco_max": 48.99, "custo": 6.75},
                {"preco_max": 78.99, "custo": 7.95},
            ]
        },
        {
            "peso_min_kg": 1.0,
            "peso_max_kg": 1.5,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 6.15},
                {"preco_max": 48.99, "custo": 6.85},
                {"preco_max": 78.99, "custo": 8.05},
            ]
        },
        {
            "peso_min_kg": 1.5,
            "peso_max_kg": 2.0,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 6.25},
                {"preco_max": 48.99, "custo": 6.95},
                {"preco_max": 78.99, "custo": 8.15},
            ]
        },
        {
            "peso_min_kg": 2.0,
            "peso_max_kg": 3.0,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 6.35},
                {"preco_max": 48.99, "custo": 7.95},
                {"preco_max": 78.99, "custo": 8.55},
            ]
        },
        {
            "peso_min_kg": 3.0,
            "peso_max_kg": 4.0,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 6.45},
                {"preco_max": 48.99, "custo": 8.15},
                {"preco_max": 78.99, "custo": 8.95},
            ]
        },
        {
            "peso_min_kg": 4.0,
            "peso_max_kg": 5.0,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 6.55},
                {"preco_max": 48.99, "custo": 8.35},
                {"preco_max": 78.99, "custo": 9.75},
            ]
        },
    ],
    "Livros": [
        {
            "peso_min_kg": 0.0,
            "peso_max_kg": 0.3,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 2.83},
                {"preco_max": 48.99, "custo": 3.28},
                {"preco_max": 78.99, "custo": 3.88},
            ]
        },
        {
            "peso_min_kg": 0.3,
            "peso_max_kg": 0.5,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 2.98},
                {"preco_max": 48.99, "custo": 3.33},
                {"preco_max": 78.99, "custo": 3.93},
            ]
        },
        {
            "peso_min_kg": 0.5,
            "peso_max_kg": 1.0,
            "custos_por_faixa": [
                {"preco_max": 18.99, "custo": 3.03},
                {"preco_max": 48.99, "custo": 3.38},
                {"preco_max": 78.99, "custo": 3.98},
            ]
        },
    ],
}

# Tabelas de Taxa Fixa do Mercado Livre para Envios Flex (Logística Própria) - Válido a partir de 02/03/2026
# Aplicada quando preço <= 79 reais e usando logística própria (Flex, Retirada, etc.)
MERCADO_LIVRE_TAXA_FIXA_FLEX = {
    "Produtos Comuns": [
        {"min": 0.0, "max": 18.99, "taxa_fixa": 6.25},
        {"min": 19.0, "max": 48.99, "taxa_fixa": 6.65},
        {"min": 49.0, "max": 78.99, "taxa_fixa": 7.75},
    ],
    "Livros": [
        {"min": 0.0, "max": 18.99, "taxa_fixa": 3.00},
        {"min": 19.0, "max": 48.99, "taxa_fixa": 3.50},
        {"min": 49.0, "max": 78.99, "taxa_fixa": 4.50},
    ],
}

# Tabelas de Custo de Frete para Produtos acima de R$ 79 (Frete Grátis) - Válido a partir de 02/03/2026
# Aplicada para Logística Full, Coleta e Agências quando preço >= 79 reais
MERCADO_LIVRE_FRETE_GRATIS_PESO = {
    "Produtos Comuns": [
        {
            "peso_min_kg": 0.0,
            "peso_max_kg": 0.3,
            "custos_por_faixa": [
                {"preco_max": 99.99, "custo": 12.35},
                {"preco_max": 119.99, "custo": 14.35},
                {"preco_max": 149.99, "custo": 16.45},
                {"preco_max": 199.99, "custo": 18.45},
                {"preco_max": float('inf'), "custo": 20.95},
            ]
        },
        {
            "peso_min_kg": 0.3,
            "peso_max_kg": 0.5,
            "custos_por_faixa": [
                {"preco_max": 99.99, "custo": 13.25},
                {"preco_max": 119.99, "custo": 15.45},
                {"preco_max": 149.99, "custo": 17.65},
                {"preco_max": 199.99, "custo": 19.85},
                {"preco_max": float('inf'), "custo": 22.55},
            ]
        },
        {
            "peso_min_kg": 0.5,
            "peso_max_kg": 1.0,
            "custos_por_faixa": [
                {"preco_max": 99.99, "custo": 13.85},
                {"preco_max": 119.99, "custo": 16.15},
                {"preco_max": 149.99, "custo": 18.45},
                {"preco_max": 199.99, "custo": 20.75},
                {"preco_max": float('inf'), "custo": 23.65},
            ]
        },
    ],
    "Livros": [
        {
            "peso_min_kg": 0.0,
            "peso_max_kg": 0.3,
            "custos_por_faixa": [
                {"preco_max": 99.99, "custo": 12.35},
                {"preco_max": 119.99, "custo": 14.35},
                {"preco_max": 149.99, "custo": 16.45},
                {"preco_max": 199.99, "custo": 18.45},
                {"preco_max": float('inf'), "custo": 20.95},
            ]
        },
    ],
}

# Limite para aplicacao da taxa fixa (até R$ 79, acima disso é frete grátis)
MERCADO_LIVRE_LIMITE_TAXA_FIXA = 79.0

# Tipos de logística do Mercado Livre
MERCADO_LIVRE_TIPOS_LOGISTICA = {
    "Full": "Logística Mercado Livre (Full, Coleta, Agências)",
    "Flex": "Minha Logística (Flex, Retirada, Acordo com Comprador)",
}

# Tabelas de Comissao e Subsidio Pix da Shopee por Faixa de Preco (2026)
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
