"""
Módulo de cálculos de precificação baseado na lógica da planilha V3
"""

import pandas as pd
import numpy as np
from config import (
    DEFAULT_MARKETPLACES,
    DEFAULT_REGIMES,
    STATUS_SAUDAVEL,
    STATUS_ALERTA,
    STATUS_PREJUIZO,
)


class PricingCalculator:
    """Calcula precificação, margens e lucros com base em configurações de marketplace e regime tributário."""

    def __init__(self, marketplaces=None, regimes=None):
        self.marketplaces = marketplaces or DEFAULT_MARKETPLACES
        self.regimes = regimes or DEFAULT_REGIMES

    def calcular_custos_variáveis(self, preco_venda, marketplace, regime, ads_percent=0):
        """
        Calcula todos os custos variáveis (comissão, taxa fixa, impostos, ads)
        
        Args:
            preco_venda: Preço de venda em R$
            marketplace: Nome do marketplace
            regime: Regime tributário
            ads_percent: Percentual de Ads
            
        Returns:
            dict com detalhamento de custos
        """
        mp_config = self.marketplaces.get(marketplace, self.marketplaces["Outros"])
        regime_config = self.regimes.get(regime, self.regimes["Lucro Real"])

        # Comissão do marketplace
        comissao = preco_venda * mp_config["comissao"]

        # Taxa fixa do marketplace
        taxa_fixa = mp_config["custo_fixo"]

        # Impostos (IBS + CBS + Impostos e Encargos)
        impostos = preco_venda * (
            regime_config["ibs"] + regime_config["cbs"] + regime_config["impostos_encargos"]
        )

        # Ads
        ads = preco_venda * ads_percent if ads_percent > 0 else 0

        # Taxa de devolução
        taxa_devolucao = preco_venda * mp_config["taxa_devolucao"]

        return {
            "comissao": comissao,
            "taxa_fixa": taxa_fixa,
            "impostos": impostos,
            "ads": ads,
            "taxa_devolucao": taxa_devolucao,
            "total_variavel": comissao + taxa_fixa + impostos + ads + taxa_devolucao,
        }

    def calcular_margem(self, preco_venda, custo_total_direto, custos_variáveis):
        """
        Calcula margem bruta e líquida
        
        Args:
            preco_venda: Preço de venda
            custo_total_direto: Custo do produto + frete
            custos_variáveis: Dict com custos variáveis
            
        Returns:
            dict com margens
        """
        if preco_venda <= 0:
            return {"bruta": 0, "liquida": 0, "lucro": 0}

        # Lucro bruto
        lucro_bruto = preco_venda - custo_total_direto
        margem_bruta = (lucro_bruto / preco_venda) * 100 if preco_venda > 0 else 0

        # Lucro líquido
        lucro_liquido = preco_venda - custo_total_direto - custos_variáveis["total_variavel"]
        margem_liquida = (lucro_liquido / preco_venda) * 100 if preco_venda > 0 else 0

        return {
            "bruta": margem_bruta,
            "liquida": margem_liquida,
            "lucro": lucro_liquido,
        }

    def calcular_preco_sugerido(
        self, custo_total_direto, marketplace, regime, margem_alvo, ads_percent=0
    ):
        """
        Calcula o preço sugerido para atingir uma margem alvo
        
        Args:
            custo_total_direto: Custo do produto + frete
            marketplace: Nome do marketplace
            regime: Regime tributário
            margem_alvo: Margem desejada em %
            ads_percent: Percentual de Ads
            
        Returns:
            float com preço sugerido
        """
        mp_config = self.marketplaces.get(marketplace, self.marketplaces["Outros"])
        regime_config = self.regimes.get(regime, self.regimes["Lucro Real"])

        # Taxa variável total (sem considerar preço ainda)
        taxa_variavel = (
            mp_config["comissao"]
            + regime_config["ibs"]
            + regime_config["cbs"]
            + regime_config["impostos_encargos"]
            + mp_config["taxa_devolucao"]
            + ads_percent
        )

        # Fórmula: Preço = Custo / (1 - Taxa Variável - Margem Alvo)
        denominador = 1 - taxa_variavel - (margem_alvo / 100)

        if denominador <= 0:
            return 0

        preco_sugerido = (custo_total_direto + mp_config["custo_fixo"]) / denominador

        return max(0, preco_sugerido)

    def calcular_desconto_maximo(self, preco_venda, custo_total_direto, margem_liquida_minima):
        """
        Calcula o desconto máximo permitido antes de atingir a margem líquida mínima
        
        Args:
            preco_venda: Preço de venda atual
            custo_total_direto: Custo do produto + frete
            margem_liquida_minima: Margem líquida mínima aceitável em %
            
        Returns:
            float com desconto máximo em %
        """
        if preco_venda <= 0:
            return 0

        # Preço mínimo para manter a margem líquida mínima
        preco_minimo = custo_total_direto / (1 - (margem_liquida_minima / 100))

        desconto = ((preco_venda - preco_minimo) / preco_venda) * 100

        return max(0, desconto)

    def avaliar_saude_precificacao(self, preco_venda, margem_liquida, margem_liquida_minima, margem_bruta_alvo):
        """
        Avalia se a precificação está saudável, em alerta ou prejuízo
        
        Args:
            preco_venda: Preço de venda
            margem_liquida: Margem líquida atual em %
            margem_liquida_minima: Margem líquida mínima em %
            margem_bruta_alvo: Margem bruta alvo em %
            
        Returns:
            str com status
        """
        if preco_venda <= 0:
            return STATUS_PREJUIZO

        if margem_liquida < margem_liquida_minima:
            return STATUS_PREJUIZO

        if margem_liquida < margem_bruta_alvo:
            return STATUS_ALERTA

        return STATUS_SAUDAVEL

    def processar_base_dados(self, df, marketplaces=None, regimes=None):
        """
        Processa a base de dados completa e calcula todas as métricas
        
        Args:
            df: DataFrame com dados da base
            marketplaces: Dict de marketplaces (usa padrão se None)
            regimes: Dict de regimes (usa padrão se None)
            
        Returns:
            DataFrame processado com cálculos
        """
        if marketplaces:
            self.marketplaces = marketplaces
        if regimes:
            self.regimes = regimes

        df = df.copy()

        # Calcular custo total direto
        df["Custo Total Direto"] = df["Custo Produto (R$)"] + df["Frete (R$)"]

        # Calcular custos variáveis
        df["Custos Variáveis"] = df.apply(
            lambda row: self.calcular_custos_variáveis(
                row["Preço Base (R$)"],
                row["Marketplace"],
                row["Regime Tributário"],
                row.get("Ads (%)", 0) / 100,
            )["total_variavel"],
            axis=1,
        )

        # Calcular margens
        df["Lucro R$"] = df.apply(
            lambda row: row["Preço Base (R$)"] - row["Custo Total Direto"] - row["Custos Variáveis"],
            axis=1,
        )

        df["Margem Calculada %"] = df.apply(
            lambda row: (row["Lucro R$"] / row["Preço Base (R$)"] * 100)
            if row["Preço Base (R$)"] > 0
            else 0,
            axis=1,
        )

        # Calcular desconto máximo
        df["Desconto Máximo %"] = df.apply(
            lambda row: self.calcular_desconto_maximo(
                row["Preço Base (R$)"],
                row["Custo Total Direto"],
                row["Margem Líquida (%)"],
            ),
            axis=1,
        )

        # Avaliar saúde
        df["Status"] = df.apply(
            lambda row: self.avaliar_saude_precificacao(
                row["Preço Base (R$)"],
                row["Margem Calculada %"],
                row["Margem Líquida (%)"],
                row["Margem Bruta (%)"],
            ),
            axis=1,
        )

        return df
