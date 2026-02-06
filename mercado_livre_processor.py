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
        Aceita múltiplos formatos de entrada
        
        Args:
            df: DataFrame com dados brutos do Mercado Livre
            
        Returns:
            DataFrame normalizado com colunas: SKU, Descrição, Custo Produto, Frete, Preço Atual
        """
        df = df.copy()
        
        # Normalizar nomes de colunas (lowercase e sem espaços extras)
        df.columns = df.columns.str.lower().str.strip()
        
        # Mapeamento de colunas comuns do Mercado Livre
        mapeamento_colunas = {
            "sku": "SKU",
            "sku/mlb": "SKU",
            "mlb": "SKU",
            "id": "SKU",
            "n.º de venda": "Venda",
            "produto": "Descrição",
            "título do anúncio": "Descrição",
            "título": "Descrição",
            "descrição": "Descrição",
            "custo produto": "Custo Produto",
            "custo do produto": "Custo Produto",
            "custo prod": "Custo Produto",
            "custo": "Custo Produto",
            "frete": "Frete",
            "frete (r$)": "Frete",
            "preço": "Preço Atual",
            "preço atual": "Preço Atual",
            "preço de venda": "Preço Atual",
            "preço unitário de venda do anúncio (brl)": "Preço Atual",
            "preço venda (r$)": "Preço Atual",
            "total (brl)": "Preço Atual",
            "quantidade": "Quantidade Vendida",
            "quantidade vendida": "Quantidade Vendida",
            "unidades": "Quantidade Vendida",
            "vendas": "Quantidade Vendida",
            "faturamento": "Faturamento",
            "receita por produtos (brl)": "Faturamento",
            "receita": "Faturamento",
            "total vendido": "Faturamento",
        }
        
        # Renomear colunas
        df = df.rename(columns=mapeamento_colunas)
        
        # Remover colunas duplicadas
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        # Garantir que temos a coluna SKU
        if "SKU" not in df.columns:
            raise ValueError("Arquivo deve conter coluna 'SKU' ou 'SKU/MLB'")
        
        # Remover linhas onde SKU está vazio
        df = df[df["SKU"].notna() & (df["SKU"] != "")]
        
        # Converter SKU para string
        df["SKU"] = df["SKU"].astype(str).str.strip()
        
        # Adicionar colunas padrão se não existirem
        if "Descrição" not in df.columns:
            if "Título do anúncio" in df.columns:
                df["Descrição"] = df["Título do anúncio"]
            else:
                df["Descrição"] = df["SKU"]
        
        if "Custo Produto" not in df.columns:
            df["Custo Produto"] = 0.0
        
        if "Frete" not in df.columns:
            df["Frete"] = 0.0
        
        if "Preço Atual" not in df.columns:
            if "Preço unitário de venda do anúncio (brl)" in df.columns:
                df["Preço Atual"] = df["Preço unitário de venda do anúncio (brl)"]
            elif "Preço" in df.columns:
                df["Preço Atual"] = df["Preço"]
            else:
                raise ValueError("Arquivo deve conter coluna de preço")
        
        # Converter tipos de dados
        if "Custo Produto" in df.columns:
            df["Custo Produto"] = pd.to_numeric(df["Custo Produto"], errors="coerce").fillna(0.0)
        else:
            df["Custo Produto"] = 0.0
        
        if "Frete" in df.columns:
            df["Frete"] = pd.to_numeric(df["Frete"], errors="coerce").fillna(0.0)
        else:
            df["Frete"] = 0.0
        
        if "Preço Atual" not in df.columns:
            raise ValueError("Coluna de preço não encontrada")
        
        # Converter para numérico
        try:
            df["Preço Atual"] = df["Preço Atual"].astype(float)
        except:
            df["Preço Atual"] = pd.to_numeric(df["Preço Atual"], errors="coerce")
        
        # Remover linhas com preço inválido
        df = df[(df["Preço Atual"].notna()) & (df["Preço Atual"] > 0)].reset_index(drop=True)
        
        # Selecionar apenas as colunas necessárias
        colunas_necessarias = ["SKU", "Descrição", "Custo Produto", "Frete", "Preço Atual"]
        
        # Garantir que todas as colunas existem
        for col in colunas_necessarias:
            if col not in df.columns:
                if col == "Descrição":
                    df[col] = df["SKU"]
                else:
                    df[col] = 0.0
        
        df = df[colunas_necessarias]
        
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
            return False, "Relatório deve conter coluna de preço"
        
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
        # Tentar carregar com skiprows=5 (formato padrão do Mercado Livre)
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=5)
            if len(df) > 0:
                return df
        except:
            pass
        
        # Se não funcionar, tentar sem skiprows
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            if len(df) > 0:
                return df
        except:
            pass
        
        # Tentar com diferentes skiprows
        for skip in [0, 1, 2, 3, 4, 6, 7, 8]:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip)
                if len(df) > 0 and len(df.columns) > 0:
                    return df
            except:
                continue
        
        raise ValueError("Não foi possível carregar o arquivo Excel")

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
