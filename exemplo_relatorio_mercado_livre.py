"""
Script para gerar arquivo de exemplo do Mercado Livre para teste
"""

import pandas as pd
import numpy as np

# Definir seed para reproduzibilidade
np.random.seed(42)

# Criar dados de exemplo
n_produtos = 30

dados = {
    "SKU": [f"MLB{np.random.randint(100000000, 999999999)}" for _ in range(n_produtos)],
    "Título": [
        "Carro Miniatura 1:64",
        "Carro Miniatura 1:43",
        "Carro Miniatura 1:18",
        "Carro Diecast Premium",
        "Carro Clássico Vintage",
        "Carro Esportivo Vermelho",
        "Carro Azul Metalizado",
        "Carro Preto Fosco",
        "Carro Amarelo Brilhante",
        "Carro Branco Pérola",
        "Carro Verde Musgo",
        "Carro Laranja Queimado",
        "Carro Rosa Pastel",
        "Carro Roxo Escuro",
        "Carro Cinza Chumbo",
        "Carro Marrom Chocolate",
        "Carro Dourado Luxo",
        "Carro Prata Espelhado",
        "Carro Cobre Antigo",
        "Carro Titânio Moderno",
        "Carro Camaleão Especial",
        "Carro Neon Fluorescente",
        "Carro Holográfico",
        "Carro Matte Black",
        "Carro Candy Red",
        "Carro Midnight Blue",
        "Carro Forest Green",
        "Carro Sunset Orange",
        "Carro Pearl White",
        "Carro Charcoal Grey",
    ],
    "Preço": np.random.uniform(45, 350, n_produtos),
    "Quantidade Vendida": np.random.randint(3, 150, n_produtos),
}

df = pd.DataFrame(dados)
df["Faturamento"] = df["Preço"] * df["Quantidade Vendida"]

# Ordenar por faturamento decrescente para simular dados reais
df = df.sort_values("Faturamento", ascending=False).reset_index(drop=True)

# Salvar como Excel
output_path = "/home/ubuntu/carblue-streamlit/exemplo_relatorio.xlsx"
df.to_excel(output_path, index=False, sheet_name="Vendas")

print(f"✅ Arquivo de exemplo criado: {output_path}")
print(f"Total de produtos: {len(df)}")
print(f"Faturamento total: R$ {df['Faturamento'].sum():,.2f}")
print()
print("Primeiros 10 produtos:")
print(df[["SKU", "Título", "Preço", "Quantidade Vendida", "Faturamento"]].head(10).to_string(index=False))
