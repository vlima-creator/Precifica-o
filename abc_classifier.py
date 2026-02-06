"""
Módulo para classificação ABC de produtos baseado em faturamento
"""

import pandas as pd
import numpy as np
from config import CURVA_ABC_LIMITS


class ABCClassifier:
    """Classifica produtos em Curva A, B, C baseado em faturamento acumulado."""

    def __init__(self, limits=None):
        """
        Inicializa o classificador
        
        Args:
            limits: Dict com limites de curva (padrão: CURVA_ABC_LIMITS)
        """
        self.limits = limits or CURVA_ABC_LIMITS

    def classificar_produtos(self, df, faturamento_col="Faturamento"):
        """
        Classifica produtos em Curva ABC baseado em faturamento
        
        Args:
            df: DataFrame com dados dos produtos
            faturamento_col: Nome da coluna de faturamento
            
        Returns:
            DataFrame com coluna 'Curva ABC' adicionada
        """
        df = df.copy()

        # Remover linhas com faturamento nulo ou zero
        df = df[df[faturamento_col] > 0].copy()

        # Ordenar por faturamento decrescente
        df = df.sort_values(by=faturamento_col, ascending=False).reset_index(drop=True)

        # Calcular faturamento acumulado
        faturamento_total = df[faturamento_col].sum()
        df["Faturamento Acumulado %"] = (
            df[faturamento_col].cumsum() / faturamento_total
        )

        # Classificar em curvas
        def classificar_linha(row):
            acum_pct = row["Faturamento Acumulado %"]
            if acum_pct <= self.limits["A"]:
                return "A"
            elif acum_pct <= self.limits["B"]:
                return "B"
            elif acum_pct <= self.limits["C"]:
                return "C"
            else:
                return "Sem Curva"

        df["Curva ABC"] = df.apply(classificar_linha, axis=1)

        return df

    def gerar_resumo_abc(self, df):
        """
        Gera resumo estatístico por curva ABC
        
        Args:
            df: DataFrame com coluna 'Curva ABC'
            
        Returns:
            DataFrame com resumo por curva
        """
        resumo = df.groupby("Curva ABC").agg({
            "SKU": "count",
            "Faturamento": "sum",
            "Preço": "mean",
            "Quantidade Vendida": "sum",
        }).round(2)

        resumo.columns = ["Qtd SKUs", "Faturamento", "Preço Médio", "Qtd Vendas"]
        resumo = resumo.reset_index()
        
        return resumo

    def identificar_oportunidades(self, df, margem_minima=15):
        """
        Identifica produtos em Curva B/C com margem alta (oportunidades de promoção)
        
        Args:
            df: DataFrame com colunas 'Curva ABC' e 'Margem Calculada %'
            margem_minima: Margem mínima para considerar como oportunidade
            
        Returns:
            DataFrame com produtos em oportunidade
        """
        oportunidades = df[
            ((df["Curva ABC"] == "B") | (df["Curva ABC"] == "C"))
            & (df.get("Margem Calculada %", 0) > margem_minima)
        ].copy()

        return oportunidades.sort_values("Faturamento", ascending=False)
