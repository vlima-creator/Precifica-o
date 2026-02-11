"""
Configurações e constantes do aplicativo de precificação Carblue
Atualizado com as regras do Mercado Livre 2026 (Analise_Mercado_Livre_2026.xlsx)
"""

# Configurações padrão de Marketplaces
DEFAULT_MARKETPLACES = {
    "Mercado Livre": {"comissao": 0.14, "custo_fixo": 6.0, "taxa_devolucao": 0.02},
    "Shopee": {"comissao": 0.20, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Amazon": {"comissao": 0.15, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Magalu": {"comissao": 0.18, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Outros": {"comissao": 0.18, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
}

# ============================================================================
# MERCADO LIVRE 2026 - MATRIZES DE CUSTOS E REGRAS
# ============================================================================

# Limites de Preço
MERCADO_LIVRE_LIMITE_TAXA_FIXA = 79.0
MERCADO_LIVRE_LIMITE_CUSTO_FIXO_BAIXO = 12.50
MERCADO_LIVRE_LIMITE_CUSTO_OPERACIONAL_GERAL = 19.0
MERCADO_LIVRE_LIMITE_CUSTO_OPERACIONAL_SUPERMERCADO = 29.0

# Regras de Custo Fixo Condicional
MERCADO_LIVRE_REGRAS_CUSTO_FIXO = {
    "abaixo_12_50": 0.50,  # 50% do valor do produto
    "abaixo_19_geral": 0.50,  # Máximo 50% do preço
    "abaixo_29_supermercado": 0.25,  # Máximo 25% do preço
}

# 1. Custo Operacional Full, Coleta e Agências (Preço <= 79)
MERCADO_LIVRE_CUSTO_OPERACIONAL_FULL_2026 = {
    "Até 300g": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 5.65},
        {"preco_min": 19.0, "preco_max": 48.99, "custo": 6.55},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 7.75},
    ],
    "300g a 500g": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 5.95},
        {"preco_min": 19.0, "preco_max": 48.99, "custo": 6.65},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 7.85},
    ],
    "500g a 1kg": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 6.05},
        {"preco_min": 19.0, "preco_max": 48.99, "custo": 6.75},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 7.95},
    ],
    "1kg a 2kg": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 6.25},
        {"preco_min": 19.0, "preco_max": 48.99, "custo": 6.95},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 8.15},
    ],
}

# 2. Custo Operacional Supermercado 2026
MERCADO_LIVRE_CUSTO_OPERACIONAL_SUPERMERCADO_2026 = {
    "Até 300g": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 1.25},
        {"preco_min": 19.0, "preco_max": 28.99, "custo": 1.50},
        {"preco_min": 29.0, "preco_max": 48.99, "custo": 2.00},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 3.00},
        {"preco_min": 79.0, "preco_max": 98.99, "custo": 4.00},
        {"preco_min": 99.0, "preco_max": 198.99, "custo": 6.00},
        {"preco_min": 199.0, "preco_max": float('inf'), "custo": 20.95},
    ],
    "500g a 1kg": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 1.25},
        {"preco_min": 19.0, "preco_max": 28.99, "custo": 1.50},
        {"preco_min": 29.0, "preco_max": 48.99, "custo": 2.00},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 3.00},
        {"preco_min": 79.0, "preco_max": 98.99, "custo": 4.00},
        {"preco_min": 99.0, "preco_max": 198.99, "custo": 6.00},
        {"preco_min": 199.0, "preco_max": float('inf'), "custo": 23.65},
    ],
}

# 3. Custo Operacional Livros 2026
MERCADO_LIVRE_CUSTO_OPERACIONAL_LIVROS_2026 = {
    "Até 300g": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 2.83},
        {"preco_min": 19.0, "preco_max": 48.99, "custo": 3.28},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 3.88},
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 12.35},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 14.35},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 16.45},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 18.45},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 20.95},
    ],
    "500g a 1kg": [
        {"preco_min": 0.0, "preco_max": 18.99, "custo": 3.03},
        {"preco_min": 19.0, "preco_max": 48.99, "custo": 3.38},
        {"preco_min": 49.0, "preco_max": 78.99, "custo": 3.98},
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 13.85},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 16.15},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 18.45},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 20.75},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 23.65},
    ],
}

# 4. Taxa Fixa Flex e Logística Própria (Preço <= 79)
MERCADO_LIVRE_TAXA_FIXA_FLEX_2026 = {
    "Geral": [
        {"preco_min": 0.0, "preco_max": 18.99, "taxa_fixa": 6.25},
        {"preco_min": 19.0, "preco_max": 48.99, "taxa_fixa": 6.65},
        {"preco_min": 49.0, "preco_max": 78.99, "taxa_fixa": 7.75},
        {"preco_min": 79.0, "preco_max": float('inf'), "taxa_fixa": 0.0},
    ],
    "Livros": [
        {"preco_min": 0.0, "preco_max": 18.99, "taxa_fixa": 3.00},
        {"preco_min": 19.0, "preco_max": 48.99, "taxa_fixa": 3.50},
        {"preco_min": 49.0, "preco_max": 78.99, "taxa_fixa": 4.50},
        {"preco_min": 79.0, "preco_max": float('inf'), "taxa_fixa": 0.0},
    ],
}

# 5. Frete Grátis Full (Preço >= 79)
MERCADO_LIVRE_FRETE_GRATIS_FULL_2026 = {
    "Até 300g": [
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 11.97},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 14.35},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 16.45},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 18.45},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 19.95},
    ],
    "300g a 500g": [
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 12.87},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 15.45},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 17.65},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 19.85},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 21.45},
    ],
    "500g a 1kg": [
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 13.47},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 16.15},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 18.45},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 20.75},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 22.45},
    ],
    "1kg a 2kg": [
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 14.07},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 16.85},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 19.25},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 21.65},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 23.45},
    ],
    "2kg a 3kg": [
        {"preco_min": 79.0, "preco_max": 99.99, "custo": 14.97},
        {"preco_min": 100.0, "preco_max": 119.99, "custo": 17.85},
        {"preco_min": 120.0, "preco_max": 149.99, "custo": 20.25},
        {"preco_min": 150.0, "preco_max": 199.99, "custo": 22.65},
        {"preco_min": 200.0, "preco_max": float('inf'), "custo": 24.95},
    ],
}

# 6. Comissões por Categoria 2026
MERCADO_LIVRE_COMISSAO_CATEGORIA_2026 = {
    "Acessórios para Veículos": {"classico": 0.12, "premium": 0.17},
    "Agro": {"classico": 0.115, "premium": 0.165},
    "Alimentos e Bebidas": {"classico": 0.14, "premium": 0.19},
    "Antiguidades e Coleções": {"classico": 0.115, "premium": 0.165},
    "Arte, Papelaria e Armarinho": {"classico": 0.115, "premium": 0.165},
    "Bebês": {"classico": 0.14, "premium": 0.19},
    "Beleza e Cuidado Pessoal": {"classico": 0.14, "premium": 0.19},
    "Brinquedos e Hobbies": {"classico": 0.115, "premium": 0.165},
    "Calçados, Roupas e Bolsas": {"classico": 0.14, "premium": 0.19},
    "Câmeras e Acessórios": {"classico": 0.11, "premium": 0.16},
    "Casa, Móveis e Decoração": {"classico": 0.115, "premium": 0.165},
    "Construção": {"classico": 0.115, "premium": 0.165},
    "Eletrodomésticos": {"classico": 0.11, "premium": 0.16},
    "Eletrônicos, Áudio e Vídeo": {"classico": 0.13, "premium": 0.18},
    "Esportes e Fitness": {"classico": 0.14, "premium": 0.19},
    "Festas e Lembrancinhas": {"classico": 0.115, "premium": 0.165},
    "Games": {"classico": 0.13, "premium": 0.18},
    "Informática": {"classico": 0.11, "premium": 0.16},
    "Indústria e Comércio": {"classico": 0.12, "premium": 0.17},
    "Ingressos": {"classico": 0.115, "premium": 0.165},
    "Livros": {"classico": 0.065, "premium": 0.115},
    "Moda Fitness": {"classico": 0.14, "premium": 0.19},
    "Móveis": {"classico": 0.115, "premium": 0.165},
    "Pet Shop": {"classico": 0.14, "premium": 0.19},
    "Saúde": {"classico": 0.12, "premium": 0.17},
    "Supermercado": {"classico": 0.14, "premium": 0.19},
    "Telefonia": {"classico": 0.13, "premium": 0.18},
    "Viagens": {"classico": 0.115, "premium": 0.165},
}

# 7. Custos Operacionais Adicionais
MERCADO_LIVRE_CUSTOS_ADICIONAIS = {
    "armazenamento_full_aumento": 0.076,
    "retirada_estoque_full_aumento": 0.05,
    "estoque_antigo_aumento": 0.064,
    "diferenca_estoque_alta": 9.0,
    "diferenca_estoque_baixa": 3.0,
}

# ============================================================================
# OUTROS MARKETPLACES E CONFIGURAÇÕES GERAIS
# ============================================================================

SHOPEE_FAIXAS_PRECO = [
    {"min": 0.0, "max": 79.99, "comissao_percent": 0.20, "comissao_fixa": 4.0, "subsidio_pix_percent": 0.0, "descricao": "Ate R$ 79,99"},
    {"min": 80.0, "max": 99.99, "comissao_percent": 0.14, "comissao_fixa": 16.0, "subsidio_pix_percent": 0.05, "descricao": "R$ 80,00 - R$ 99,99"},
    {"min": 100.0, "max": 199.99, "comissao_percent": 0.14, "comissao_fixa": 20.0, "subsidio_pix_percent": 0.05, "descricao": "R$ 100,00 - R$ 199,99"},
    {"min": 200.0, "max": 499.99, "comissao_percent": 0.14, "comissao_fixa": 26.0, "subsidio_pix_percent": 0.05, "descricao": "R$ 200,00 - R$ 499,99"},
    {"min": 500.0, "max": float('inf'), "comissao_percent": 0.14, "comissao_fixa": 26.0, "subsidio_pix_percent": 0.08, "descricao": "Acima de R$ 500,00"},
]

DEFAULT_REGIMES = {
    "Simples Nacional": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.04},
    "Lucro Presumido": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.13},
    "Lucro Real": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.18},
    "MEI": {"ibs": 0.0, "cbs": 0.0, "impostos_encargos": 0.0},
}

CURVA_ABC_LIMITS = {"A": 0.80, "B": 0.95, "C": 1.00}
STATUS_SAUDAVEL = "🟢 Saudável"
STATUS_ALERTA = "🟡 Alerta"
STATUS_PREJUIZO = "🔴 Prejuízo/Abaixo"

MERCADO_LIVRE_COLUMNS = ["SKU", "Título", "Custo Produto", "Frete", "Preço Atual", "Tipo de Anúncio"]
BASE_DADOS_COLUMNS = ["SKU/MLB", "Descrição", "Marketplace", "Regime Tributário", "Custo Produto (R$)", "Frete (R$)", "Preço Base (R$)", "Vendas/Mês", "Curva ABC", "Margem Bruta (%)", "Margem Líquida (%)", "Publicidade (%)"]
