"""
Módulo para Calculadora de Precificação V2
Implementa a lógica automática baseada em dados do relatório
"""

import pandas as pd
import numpy as np
from config import MERCADO_LIVRE_AD_TYPES


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

    def obter_config_marketplace(self, marketplace, tipo_anuncio=""):
        """
        Obtém configuração do marketplace, considerando tipo de anúncio para Mercado Livre
        
        Args:
            marketplace: Nome do marketplace
            tipo_anuncio: Tipo de anúncio (para Mercado Livre: "Clássico" ou "Premium")
            
        Returns:
            Dict com configuração (comissao, custo_fixo)
        """
        # Se é Mercado Livre e tem tipo de anúncio especificado
        if marketplace == "Mercado Livre" and tipo_anuncio and tipo_anuncio in MERCADO_LIVRE_AD_TYPES:
            return MERCADO_LIVRE_AD_TYPES[tipo_anuncio]
        
        # Caso contrário, usar configuração padrão do marketplace
        return self.marketplaces.get(marketplace, {"comissao": 0.0, "custo_fixo": 0.0})

    def calcular_linha(self, sku, descricao, custo_produto, frete, preco_atual, 
                       marketplace, regime_tributario, tipo_anuncio=""):
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
            tipo_anuncio: Tipo de anúncio (opcional, para Mercado Livre)
            
        Returns:
            Dict com todos os cálculos
        """
        # Obter configurações do marketplace (considerando tipo de anúncio)
        mp_config = self.obter_config_marketplace(marketplace, tipo_anuncio)
        comissao_percent = mp_config.get("comissao", 0.0)
        taxa_fixa = mp_config.get("custo_fixo", 0.0)
        
        # Obter configurações do regime tributário
        regime_config = self.regimes.get(regime_tributario, {})
        impostos_percent = regime_config.get("impostos_encargos", 0.0)
        custo_fixo_operacional = regime_config.get("custo_fixo_operacional", 0.0)
        
        # Cálculos
        comissao = preco_atual * comissao_percent
        impostos = preco_atual * impostos_percent
        publicidade = preco_atual * (self.percent_publicidade / 100)
        
        lucro = preco_atual - custo_produto - frete - comissao - taxa_fixa - impostos - publicidade - custo_fixo_operacional
        
        margem_bruta = (lucro / preco_atual * 100) if preco_atual > 0 else 0
        
        # Determinar status
        if margem_bruta >= self.margem_bruta_alvo:
            status = "🟢 Saudável"
        elif margem_bruta >= self.margem_liquida_minima:
            status = "🟡 Alerta"
        else:
            status = "🔴 Prejuízo/Abaixo"
        
        return {
            "SKU": sku,
            "Descrição": descricao,
            "Preço Atual (R$)": preco_atual,
            "Custo Produto": custo_produto,
            "Frete": frete,
            "Comissão": comissao,
            "Taxa Fixa": taxa_fixa,
            "Custo Fixo Op.": custo_fixo_operacional,
            "Impostos": impostos,
            "Publicidade": publicidade,
            "Lucro R$": lucro,
            "Margem Bruta %": margem_bruta,
            "Status": status,
        }

    def calcular_dataframe(self, df, marketplace, regime_tributario):
        """
        Calcula precificação para múltiplas linhas
        
        Args:
            df: DataFrame com colunas: SKU, Descrição, Custo Produto, Frete, Preço Atual, Tipo de Anúncio (opcional)
            marketplace: Marketplace selecionado
            regime_tributario: Regime tributário selecionado
                
        Returns:
            DataFrame com cálculos completos
        """
        resultados = []
        
        for _, row in df.iterrows():
            tipo_anuncio = row.get("Tipo de Anúncio", "")
            
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                descricao=row.get("Descrição", ""),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                preco_atual=float(row.get("Preço Atual", 0) or 0),
                marketplace=marketplace,
                regime_tributario=regime_tributario,
                tipo_anuncio=tipo_anuncio,
            )
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)
