"""
Módulo para Simulador de Preço Alvo
Implementa a lógica da aba Simulador_Preco_Alvo da planilha V3
"""

import pandas as pd
import numpy as np


class PriceSimulator:
    """Simula preços alvo baseado em margens desejadas."""

    def __init__(self, marketplaces, regimes, margem_liquida_minima):
        """
        Inicializa o simulador
        
        Args:
            marketplaces: Dict com configurações de marketplaces
            regimes: Dict com configurações de regimes tributários
            margem_liquida_minima: Margem líquida mínima (%)
        """
        self.marketplaces = marketplaces
        self.regimes = regimes
        self.margem_liquida_minima = margem_liquida_minima

    def calcular_linha(self, sku, custo_produto, frete, taxa_fixa, 
                       comissao_percent, impostos_percent, ads_percent, 
                       margem_alvo_percent):
        """
        Calcula uma linha do Simulador de Preço Alvo
        
        Args:
            sku: SKU do produto
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            taxa_fixa: Taxa fixa (R$)
            comissao_percent: Percentual de comissão (%)
            impostos_percent: Percentual de impostos (%)
            ads_percent: Percentual de ads (%)
            margem_alvo_percent: Margem alvo desejada (%)
            
        Returns:
            Dict com simulação de preço
        """
        # Custo total direto
        custo_total_direto = custo_produto + frete + taxa_fixa
        
        # Taxas variáveis (em decimal)
        taxas_variaveis = (comissao_percent + impostos_percent + ads_percent) / 100
        
        # Margem alvo (em decimal)
        margem_alvo_decimal = margem_alvo_percent / 100
        
        # Preço sugerido = Custo / (1 - Taxas - Margem)
        denominador = 1 - taxas_variaveis - margem_alvo_decimal
        
        if denominador > 0 and custo_total_direto > 0:
            preco_sugerido = custo_total_direto / denominador
            lucro_estimado = preco_sugerido * margem_alvo_decimal
        else:
            preco_sugerido = 0
            lucro_estimado = 0
        
        # Preço promo limite (com margem mínima)
        margem_minima_decimal = self.margem_liquida_minima / 100
        denominador_promo = 1 - taxas_variaveis - margem_minima_decimal
        
        if denominador_promo > 0 and custo_total_direto > 0:
            preco_promo_limite = custo_total_direto / denominador_promo
            lucro_promo = preco_promo_limite * margem_minima_decimal
        else:
            preco_promo_limite = 0
            lucro_promo = 0
        
        return {
            "SKU": sku,
            "Custo Total Direto": custo_total_direto,
            "Taxas Variáveis %": taxas_variaveis * 100,
            "Margem Alvo %": margem_alvo_percent,
            "Preço Sugerido": preco_sugerido,
            "Lucro Estimado": lucro_estimado,
            "Preço Promo Limite": preco_promo_limite,
            "Lucro Promo": lucro_promo,
        }

    def calcular_dataframe(self, df, margem_alvo_percent):
        """
        Calcula múltiplas linhas
        
        Args:
            df: DataFrame com colunas: SKU, Custo Produto, Frete, Taxa Fixa,
                Comissão (%), Impostos (%), Ads (%)
            margem_alvo_percent: Margem alvo desejada (%)
                
        Returns:
            DataFrame com simulação de preços
        """
        resultados = []
        
        for _, row in df.iterrows():
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                taxa_fixa=float(row.get("Taxa Fixa", 0) or 0),
                comissao_percent=float(row.get("Comissão (%)", 0) or 0),
                impostos_percent=float(row.get("Impostos (%)", 0) or 0),
                ads_percent=float(row.get("Ads (%)", 0) or 0),
                margem_alvo_percent=margem_alvo_percent,
            )
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)

    def simular_preco_unico(self, sku, custo_produto, frete, taxa_fixa,
                           comissao_percent, impostos_percent, ads_percent,
                           margem_alvo_percent):
        """
        Simula preço para um único produto
        
        Args:
            sku: SKU do produto
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            taxa_fixa: Taxa fixa (R$)
            comissao_percent: Percentual de comissão (%)
            impostos_percent: Percentual de impostos (%)
            ads_percent: Percentual de ads (%)
            margem_alvo_percent: Margem alvo desejada (%)
            
        Returns:
            Dict com simulação
        """
        return self.calcular_linha(
            sku=sku,
            custo_produto=custo_produto,
            frete=frete,
            taxa_fixa=taxa_fixa,
            comissao_percent=comissao_percent,
            impostos_percent=impostos_percent,
            ads_percent=ads_percent,
            margem_alvo_percent=margem_alvo_percent,
        )
