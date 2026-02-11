
"""
Configurações e constantes do aplicativo de precificação Carblue
"""

# Configurações padrão de Marketplaces
DEFAULT_MARKETPLACES = {
    "Mercado Livre": {"comissao": 0.14, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Shopee": {"comissao": 0.20, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Amazon": {"comissao": 0.15, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Magalu": {"comissao": 0.18, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
    "Outros": {"comissao": 0.18, "custo_fixo": 0.0, "taxa_devolucao": 0.02},
}

# Configurações de tipos de anúncio para Mercado Livre
MERCADO_LIVRE_AD_TYPES = {
    "Clássico": {"comissao": 0.14, "custo_fixo": 0.0},
    "Premium": {"comissao": 0.19, "custo_fixo": 0.0},
}

# Novas Comissões do Mercado Livre por Categoria (2026)
MERCADO_LIVRE_COMISSOES_POR_CATEGORIA_2026 = {
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
    "Instrumentos Musicais": {"classico": 0.115, "premium": 0.165},
    "Joias e Relógios": {"classico": 0.125, "premium": 0.175},
    "Livros, Revistas e Comics": {"classico": 0.12, "premium": 0.17},
    "Música, Filmes e Seriados": {"classico": 0.12, "premium": 0.17},
    "Pet Shop": {"classico": 0.125, "premium": 0.175},
    "Saúde": {"classico": 0.12, "premium": 0.17}
}

# Novas Tabelas de Custo Operacional do Mercado Livre (2026) - Dados exatos da aba Geral (Full-Coleta-Ag)
MERCADO_LIVRE_CUSTO_OPERACIONAL_GERAL_2026 = [
    {'Peso': 'Até 0,3 kg', 'R$ 0-18,99': 5.65, 'R$ 19-48,99': 6.55, 'R$ 49-78,99': 7.75, 'R$ 79-99,99': 12.35, 'R$ 100-119,99': 14.35, 'R$ 120-149,99': 16.45, 'R$ 150-199,99': 18.45, 'A partir de R$ 200': 20.95},
    {'Peso': '0,3 a 0,5 kg', 'R$ 0-18,99': 5.95, 'R$ 19-48,99': 6.65, 'R$ 49-78,99': 7.85, 'R$ 79-99,99': 13.25, 'R$ 100-119,99': 15.45, 'R$ 120-149,99': 17.65, 'R$ 150-199,99': 19.85, 'A partir de R$ 200': 22.55},
    {'Peso': '0,5 a 1 kg', 'R$ 0-18,99': 6.05, 'R$ 19-48,99': 6.75, 'R$ 49-78,99': 7.95, 'R$ 79-99,99': 13.85, 'R$ 100-119,99': 16.15, 'R$ 120-149,99': 18.45, 'R$ 150-199,99': 20.75, 'A partir de R$ 200': 23.65},
    {'Peso': '1 a 2 kg', 'R$ 0-18,99': 6.25, 'R$ 19-48,99': 6.95, 'R$ 49-78,99': 8.15, 'R$ 79-99,99': 14.45, 'R$ 100-119,99': 16.85, 'R$ 120-149,99': 19.25, 'R$ 150-199,99': 21.65, 'A partir de R$ 200': 24.65},
]

MERCADO_LIVRE_LIVROS_2026 = [
    {'Peso': 'Até 0,3 kg', 'R$ 0-18,99': 2.83, 'R$ 19-48,99': 3.28, 'R$ 49-78,99': 3.88, 'R$ 79-99,99': 12.35, 'R$ 100-119,99': 14.35, 'R$ 120-149,99': 16.45, 'R$ 150-199,99': 18.45, 'A partir de R$ 200': 20.95},
    {'Peso': '0,5 a 1 kg', 'R$ 0-18,99': 3.03, 'R$ 19-48,99': 3.38, 'R$ 49-78,99': 3.98, 'R$ 79-99,99': 13.85, 'R$ 100-119,99': 16.15, 'R$ 120-149,99': 18.45, 'R$ 150-199,99': 20.75, 'A partir de R$ 200': 23.65},
]

MERCADO_LIVRE_SUPERMERCADO_2026 = [
    {'Peso': 'Até 0,3 kg', 'R$ 0-18,99': 1.25, 'R$ 19-28,99': 1.5, 'R$ 29-48,99': 2, 'R$ 49-78,99': 3, 'R$ 79-98,99': 4, 'R$ 99-198,99': 6, 'A partir de R$ 199': 20.95},
    {'Peso': '0,5 a 1 kg', 'R$ 0-18,99': 1.25, 'R$ 19-28,99': 1.5, 'R$ 29-48,99': 2, 'R$ 49-78,99': 3, 'R$ 79-98,99': 4, 'R$ 99-198,99': 6, 'A partir de R$ 199': 23.65},
]

# Limite para aplicacao de frete grátis
MERCADO_LIVRE_LIMITE_FRETE_GRATIS = 79.0

# Tabelas de Comissao e Subsidio Pix da Shopee por Faixa de Preco (2025)
SHOPEE_FAIXAS_PRECO = [
    {"min": 0.0, "max": 79.99, "comissao_percent": 0.20, "comissao_fixa": 4.0, "subsidio_pix_percent": 0.0, "descricao": "Ate R$ 79,99"},
    {"min": 80.0, "max": 99.99, "comissao_percent": 0.14, "comissao_fixa": 16.0, "subsidio_pix_percent": 0.05, "descricao": "R$ 80,00 - R$ 99,99"},
    {"min": 100.0, "max": 199.99, "comissao_percent": 0.14, "comissao_fixa": 20.0, "subsidio_pix_percent": 0.05, "descricao": "R$ 100,00 - R$ 199,99"},
    {"min": 200.0, "max": 499.99, "comissao_percent": 0.14, "comissao_fixa": 26.0, "subsidio_pix_percent": 0.05, "descricao": "R$ 200,00 - R$ 499,99"},
    {"min": 500.0, "max": float('inf'), "comissao_percent": 0.14, "comissao_fixa": 26.0, "subsidio_pix_percent": 0.08, "descricao": "Acima de R$ 500,00"},
]

# Configurações de Regimes Tributários
DEFAULT_REGIMES = {
    "Simples Nacional": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.04},
    "Lucro Presumido": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.13},
    "Lucro Real": {"ibs": 0.001, "cbs": 0.009, "impostos_encargos": 0.18},
    "MEI": {"ibs": 0.0, "cbs": 0.0, "impostos_encargos": 0.0},
}

# Custos Operacionais
DEFAULT_CUSTO_FIXO_OPERACIONAL = 0.0
DEFAULT_TAXA_DEVOLUCAO = 0.0

# Limites de Curva ABC
CURVA_ABC_LIMITS = {"A": 0.80, "B": 0.95, "C": 1.00}

# Status de Saúde da Precificação
STATUS_SAUDAVEL = "🟢 Saudável"
STATUS_ALERTA = "🟡 Alerta"
STATUS_PREJUIZO = "🔴 Prejuízo/Abaixo"

# Colunas esperadas no relatório do Mercado Livre
MERCADO_LIVRE_COLUMNS = ["SKU", "Título", "Custo Produto", "Frete", "Preço Atual", "Tipo de Anúncio"]

# Colunas da Base de Dados interna
BASE_DADOS_COLUMNS = ["SKU/MLB", "Descrição", "Marketplace", "Regime Tributário", "Custo Produto (R$)", "Frete (R$)", "Preço Base (R$)", "Vendas/Mês", "Curva ABC", "Margem Bruta (%)", "Margem Líquida (%)", "Publicidade (%)"]
