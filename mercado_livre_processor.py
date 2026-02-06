"""
Módulo para processar relatórios de vendas do Mercado Livre
"""

import pandas as pd
import numpy as np
from io import BytesIO


class MercadoLivreProcessor:
    """Processa relatórios de vendas do Mercado Livre."""

    @staticmethod
    def detectar_formato(df):
        """
        Detecta o formato do arquivo enviado
        
        Args:
            df: DataFrame carregado
            
        Returns:
            str com tipo de formato detectado
        """
        colunas = df.columns.str.lower().tolist()
        
        # Verificar se é relatório de vendas
        if any(col in colunas for col in ["sku", "produto", "preço", "quantidade"]):
            return "vendas"
        
        return "desconhecido"

    @staticmethod
    def normalizar_relatorio_vendas(df):
        """
        Normaliza relatório de vendas do Mercado Livre
        
        Args:
            df: DataFrame com dados brutos do Mercado Livre
            
        Returns:
            DataFrame normalizado
        """
        df = df.copy()
        
        # Mapeamento de colunas comuns do Mercado Livre
        mapeamento_colunas = {
            "sku": "SKU",
            "id": "SKU",
            "produto": "Descrição",
            "título": "Descrição",
            "preço": "Preço",
            "preço atual": "Preço",
            "preço de venda": "Preço",
            "quantidade": "Quantidade Vendida",
            "quantidade vendida": "Quantidade Vendida",
            "vendas": "Quantidade Vendida",
            "faturamento": "Faturamento",
            "receita": "Faturamento",
            "total vendido": "Faturamento",
        }
        
        # Normalizar nomes de colunas
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=mapeamento_colunas)
        
        # Garantir colunas essenciais
        colunas_essenciais = ["SKU", "Preço", "Quantidade Vendida"]
        
        for col in colunas_essenciais:
            if col not in df.columns:
                raise ValueError(f"Coluna obrigatória '{col}' não encontrada no relatório")
        
        # Converter tipos de dados
        df["SKU"] = df["SKU"].astype(str)
        df["Preço"] = pd.to_numeric(df["Preço"], errors="coerce")
        df["Quantidade Vendida"] = pd.to_numeric(df["Quantidade Vendida"], errors="coerce")
        
        # Calcular faturamento se não existir
        if "Faturamento" not in df.columns:
            df["Faturamento"] = df["Preço"] * df["Quantidade Vendida"]
        else:
            df["Faturamento"] = pd.to_numeric(df["Faturamento"], errors="coerce")
        
        # Remover linhas com dados inválidos
        df = df.dropna(subset=["SKU", "Preço", "Quantidade Vendida"])
        df = df[df["Faturamento"] > 0]
        
        return df.reset_index(drop=True)

    @staticmethod
    def agregar_por_sku(df):
        """
        Agrega dados por SKU (caso haja múltiplas linhas do mesmo produto)
        
        Args:
            df: DataFrame com dados de vendas
            
        Returns:
            DataFrame agregado por SKU
        """
        df_agg = df.groupby("SKU").agg({
            "Descrição": "first",
            "Preço": "mean",
            "Quantidade Vendida": "sum",
            "Faturamento": "sum",
        }).reset_index()
        
        return df_agg

    @staticmethod
    def validar_relatorio(df):
        """
        Valida se o relatório tem dados suficientes
        
        Args:
            df: DataFrame com dados de vendas
            
        Returns:
            tuple (bool, str) com resultado e mensagem
        """
        if df.empty:
            return False, "Relatório vazio"
        
        if len(df) < 5:
            return False, "Relatório deve ter pelo menos 5 produtos"
        
        if df["Faturamento"].sum() <= 0:
            return False, "Faturamento total deve ser maior que zero"
        
        return True, "Relatório válido"

    @staticmethod
    def calcular_periodo_vendas(df, data_col=None):
        """
        Calcula período de vendas do relatório
        
        Args:
            df: DataFrame com dados de vendas
            data_col: Nome da coluna de data (se existir)
            
        Returns:
            str com período estimado
        """
        if data_col and data_col in df.columns:
            df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
            data_min = df[data_col].min()
            data_max = df[data_col].max()
            return f"{data_min.date()} a {data_max.date()}"
        
        return "Período não identificado"

    @staticmethod
    def exportar_para_excel(df, output_path):
        """
        Exporta DataFrame para Excel
        
        Args:
            df: DataFrame para exportar
            output_path: Caminho do arquivo de saída
        """
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Relatório", index=False)

    @staticmethod
    def carregar_de_excel(file_path, sheet_name=0):
        """
        Carrega dados de arquivo Excel
        
        Args:
            file_path: Caminho do arquivo
            sheet_name: Nome ou índice da aba
            
        Returns:
            DataFrame com dados
        """
        return pd.read_excel(file_path, sheet_name=sheet_name)

    @staticmethod
    def carregar_de_csv(file_path, encoding="utf-8"):
        """
        Carrega dados de arquivo CSV
        
        Args:
            file_path: Caminho do arquivo
            encoding: Codificação do arquivo
            
        Returns:
            DataFrame com dados
        """
        return pd.read_csv(file_path, encoding=encoding)
