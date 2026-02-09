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
        Aceita formato simples com colunas: SKU/MLB, Titulo, Custo Produto, Frete, Preço Atual, Tipo de Anúncio (opcional), Quantidade Vendida (opcional)
        
        Args:
            df: DataFrame com dados brutos do Mercado Livre
            
        Returns:
            DataFrame normalizado com colunas: SKU, Descrição, Custo Produto, Frete, Preço Atual, Tipo de Anúncio, Quantidade Vendida
        """
        df = df.copy()
        
        # Debug: Mostrar colunas originais
        print(f"Colunas originais: {df.columns.tolist()}")
        
        # Mapeamento de colunas possíveis - EXATO E FLEXÍVEL
        mapeamento_colunas = {
            # SKU
            "sku/mlb": "SKU",
            "sku": "SKU",
            "mlb": "SKU",
            "col a": "SKU",
            # Título/Descrição
            "titulo": "Descrição",
            "título": "Descrição",
            "title": "Descrição",
            "product": "Descrição",
            "col b": "Descrição",
            # Custo Produto
            "custo produto (r$)": "Custo Produto",
            "custo produto": "Custo Produto",
            "custo": "Custo Produto",
            "cost": "Custo Produto",
            "col c": "Custo Produto",
            # Frete
            "frete (r$)": "Frete",
            "frete": "Frete",
            "shipping": "Frete",
            "col d": "Frete",
            # Preço Atual
            "preço atual (r$)": "Preço Atual",
            "preço atual": "Preço Atual",
            "preço": "Preço Atual",
            "price": "Preço Atual",
            "current price": "Preço Atual",
            "col e": "Preço Atual",
            # Tipo de Anúncio
            "tipo de anúncio": "Tipo de Anúncio",
            "tipo de anuncio": "Tipo de Anúncio",
            "ad type": "Tipo de Anúncio",
            "anuncio": "Tipo de Anúncio",
            "col f": "Tipo de Anúncio",
            # Quantidade Vendida
            "quantidade vendida": "Quantidade Vendida",
            "quantidade": "Quantidade Vendida",
            "quantity": "Quantidade Vendida",
            "vendas": "Quantidade Vendida",
            "sales": "Quantidade Vendida",
            "col g": "Quantidade Vendida",
        }
        
        # Normalizar nomes de colunas
        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=mapeamento_colunas)
        
        print(f"Colunas após mapeamento: {df.columns.tolist()}")
        
        # Adicionar coluna Tipo de Anúncio se não existir
        if "Tipo de Anúncio" not in df.columns:
            df["Tipo de Anúncio"] = ""  # Vazio por padrão
        
        # Adicionar coluna Quantidade Vendida se não existir
        if "Quantidade Vendida" not in df.columns:
            df["Quantidade Vendida"] = 0  # Padrão 0 se não informado
        
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
        
        # Converter Tipo de Anúncio para string (pode estar vazio)
        df["Tipo de Anúncio"] = df["Tipo de Anúncio"].astype(str).str.strip().str.lower()
        # Normalizar valores: "clássico" ou "premium"
        df["Tipo de Anúncio"] = df["Tipo de Anúncio"].replace({
            "clássico": "Clássico",
            "classico": "Clássico",
            "classic": "Clássico",
            "premium": "Premium",
            "nan": "",  # Converter NaN para vazio
        })
        # Se ainda tiver valores não reconhecidos, deixar vazio
        df.loc[~df["Tipo de Anúncio"].isin(["Clássico", "Premium", ""]), "Tipo de Anúncio"] = ""
        
        # Converter Quantidade Vendida para int
        if "Quantidade Vendida" in df.columns:
            df["Quantidade Vendida"] = pd.to_numeric(df["Quantidade Vendida"], errors="coerce").fillna(0).astype(int)
        
        print(f"Quantidade Vendida após conversão: {df['Quantidade Vendida'].tolist()[:5]}")
        
        # Selecionar apenas as colunas necessárias
        colunas_selecionadas = ["SKU", "Descrição", "Custo Produto", "Frete", "Preço Atual", "Tipo de Anúncio"]
        if "Quantidade Vendida" in df.columns:
            colunas_selecionadas.append("Quantidade Vendida")
        df = df[colunas_selecionadas]
        
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
            "Tipo de Anúncio": "first",
        }
        
        # Adicionar Quantidade Vendida se existir
        if "Quantidade Vendida" in df.columns:
            agg_dict["Quantidade Vendida"] = "sum"  # Somar quantidade vendida
        
        df_agg = df.groupby("SKU").agg(agg_dict).reset_index()
        
        return df_agg

    @staticmethod
    def validar_relatorio(df):
        """
        Valida se o relatório tem as colunas necessárias
        
        Args:
            df: DataFrame com dados de vendas
            
        Returns:
            Tupla (válido, mensagem)
        """
        colunas_obrigatorias = ["SKU", "Descrição", "Custo Produto", "Frete", "Preço Atual"]
        
        for col in colunas_obrigatorias:
            if col not in df.columns:
                return False, f"Coluna '{col}' não encontrada"
        
        if len(df) == 0:
            return False, "Relatório vazio"
        
        return True, "Relatório válido"

    @staticmethod
    def carregar_de_excel(arquivo):
        """Carrega dados de arquivo Excel"""
        return pd.read_excel(arquivo)

    @staticmethod
    def carregar_de_csv(arquivo):
        """Carrega dados de arquivo CSV"""
        return pd.read_csv(arquivo)
