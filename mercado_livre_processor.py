"""
Módulo para processar relatórios de vendas do Mercado Livre
"""

import pandas as pd
import numpy as np
from io import BytesIO


class MercadoLivreProcessor:
    """Processa relatórios de vendas do Mercado Livre."""

    @staticmethod
    def normalizar_relatorio_vendas(df):
        """
        Normaliza relatório de vendas do Mercado Livre
        Aceita formato simples com colunas: SKU/MLB, Titulo, Custo Produto, Frete, Preço Atual
        
        Args:
            df: DataFrame com dados brutos do Mercado Livre
            
        Returns:
            DataFrame normalizado com colunas: SKU, Descrição, Custo Produto, Frete, Preço Atual
        """
        df = df.copy()
        
        # Se as colunas já estão em inglês/português correto, usar diretamente
        # Caso contrário, tentar mapear
        
        # Mapeamento de colunas possíveis
        mapeamento_colunas = {
            "sku/mlb": "SKU",
            "sku": "SKU",
            "mlb": "SKU",
            "titulo": "Descrição",
            "título": "Descrição",
            "title": "Descrição",
            "product": "Descrição",
            "custo produto (r$)": "Custo Produto",
            "custo produto": "Custo Produto",
            "custo": "Custo Produto",
            "cost": "Custo Produto",
            "frete (r$)": "Frete",
            "frete": "Frete",
            "shipping": "Frete",
            "preço atual (r$)": "Preço Atual",
            "preço atual": "Preço Atual",
            "preço": "Preço Atual",
            "price": "Preço Atual",
            "current price": "Preço Atual",
        }
        
        # Normalizar nomes de colunas
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=mapeamento_colunas)
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = ["SKU", "Descrição", "Custo Produto", "Frete", "Preço Atual"]
        colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]
        
        if colunas_faltando:
            raise ValueError(f"Colunas faltando: {', '.join(colunas_faltando)}")
        
        # Remover linhas onde SKU está vazio
        df = df[df["SKU"].notna() & (df["SKU"] != "")]
        
        if len(df) == 0:
            raise ValueError("Nenhuma linha com SKU válido encontrada")
        
        # Converter SKU para string
        df["SKU"] = df["SKU"].astype(str).str.strip()
        
        # Converter Descrição para string
        df["Descrição"] = df["Descrição"].astype(str).str.strip()
        
        # Converter valores monetários para float
        df["Custo Produto"] = pd.to_numeric(df["Custo Produto"], errors="coerce").fillna(0.0)
        df["Frete"] = pd.to_numeric(df["Frete"], errors="coerce").fillna(0.0)
        df["Preço Atual"] = pd.to_numeric(df["Preço Atual"], errors="coerce")
        
        # Remover linhas com preço inválido
        df = df[df["Preço Atual"].notna() & (df["Preço Atual"] > 0)]
        
        if len(df) == 0:
            raise ValueError("Nenhuma linha com preço válido encontrada")
        
        # Selecionar apenas as colunas necessárias
        df = df[["SKU", "Descrição", "Custo Produto", "Frete", "Preço Atual"]]
        
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
        agg_dict = {
            "Descrição": "first",
            "Custo Produto": "mean",
            "Frete": "mean",
            "Preço Atual": "mean",
        }
        
        df_agg = df.groupby("SKU").agg(agg_dict).reset_index()
        
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
        
        if "SKU" not in df.columns:
            return False, "Relatório deve conter coluna 'SKU'"
        
        if "Preço Atual" not in df.columns:
            return False, "Relatório deve conter coluna 'Preço Atual'"
        
        return True, "Relatório válido"

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
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            if len(df) > 0:
                return df
        except Exception as e:
            raise ValueError(f"Erro ao carregar arquivo Excel: {str(e)}")

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
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except:
            try:
                return pd.read_csv(file_path, encoding="latin-1")
            except:
                return pd.read_csv(file_path, encoding="iso-8859-1")
