"""
Módulo aprimorado para cálculo de custos do Mercado Livre 2026
Integra as novas regras de precificação do arquivo Analise_Mercado_Livre_2026.xlsx
"""

from config import (
    MERCADO_LIVRE_CUSTO_OPERACIONAL_FULL_2026,
    MERCADO_LIVRE_CUSTO_OPERACIONAL_SUPERMERCADO_2026,
    MERCADO_LIVRE_CUSTO_OPERACIONAL_LIVROS_2026,
    MERCADO_LIVRE_TAXA_FIXA_FLEX_2026,
    MERCADO_LIVRE_FRETE_GRATIS_FULL_2026,
    MERCADO_LIVRE_REGRAS_CUSTO_FIXO,
    MERCADO_LIVRE_COMISSAO_CATEGORIA_2026,
    MERCADO_LIVRE_CUSTOS_ADICIONAIS,
    MERCADO_LIVRE_LIMITE_TAXA_FIXA,
    MERCADO_LIVRE_LIMITE_CUSTO_FIXO_BAIXO,
    MERCADO_LIVRE_LIMITE_CUSTO_OPERACIONAL_GERAL,
    MERCADO_LIVRE_LIMITE_CUSTO_OPERACIONAL_SUPERMERCADO,
)


class MercadoLivreCostsCalculator:
    """
    Calculadora de custos do Mercado Livre 2026 com suporte às novas regras
    """

    @staticmethod
    def _encontrar_faixa_peso(peso_kg):
        """
        Encontra a faixa de peso correspondente para o produto
        
        Args:
            peso_kg: Peso do produto em kg
            
        Returns:
            String com a faixa de peso (ex: "Até 0,3 kg", "0,3 a 0,5 kg")
        """
        if peso_kg <= 0.3:
            return "Até 300g"
        elif peso_kg <= 0.5:
            return "300g a 500g"
        elif peso_kg <= 1.0:
            return "500g a 1kg"
        elif peso_kg <= 2.0:
            return "1kg a 2kg"
        elif peso_kg <= 3.0:
            return "2kg a 3kg"
        else:
            return "2kg a 3kg"  # Padrão para pesos maiores

    @staticmethod
    def _encontrar_custo_por_preco(tabela_faixas, preco):
        """
        Encontra o custo correspondente à faixa de preço
        
        Args:
            tabela_faixas: Lista de dicts com preco_min, preco_max e custo (ou taxa_fixa)
            preco: Preço do produto
            
        Returns:
            Float com o custo encontrado, ou None se não encontrado
        """
        for faixa in tabela_faixas:
            if faixa["preco_min"] <= preco <= faixa["preco_max"]:
                # Tenta encontrar 'custo' primeiro, depois 'taxa_fixa'
                if "custo" in faixa:
                    return faixa["custo"]
                elif "taxa_fixa" in faixa:
                    return faixa["taxa_fixa"]
        return None

    @staticmethod
    def calcular_comissao_categoria(categoria, tipo_anuncio="Clássico"):
        """
        Calcula a comissão baseada na categoria e tipo de anúncio
        
        Args:
            categoria: Categoria do produto
            tipo_anuncio: "Clássico" ou "Premium"
            
        Returns:
            Float com a taxa de comissão (ex: 0.14 para 14%)
        """
        tipo_key = "classico" if tipo_anuncio.lower() == "clássico" else "premium"
        
        if categoria in MERCADO_LIVRE_COMISSAO_CATEGORIA_2026:
            return MERCADO_LIVRE_COMISSAO_CATEGORIA_2026[categoria].get(tipo_key, 0.14)
        
        # Padrão se categoria não encontrada
        return 0.14 if tipo_key == "classico" else 0.19

    @staticmethod
    def calcular_custo_operacional_full(preco, peso_kg=0.0, categoria="Geral"):
        """
        Calcula o custo operacional para logística Full, Coleta e Agências
        Aplicado quando preço <= R$ 79
        
        Args:
            preco: Preço do produto
            peso_kg: Peso do produto em kg (padrão: 0.0 = até 300g)
            categoria: "Geral", "Livros" ou "Supermercado"
            
        Returns:
            Float com o custo operacional
        """
        # Se preço >= 79, retorna 0 (paga frete, não custo fixo)
        if preco >= MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return 0.0
        
        # Se peso não informado, assume a faixa mínima (até 300g)
        if peso_kg is None or peso_kg <= 0:
            peso_kg = 0.15  # Meio da faixa "Até 300g"
        
        # Seleciona a tabela apropriada
        if categoria.lower() == "livros":
            tabela = MERCADO_LIVRE_CUSTO_OPERACIONAL_LIVROS_2026
        elif categoria.lower() == "supermercado":
            tabela = MERCADO_LIVRE_CUSTO_OPERACIONAL_SUPERMERCADO_2026
        else:
            tabela = MERCADO_LIVRE_CUSTO_OPERACIONAL_FULL_2026
        
        # Encontra a faixa de peso
        faixa_peso = MercadoLivreCostsCalculator._encontrar_faixa_peso(peso_kg)
        
        if faixa_peso not in tabela:
            return 0.0
        
        # Encontra o custo para a faixa de preço
        custo = MercadoLivreCostsCalculator._encontrar_custo_por_preco(
            tabela[faixa_peso], preco
        )
        
        if custo is None:
            return 0.0
        
        # Aplica regra de limite de custo fixo para produtos muito baratos
        if preco < MERCADO_LIVRE_LIMITE_CUSTO_FIXO_BAIXO:
            custo_maximo = preco * MERCADO_LIVRE_REGRAS_CUSTO_FIXO["abaixo_12_50"]
            custo = min(custo, custo_maximo)
        
        # Aplica limite de 50% para produtos < R$ 19 (Geral)
        if categoria.lower() != "supermercado" and preco < MERCADO_LIVRE_LIMITE_CUSTO_OPERACIONAL_GERAL:
            custo_maximo = preco * MERCADO_LIVRE_REGRAS_CUSTO_FIXO["abaixo_19_geral"]
            custo = min(custo, custo_maximo)
        
        # Aplica limite de 25% para produtos < R$ 29 (Supermercado)
        if categoria.lower() == "supermercado" and preco < MERCADO_LIVRE_LIMITE_CUSTO_OPERACIONAL_SUPERMERCADO:
            custo_maximo = preco * MERCADO_LIVRE_REGRAS_CUSTO_FIXO["abaixo_29_supermercado"]
            custo = min(custo, custo_maximo)
        
        return custo

    @staticmethod
    def calcular_taxa_fixa_flex(preco, categoria="Geral"):
        """
        Calcula a taxa fixa para logística Flex, Retirada e Logística Própria
        Aplicado quando preço <= R$ 79
        
        Args:
            preco: Preço do produto
            categoria: "Geral" ou "Livros"
            
        Returns:
            Float com a taxa fixa
        """
        # Se preço >= 79, retorna 0 (isento)
        if preco >= MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return 0.0
        
        # Seleciona a tabela apropriada
        tipo_categoria = "Livros" if categoria.lower() == "livros" else "Geral"
        tabela = MERCADO_LIVRE_TAXA_FIXA_FLEX_2026[tipo_categoria]
        
        # Encontra o custo para a faixa de preço
        taxa = MercadoLivreCostsCalculator._encontrar_custo_por_preco(tabela, preco)
        
        return taxa if taxa is not None else 0.0

    @staticmethod
    def calcular_frete_gratis_full(preco, peso_kg=0.0):
        """
        Calcula o custo de frete para logística Full quando preço >= R$ 79
        
        Args:
            preco: Preço do produto
            peso_kg: Peso do produto em kg (padrão: 0.0 = até 300g)
            
        Returns:
            Float com o custo de frete
        """
        # Se preço < 79, retorna 0 (paga custo operacional, não frete)
        if preco < MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return 0.0
        
        # Se peso não informado, assume a faixa mínima (até 300g)
        if peso_kg is None or peso_kg <= 0:
            peso_kg = 0.15  # Meio da faixa "Até 300g"
        
        # Encontra a faixa de peso
        faixa_peso = MercadoLivreCostsCalculator._encontrar_faixa_peso(peso_kg)
        
        if faixa_peso not in MERCADO_LIVRE_FRETE_GRATIS_FULL_2026:
            return 0.0
        
        # Encontra o custo para a faixa de preço
        custo = MercadoLivreCostsCalculator._encontrar_custo_por_preco(
            MERCADO_LIVRE_FRETE_GRATIS_FULL_2026[faixa_peso], preco
        )
        
        return custo if custo is not None else 0.0

    @staticmethod
    def calcular_custo_total_ml(preco, peso_kg, tipo_logistica, categoria="Geral", tipo_anuncio="Clássico"):
        """
        Calcula o custo total do Mercado Livre (comissão + custo operacional/frete)
        
        Args:
            preco: Preço do produto
            peso_kg: Peso do produto em kg
            tipo_logistica: "Full" ou "Flex"
            categoria: Categoria do produto
            tipo_anuncio: "Clássico" ou "Premium"
            
        Returns:
            Dict com breakdown de custos:
            {
                "comissao": float,
                "custo_operacional": float,
                "frete": float,
                "custo_total": float,
                "detalhes": str
            }
        """
        # Calcula comissão
        comissao_taxa = MercadoLivreCostsCalculator.calcular_comissao_categoria(categoria, tipo_anuncio)
        comissao = preco * comissao_taxa
        
        # Calcula custo operacional ou frete
        if tipo_logistica.lower() == "flex":
            # Logística Flex: taxa fixa
            custo_operacional = MercadoLivreCostsCalculator.calcular_taxa_fixa_flex(preco, categoria)
            frete = 0.0
            detalhes = f"Flex - Taxa Fixa: R$ {custo_operacional:.2f}"
        else:
            # Logística Full: custo operacional ou frete
            if preco < MERCADO_LIVRE_LIMITE_TAXA_FIXA:
                custo_operacional = MercadoLivreCostsCalculator.calcular_custo_operacional_full(
                    preco, peso_kg, categoria
                )
                frete = 0.0
                detalhes = f"Full - Custo Operacional: R$ {custo_operacional:.2f}"
            else:
                custo_operacional = 0.0
                frete = MercadoLivreCostsCalculator.calcular_frete_gratis_full(preco, peso_kg)
                detalhes = f"Full - Frete: R$ {frete:.2f}"
        
        custo_total = comissao + custo_operacional + frete
        
        return {
            "comissao": comissao,
            "comissao_taxa": comissao_taxa,
            "custo_operacional": custo_operacional,
            "frete": frete,
            "custo_total": custo_total,
            "detalhes": detalhes,
        }


# Função auxiliar para compatibilidade com código existente
def calcular_custo_total_ml_simples(preco, peso_kg=0.3, tipo_logistica="Full", categoria="Geral"):
    """
    Função simplificada para cálculo de custo total
    """
    calc = MercadoLivreCostsCalculator()
    resultado = calc.calcular_custo_total_ml(preco, peso_kg, tipo_logistica, categoria)
    return resultado["custo_total"]
