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
            "n.º de venda": "Venda",
            "id": "SKU",
            "produto": "Descrição",
            "título do anúncio": "Descrição",
            "preço": "Preço",
            "preço unitário de venda do anúncio (brl)": "Preço",
            "preço atual": "Preço",
            "preço de venda": "Preço",
            "quantidade": "Quantidade Vendida",
            "quantidade vendida": "Quantidade Vendida",
            "unidades": "Quantidade Vendida",
            "vendas": "Quantidade Vendida",
            "faturamento": "Faturamento",
            "receita por produtos (brl)": "Faturamento",
            "receita": "Faturamento",
            "total vendido": "Faturamento",
        }
        
        # Normalizar nomes de colunas
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=mapeamento_colunas)
        
        # Remover linhas onde SKU está vazio
        df = df[df["SKU"].notna() & (df["SKU"] != "")]
        
        # Converter tipos de dados
        df["SKU"] = df["SKU"].astype(str).str.strip()
        df["Preço"] = pd.to_numeric(df["Preço"], errors="coerce")
        df["Quantidade Vendida"] = pd.to_numeric(df["Quantidade Vendida"], errors="coerce")
        
        # Garantir que temos dados válidos
        df = df[df["Preço"].notna() & (df["Preço"] > 0)]
        df = df[df["Quantidade Vendida"].notna() & (df["Quantidade Vendida"] > 0)]
        
        # Calcular faturamento se não existir ou estiver vazio
        if "Faturamento" not in df.columns or df["Faturamento"].isna().all():
            df["Faturamento"] = df["Preço"] * df["Quantidade Vendida"]
        else:
            df["Faturamento"] = pd.to_numeric(df["Faturamento"], errors="coerce")
            # Se faturamento vazio, calcular
            df.loc[df["Faturamento"].isna(), "Faturamento"] = df["Preço"] * df["Quantidade Vendida"]
        
        # Remover linhas com faturamento inválido
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
        # Manter descrição se existir
        agg_dict = {
            "Preço": "mean",
            "Quantidade Vendida": "sum",
            "Faturamento": "sum",
        }
        
        # Adicionar descrição se existir
        if "Descrição" in df.columns:
            agg_dict["Descrição"] = "first"
        
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
        
        if len(df) < 3:
            return False, "Relatório deve ter pelo menos 3 produtos"
        
        if "Faturamento" not in df.columns or df["Faturamento"].sum() <= 0:
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
            try:
                df[data_col] = pd.to_datetime(df[data_col], errors="coerce")
                data_min = df[data_col].min()
                data_max = df[data_col].max()
                return f"{data_min.date()} a {data_max.date()}"
            except:
                pass
        
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
        # Tentar carregar com skiprows=5 (formato padrão do Mercado Livre)
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=5)
            # Verificar se tem colunas esperadas
            if "SKU" in df.columns or "Título do anúncio" in df.columns:
                return df
        except:
            pass
        
        # Se não funcionar, tentar sem skiprows
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
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
        return pd.read_csv(file_path, encoding=encoding)
