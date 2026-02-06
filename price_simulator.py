"""
Módulo para Simulador de Preço Alvo V2
Implementa a lógica automática baseada em dados do relatório
"""

import pandas as pd
import numpy as np


class PriceSimulator:
    """Simula preços alvo de forma automática baseado em dados do relatório."""

    def __init__(self, marketplaces, regimes, margem_bruta_alvo, margem_liquida_minima, percent_publicidade):
        """
        Inicializa o simulador
        
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

    def calcular_linha(self, sku, descricao, custo_produto, frete, 
                       marketplace, regime_tributario):
        """
        Calcula simulação de preço para uma linha
        
        Args:
            sku: SKU do produto
            descricao: Descrição do produto
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            marketplace: Nome do marketplace
            regime_tributario: Regime tributário
            
        Returns:
            Dict com simulação de preço
        """
        # Obter configurações
        mp_config = self.marketplaces.get(marketplace, {})
        comissao_percent = mp_config.get("comissao", 0.0)
        taxa_fixa = mp_config.get("custo_fixo", 0.0)
        
        regime_config = self.regimes.get(regime_tributario, {})
        impostos_percent = regime_config.get("impostos_encargos", 0.0)
        custo_fixo_operacional = regime_config.get("custo_fixo_operacional", 0.0)
        
        # Custo total direto
        custo_total_direto = custo_produto + frete + taxa_fixa + custo_fixo_operacional
        
        # Taxas variáveis (em decimal)
        taxas_variaveis = (comissao_percent + impostos_percent + (self.percent_publicidade / 100))
        
        # Margem alvo (em decimal)
        margem_alvo_decimal = self.margem_bruta_alvo / 100
        margem_minima_decimal = self.margem_liquida_minima / 100
        
        # Preço sugerido (Margem Bruta) = Custo / (1 - Taxas - Margem)
        denominador_bruto = 1 - taxas_variaveis - margem_alvo_decimal
        
        if denominador_bruto > 0 and custo_total_direto > 0:
            preco_sugerido = custo_total_direto / denominador_bruto
            lucro_bruto = preco_sugerido * margem_alvo_decimal
        else:
            preco_sugerido = 0
            lucro_bruto = 0
        
        # Preço promo limite (Margem Líquida)
        denominador_promo = 1 - taxas_variaveis - margem_minima_decimal
        
        if denominador_promo > 0 and custo_total_direto > 0:
            preco_promo_limite = custo_total_direto / denominador_promo
            lucro_liquido = preco_promo_limite * margem_minima_decimal
        else:
            preco_promo_limite = 0
            lucro_liquido = 0
        
        return {
            "SKU": sku,
            "Descrição": descricao,
            "Marketplace": marketplace,
            "Regime": regime_tributario,
            "Preço Sugerido": preco_sugerido,
            "Preço Promo Limite": preco_promo_limite,
            "Margem Bruta %": self.margem_bruta_alvo,
            "Margem Líquida %": self.margem_liquida_minima,
            "Lucro Bruto": lucro_bruto,
            "Lucro Líquido": lucro_liquido,
        }

    def calcular_dataframe(self, df, marketplace, regime_tributario):
        """
        Calcula simulação para múltiplas linhas
        
        Args:
            df: DataFrame com colunas: SKU, Descrição, Custo Produto, Frete
            marketplace: Marketplace selecionado
            regime_tributario: Regime tributário selecionado
                
        Returns:
            DataFrame com simulação de preços
        """
        resultados = []
        
        for _, row in df.iterrows():
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                descricao=row.get("Descrição", ""),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                marketplace=marketplace,
                regime_tributario=regime_tributario,
            )
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)
