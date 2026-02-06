"""
Módulo para gerenciamento de regras de promoção por curva ABC
"""

import pandas as pd
import numpy as np


class PromotionManager:
    """Gerencia regras de promoção e calcula preços com desconto."""

    def __init__(self):
        """Inicializa o gerenciador de promoções."""
        self.promotion_rules = {
            "A": 0.0,  # Sem promoção por padrão
            "B": 0.0,
            "C": 0.0,
            "Sem Curva": 0.0,
        }

    def definir_regras(self, regras_dict):
        """
        Define regras de promoção por curva
        
        Args:
            regras_dict: Dict com formato {"A": 0.05, "B": 0.08, "C": 0.10}
        """
        self.promotion_rules.update(regras_dict)

    def calcular_preco_promocional(self, preco_original, desconto_percent):
        """
        Calcula preço com desconto
        
        Args:
            preco_original: Preço original
            desconto_percent: Desconto em % (ex: 0.05 para 5%)
            
        Returns:
            float com preço promocional
        """
        return preco_original * (1 - desconto_percent)

    def aplicar_promocoes(self, df, regras=None):
        """
        Aplica regras de promoção aos produtos
        
        Args:
            df: DataFrame com coluna 'Curva ABC' e 'Preço'
            regras: Dict com regras (usa self.promotion_rules se None)
            
        Returns:
            DataFrame com coluna 'Preço Promocional' adicionada
        """
        if regras:
            self.definir_regras(regras)

        df = df.copy()

        # Aplicar desconto baseado na curva
        df["Desconto %"] = df["Curva ABC"].map(self.promotion_rules)
        df["Preço Promocional"] = df.apply(
            lambda row: self.calcular_preco_promocional(
                row["Preço"], row["Desconto %"]
            ),
            axis=1,
        )

        # Calcular economia do cliente
        df["Economia R$"] = df["Preço"] - df["Preço Promocional"]

        return df

    def validar_desconto_seguro(self, df, desconto_max_col="Desconto Máximo %"):
        """
        Valida se os descontos aplicados estão dentro do limite seguro
        
        Args:
            df: DataFrame com colunas 'Desconto %' e 'Desconto Máximo %'
            desconto_max_col: Nome da coluna com desconto máximo
            
        Returns:
            DataFrame com coluna 'Desconto Seguro' (True/False)
        """
        df = df.copy()
        df["Desconto Seguro"] = df["Desconto %"] <= df.get(desconto_max_col, 100)
        return df

    def gerar_relatorio_promocoes(self, df):
        """
        Gera relatório de impacto das promoções
        
        Args:
            df: DataFrame com dados de promoção
            
        Returns:
            dict com métricas de impacto
        """
        total_economia = df["Economia R$"].sum()
        economia_media = df["Economia R$"].mean()
        produtos_promocao = len(df[df["Desconto %"] > 0])

        return {
            "total_economia": total_economia,
            "economia_media": economia_media,
            "produtos_com_promocao": produtos_promocao,
            "economia_por_curva": df.groupby("Curva ABC")["Economia R$"].sum().to_dict(),
        }

    def exportar_para_mercado_livre(self, df, output_path=None):
        """
        Exporta dados formatados para upload no Mercado Livre
        
        Args:
            df: DataFrame com dados de promoção
            output_path: Caminho para salvar arquivo (se None, retorna DataFrame)
            
        Returns:
            DataFrame ou None (se salvo em arquivo)
        """
        df_export = df[["SKU", "Descrição", "Preço", "Preço Promocional", "Desconto %", "Curva ABC"]].copy()
        
        # Renomear colunas para formato Mercado Livre
        df_export.columns = ["SKU/MLB", "Título", "Preço Atual", "Preço Promoção", "Desconto %", "Curva"]
        
        # Formatar valores monetários
        df_export["Preço Atual"] = df_export["Preço Atual"].apply(lambda x: f"{x:.2f}")
        df_export["Preço Promoção"] = df_export["Preço Promoção"].apply(lambda x: f"{x:.2f}")
        df_export["Desconto %"] = df_export["Desconto %"].apply(lambda x: f"{x*100:.1f}%")
        
        if output_path:
            df_export.to_excel(output_path, index=False)
            return None
        
        return df_export
