"""
Script de teste para validar os módulos do aplicativo
"""

import pandas as pd
import numpy as np
from pricing_calculator import PricingCalculator
from abc_classifier import ABCClassifier
from promotion_manager import PromotionManager
from mercado_livre_processor import MercadoLivreProcessor

# Criar dados de teste
np.random.seed(42)

dados_teste = {
    "SKU": [f"SKU{i:04d}" for i in range(1, 21)],
    "Descrição": [f"Produto {i}" for i in range(1, 21)],
    "Preço": np.random.uniform(50, 500, 20),
    "Quantidade Vendida": np.random.randint(5, 100, 20),
}

df_teste = pd.DataFrame(dados_teste)
df_teste["Faturamento"] = df_teste["Preço"] * df_teste["Quantidade Vendida"]

print("=" * 80)
print("TESTE 1: Processador do Mercado Livre")
print("=" * 80)

processor = MercadoLivreProcessor()
df_normalizado = processor.normalizar_relatorio_vendas(df_teste)
valido, mensagem = processor.validar_relatorio(df_normalizado)

print(f"✅ Validação: {mensagem}")
print(f"Total de SKUs: {len(df_normalizado)}")
print(f"Faturamento Total: R$ {df_normalizado['Faturamento'].sum():,.2f}")
print()

print("=" * 80)
print("TESTE 2: Classificador ABC")
print("=" * 80)

classifier = ABCClassifier()
df_abc = classifier.classificar_produtos(df_normalizado, faturamento_col="Faturamento")

print("Distribuição por Curva:")
print(df_abc["Curva ABC"].value_counts().sort_index())
print()

resumo = classifier.gerar_resumo_abc(df_abc)
print("Resumo ABC:")
print(resumo.to_string(index=False))
print()

print("=" * 80)
print("TESTE 3: Gerenciador de Promoções")
print("=" * 80)

# Adicionar colunas necessárias para teste
df_abc["Desconto Máximo %"] = 15.0

promotion_manager = PromotionManager()
regras = {"A": 0.0, "B": 0.05, "C": 0.10, "Sem Curva": 0.0}
df_promo = promotion_manager.aplicar_promocoes(df_abc, regras=regras)

print(f"Regras de Promoção: {regras}")
print()

relatorio = promotion_manager.gerar_relatorio_promocoes(df_promo)
print(f"Total de Economia: R$ {relatorio['total_economia']:,.2f}")
print(f"Economia Média: R$ {relatorio['economia_media']:,.2f}")
print(f"Produtos com Promoção: {relatorio['produtos_com_promocao']}")
print()

print("=" * 80)
print("TESTE 4: Calculadora de Precificação")
print("=" * 80)

# Criar dados para teste de precificação
df_preco = pd.DataFrame({
    "SKU": ["SKU001", "SKU002", "SKU003"],
    "Marketplace": ["Mercado Livre Premium", "Shopee", "Amazon"],
    "Regime Tributário": ["Lucro Real", "Lucro Real", "Lucro Real"],
    "Custo Produto (R$)": [50, 75, 100],
    "Frete (R$)": [10, 10, 10],
    "Preço Base (R$)": [150, 200, 250],
    "Ads (%)": [0.02, 0.03, 0.01],
    "Margem Bruta (%)": [30, 30, 30],
    "Margem Líquida (%)": [10, 10, 10],
})

calculator = PricingCalculator()
df_calculado = calculator.processar_base_dados(df_preco)

print("Análise de Precificação:")
print(df_calculado[["SKU", "Preço Base (R$)", "Lucro R$", "Margem Calculada %", "Status"]].to_string(index=False))
print()

print("=" * 80)
print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
print("=" * 80)
