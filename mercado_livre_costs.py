"""
Módulo para cálculo de custos operacionais e de frete do Mercado Livre (Válido a partir de 02/03/2026)
Implementa a nova lógica de custos baseada em peso e faixa de preço
"""

from config import (
    MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO,
    MERCADO_LIVRE_TAXA_FIXA_FLEX,
    MERCADO_LIVRE_FRETE_GRATIS_PESO,
    MERCADO_LIVRE_LIMITE_TAXA_FIXA,
)


class MercadoLivreCostsCalculator:
    """Calcula custos operacionais e de frete do Mercado Livre com base nas novas regras de março de 2026."""

    @staticmethod
    def calcular_custo_operacional_full(preco_venda, peso_kg, categoria="Produtos Comuns"):
        """
        Calcula o custo operacional para logística Full (Mercado Livre) quando preço <= R$ 79.
        
        Args:
            preco_venda: Preço de venda em R$
            peso_kg: Peso do produto em kg
            categoria: Categoria do produto ("Produtos Comuns" ou "Livros")
            
        Returns:
            dict com custo_operacional (valor em R$), faixa_peso e faixa_preco
        """
        # Se preço > 79, não há custo operacional (há frete grátis)
        if preco_venda > MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return {
                "custo_operacional": 0.0,
                "faixa_peso": "Acima de R$ 79",
                "faixa_preco": "N/A",
                "tipo": "Frete Grátis"
            }
        
        # Buscar categoria
        categorias = MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO.get(categoria)
        if not categorias:
            categorias = MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO.get("Produtos Comuns")
        
        # Encontrar faixa de peso
        for faixa_peso in categorias:
            if faixa_peso["peso_min_kg"] <= peso_kg < faixa_peso["peso_max_kg"]:
                # Encontrar faixa de preço dentro da faixa de peso
                for faixa_preco in faixa_peso["custos_por_faixa"]:
                    if preco_venda <= faixa_preco["preco_max"]:
                        return {
                            "custo_operacional": faixa_preco["custo"],
                            "faixa_peso": f"{faixa_peso['peso_min_kg']:.1f}kg - {faixa_peso['peso_max_kg']:.1f}kg",
                            "faixa_preco": f"Até R$ {faixa_preco['preco_max']:.2f}",
                            "tipo": "Custo Operacional"
                        }
        
        # Fallback: retornar o custo máximo da faixa de peso mais próxima
        if categorias:
            faixa_peso = categorias[-1]  # Última faixa
            faixa_preco = faixa_peso["custos_por_faixa"][-1]  # Última faixa de preço
            return {
                "custo_operacional": faixa_preco["custo"],
                "faixa_peso": f"{faixa_peso['peso_min_kg']:.1f}kg - {faixa_peso['peso_max_kg']:.1f}kg",
                "faixa_preco": f"Acima de R$ {faixa_preco['preco_max']:.2f}",
                "tipo": "Custo Operacional"
            }
        
        return {
            "custo_operacional": 0.0,
            "faixa_peso": "Não identificada",
            "faixa_preco": "N/A",
            "tipo": "Erro"
        }

    @staticmethod
    def calcular_taxa_fixa_flex(preco_venda, categoria="Produtos Comuns"):
        """
        Calcula a taxa fixa para logística Flex (própria) quando preço <= R$ 79.
        
        Args:
            preco_venda: Preço de venda em R$
            categoria: Categoria do produto ("Produtos Comuns" ou "Livros")
            
        Returns:
            dict com taxa_fixa (valor em R$), faixa_preco
        """
        # Se preço > 79, não há taxa fixa
        if preco_venda > MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return {
                "taxa_fixa": 0.0,
                "faixa_preco": "Acima de R$ 79",
                "tipo": "Sem Taxa"
            }
        
        # Buscar categoria
        categorias = MERCADO_LIVRE_TAXA_FIXA_FLEX.get(categoria)
        if not categorias:
            categorias = MERCADO_LIVRE_TAXA_FIXA_FLEX.get("Produtos Comuns")
        
        # Encontrar faixa de preço
        for faixa in categorias:
            if faixa["min"] <= preco_venda <= faixa["max"]:
                return {
                    "taxa_fixa": faixa["taxa_fixa"],
                    "faixa_preco": f"R$ {faixa['min']:.2f} - R$ {faixa['max']:.2f}",
                    "tipo": "Taxa Fixa Flex"
                }
        
        # Fallback
        return {
            "taxa_fixa": 0.0,
            "faixa_preco": "Não identificada",
            "tipo": "Erro"
        }

    @staticmethod
    def calcular_frete_gratis_full(preco_venda, peso_kg, categoria="Produtos Comuns"):
        """
        Calcula o custo de frete para logística Full quando preço >= R$ 79 (Frete Grátis).
        
        Args:
            preco_venda: Preço de venda em R$
            peso_kg: Peso do produto em kg
            categoria: Categoria do produto ("Produtos Comuns" ou "Livros")
            
        Returns:
            dict com custo_frete (valor em R$), faixa_peso, faixa_preco
        """
        # Se preço < 79, não há frete grátis
        if preco_venda < MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return {
                "custo_frete": 0.0,
                "faixa_peso": "Abaixo de R$ 79",
                "faixa_preco": "N/A",
                "tipo": "Custo Operacional"
            }
        
        # Buscar categoria
        categorias = MERCADO_LIVRE_FRETE_GRATIS_PESO.get(categoria)
        if not categorias:
            categorias = MERCADO_LIVRE_FRETE_GRATIS_PESO.get("Produtos Comuns")
        
        # Encontrar faixa de peso
        for faixa_peso in categorias:
            if faixa_peso["peso_min_kg"] <= peso_kg < faixa_peso["peso_max_kg"]:
                # Encontrar faixa de preço dentro da faixa de peso
                for faixa_preco in faixa_peso["custos_por_faixa"]:
                    if preco_venda <= faixa_preco["preco_max"]:
                        return {
                            "custo_frete": faixa_preco["custo"],
                            "faixa_peso": f"{faixa_peso['peso_min_kg']:.1f}kg - {faixa_peso['peso_max_kg']:.1f}kg",
                            "faixa_preco": f"Até R$ {faixa_preco['preco_max']:.2f}",
                            "tipo": "Frete Grátis"
                        }
        
        # Fallback: retornar o custo máximo da faixa de peso mais próxima
        if categorias:
            faixa_peso = categorias[-1]  # Última faixa
            faixa_preco = faixa_peso["custos_por_faixa"][-1]  # Última faixa de preço
            return {
                "custo_frete": faixa_preco["custo"],
                "faixa_peso": f"{faixa_peso['peso_min_kg']:.1f}kg - {faixa_peso['peso_max_kg']:.1f}kg",
                "faixa_preco": f"Acima de R$ {faixa_preco['preco_max']:.2f}",
                "tipo": "Frete Grátis"
            }
        
        return {
            "custo_frete": 0.0,
            "faixa_peso": "Não identificada",
            "faixa_preco": "N/A",
            "tipo": "Erro"
        }

    @staticmethod
    def calcular_custo_total_ml(preco_venda, peso_kg, tipo_logistica="Full", categoria="Produtos Comuns"):
        """
        Calcula o custo total (operacional ou taxa fixa) para o Mercado Livre.
        
        Args:
            preco_venda: Preço de venda em R$
            peso_kg: Peso do produto em kg
            tipo_logistica: Tipo de logística ("Full" ou "Flex")
            categoria: Categoria do produto ("Produtos Comuns" ou "Livros")
            
        Returns:
            dict com custo_total, detalhes de faixa e tipo
        """
        if tipo_logistica == "Full":
            if preco_venda <= MERCADO_LIVRE_LIMITE_TAXA_FIXA:
                return MercadoLivreCostsCalculator.calcular_custo_operacional_full(
                    preco_venda, peso_kg, categoria
                )
            else:
                return MercadoLivreCostsCalculator.calcular_frete_gratis_full(
                    preco_venda, peso_kg, categoria
                )
        elif tipo_logistica == "Flex":
            return MercadoLivreCostsCalculator.calcular_taxa_fixa_flex(
                preco_venda, categoria
            )
        else:
            return {
                "custo_total": 0.0,
                "faixa": "Tipo de logística inválido",
                "tipo": "Erro"
            }
