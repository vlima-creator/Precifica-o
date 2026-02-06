"""
Módulo para Calculadora de Precificação V2
Implementa a lógica automática baseada em dados do relatório
"""

import pandas as pd
import numpy as np


class PricingCalculatorV2:
    """Calcula precificação automática baseada em dados do relatório."""

    def __init__(self, marketplaces, regimes, margem_bruta_alvo, margem_liquida_minima, percent_publicidade):
        """
        Inicializa a calculadora
        
        Args:
            marketplaces: Dict com configurações de marketplaces
            regimes: Dict com configurações de regimes tributários
            margem_bruta_alvo: Margem bruta alvo (%)
            margem_liquida_minima: Margem líquida mínima (%)
            percent_publicidade: % de publicidade
        """
        self.marketplaces = marketplaces
        self.regimes = regimes
        self.margem_bruta_alvo = margem_bruta_alvo
        self.margem_liquida_minima = margem_liquida_minima
        self.percent_publicidade = percent_publicidade

    def calcular_linha(self, sku, descricao, custo_produto, frete, preco_atual, 
                       marketplace, regime_tributario):
        """
        Calcula uma linha da Calculadora de Precificação
        
        Args:
            sku: SKU do produto
            descricao: Descrição do produto
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            preco_atual: Preço atual (R$)
            marketplace: Nome do marketplace
            regime_tributario: Regime tributário
            
        Returns:
            Dict com todos os cálculos
        """
        # Obter configurações
        mp_config = self.marketplaces.get(marketplace, {})
        comissao_percent = mp_config.get("comissao", 0.0)
        taxa_fixa = mp_config.get("custo_fixo", 0.0)
        
        regime_config = self.regimes.get(regime_tributario, {})
        impostos_percent = regime_config.get("impostos_encargos", 0.0)
        custo_fixo_operacional = regime_config.get("custo_fixo_operacional", 0.0)
        
        # Cálculos
        comissao = preco_atual * comissao_percent if preco_atual > 0 else 0
        impostos = preco_atual * impostos_percent if preco_atual > 0 else 0
        publicidade = preco_atual * (self.percent_publicidade / 100) if preco_atual > 0 else 0
        
        # Lucro
        lucro_r = preco_atual - custo_produto - frete - comissao - taxa_fixa - impostos - publicidade - custo_fixo_operacional
        
        # Margens
        margem_bruta_percent = (lucro_r / preco_atual * 100) if preco_atual > 0 else 0
        
        # Status
        if margem_bruta_percent < self.margem_liquida_minima:
            status = "🔴 Prejuízo/Abaixo"
        elif margem_bruta_percent < self.margem_bruta_alvo:
            status = "🟡 Alerta"
        else:
            status = "🟢 Saudável"
        
        return {
            "SKU": sku,
            "Descrição": descricao,
            "Marketplace": marketplace,
            "Regime": regime_tributario,
            "Preço Atual (R$)": preco_atual,
            "Custo Produto": custo_produto,
            "Frete": frete,
            "Comissão": comissao,
            "Taxa Fixa": taxa_fixa,
            "Impostos": impostos,
            "Publicidade": publicidade,
            "Custo Fixo Op.": custo_fixo_operacional,
            "Lucro R$": lucro_r,
            "Margem Bruta %": margem_bruta_percent,
            "Status": status,
        }

    def calcular_dataframe(self, df, marketplace, regime_tributario):
        """
        Calcula múltiplas linhas
        
        Args:
            df: DataFrame com colunas: SKU, Descrição, Custo Produto, Frete, Preço Atual
            marketplace: Marketplace selecionado
            regime_tributario: Regime tributário selecionado
                
        Returns:
            DataFrame com todos os cálculos
        """
        resultados = []
        
        for _, row in df.iterrows():
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                descricao=row.get("Descrição", ""),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                preco_atual=float(row.get("Preço Atual", 0) or 0),
                marketplace=marketplace,
                regime_tributario=regime_tributario,
            )
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)
