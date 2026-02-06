"""
Módulo para Calculadora de Precificação
Implementa a lógica da aba Calculadora_Precificacao da planilha V3
"""

import pandas as pd
import numpy as np


class PricingCalculatorV2:
    """Calcula precificação e margens de produtos."""

    def __init__(self, marketplaces, regimes, margem_bruta_alvo, margem_liquida_minima):
        """
        Inicializa a calculadora
        
        Args:
            marketplaces: Dict com configurações de marketplaces
            regimes: Dict com configurações de regimes tributários
            margem_bruta_alvo: Margem bruta alvo (%)
            margem_liquida_minima: Margem líquida mínima (%)
        """
        self.marketplaces = marketplaces
        self.regimes = regimes
        self.margem_bruta_alvo = margem_bruta_alvo
        self.margem_liquida_minima = margem_liquida_minima

    def calcular_linha(self, sku, marketplace, preco_venda, custo_produto, frete, 
                       regime_tributario, ads_percent):
        """
        Calcula uma linha da Calculadora de Precificação
        
        Args:
            sku: SKU do produto
            marketplace: Nome do marketplace
            preco_venda: Preço de venda (R$)
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            regime_tributario: Regime tributário
            ads_percent: Percentual de Ads (%)
            
        Returns:
            Dict com todos os cálculos
        """
        # Obter configurações
        mp_config = self.marketplaces.get(marketplace, {})
        comissao_percent = mp_config.get("comissao", 0.0)
        taxa_fixa = mp_config.get("custo_fixo", 0.0)
        
        regime_config = self.regimes.get(regime_tributario, {})
        impostos_percent = regime_config.get("impostos_encargos", 0.0)
        
        # Cálculos
        comissao = preco_venda * comissao_percent if preco_venda > 0 else 0
        impostos = preco_venda * impostos_percent if preco_venda > 0 else 0
        ads = preco_venda * (ads_percent / 100) if preco_venda > 0 else 0
        
        # Lucro
        lucro_r = preco_venda - custo_produto - frete - comissao - taxa_fixa - impostos - ads
        
        # Margem
        margem_percent = (lucro_r / preco_venda * 100) if preco_venda > 0 else 0
        
        # Desconto máximo
        desconto_max = max(0, margem_percent - self.margem_bruta_alvo)
        
        # Status
        if margem_percent < self.margem_liquida_minima:
            status = "🔴 Prejuízo/Abaixo"
        elif margem_percent < self.margem_bruta_alvo:
            status = "🟡 Alerta"
        else:
            status = "🟢 Saudável"
        
        return {
            "SKU": sku,
            "Marketplace": marketplace,
            "Preço Venda (R$)": preco_venda,
            "Custo Prod": custo_produto,
            "Frete": frete,
            "Comissão": comissao,
            "Taxa Fixa": taxa_fixa,
            "Impostos": impostos,
            "Ads": ads,
            "Lucro R$": lucro_r,
            "Margem %": margem_percent,
            "Desconto Máx. (%)": desconto_max,
            "Status": status,
        }

    def calcular_dataframe(self, df):
        """
        Calcula múltiplas linhas
        
        Args:
            df: DataFrame com colunas: SKU, Marketplace, Preço Venda, Custo Produto, 
                Frete, Regime Tributário, Ads (%)
                
        Returns:
            DataFrame com todos os cálculos
        """
        resultados = []
        
        for _, row in df.iterrows():
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                marketplace=row.get("Marketplace", ""),
                preco_venda=float(row.get("Preço Venda (R$)", 0) or 0),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                regime_tributario=row.get("Regime Tributário", ""),
                ads_percent=float(row.get("Ads (%)", 0) or 0),
            )
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)
