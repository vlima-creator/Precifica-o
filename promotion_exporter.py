"""
Módulo genérico para exportação de promoções por marketplace
Suporta múltiplos canais (Shopee, Mercado Livre, etc) com templates específicos
"""

import pandas as pd
import numpy as np
import unicodedata
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows


class PromotionExporter:
    """Exporta promoções no formato compatível com diferentes marketplaces."""
    
    # Mapeamento de sinônimos de colunas (para diferentes marketplaces)
    COLUMN_SYNONYMS = {
        "id": ["sku", "mlb", "id do produto", "id_produto", "product_id", "item_id", "codigo", "product id", "item id"],
        "descricao": ["descricao", "titulo", "nome do produto", "nome_produto", "product_name", "name", "product name"],
        "preco": ["preco", "price", "valor", "valor_venda", "preco_venda", "valor venda", "preco venda", "preco sugerido", "preço sugerido", "preco limite", "preço limite", "preco promo limite", "preço promo limite"]
    }
    
    # Templates de colunas por marketplace
    MARKETPLACE_TEMPLATES = {
        "Shopee": {
            "colunas": [
                "ID do produto",
                "Nome do Produto. (Opcional)",
                "Nº de Ref. Parent SKU. (Opcional)",
                "ID de variação",
                "Variação de nome. (Opcional)",
                "Nº de Ref. SKU. (Opcional)",
                "Preço original (opcional)",
                "Preço de desconto",
                "Limite de compra (Opcional)",
            ],
            "mapeamento": {
                "ID do produto": "SKU",
                "Nome do Produto. (Opcional)": "Descrição",
                "Nº de Ref. Parent SKU. (Opcional)": None,
                "ID de variação": "SKU",
                "Variação de nome. (Opcional)": None,
                "Nº de Ref. SKU. (Opcional)": "SKU",
                "Preço original (opcional)": "Preço",
                "Preço de desconto": "Preço_Desconto",
                "Limite de compra (Opcional)": None,
            }
        }
    }
    
    def __init__(self, marketplace="Shopee"):
        """
        Inicializa o exportador
        
        Args:
            marketplace: Nome do marketplace (ex: "Shopee", "Mercado Livre")
        """
        if marketplace not in self.MARKETPLACE_TEMPLATES:
            raise ValueError(f"Marketplace '{marketplace}' não suportado. Suportados: {list(self.MARKETPLACE_TEMPLATES.keys())}")
        
        self.marketplace = marketplace
        self.template = self.MARKETPLACE_TEMPLATES[marketplace]
    
    def _normalizar_nome_coluna(self, nome):
        """
        Normaliza o nome de uma coluna para comparação
        Remove espaços, acentos e converte para minúsculas
        
        Args:
            nome: Nome da coluna
            
        Returns:
            Nome normalizado
        """
        # Remover acentos
        nome_sem_acentos = ''.join(
            c for c in unicodedata.normalize('NFD', str(nome))
            if unicodedata.category(c) != 'Mn'
        )
        # Converter para minúsculas e remover espaços
        return nome_sem_acentos.lower().strip()
    
    def _encontrar_coluna(self, df, tipo_coluna):
        """
        Encontra uma coluna no DataFrame usando sinônimos
        
        Args:
            df: DataFrame
            tipo_coluna: "id", "descricao" ou "preco"
            
        Returns:
            Nome da coluna encontrada ou None
        """
        sinonimos = self.COLUMN_SYNONYMS.get(tipo_coluna, [])
        
        # Normalizar sinônimos
        sinonimos_normalizados = [self._normalizar_nome_coluna(s) for s in sinonimos]
        
        # Procurar nas colunas do DataFrame
        for col in df.columns:
            col_normalizado = self._normalizar_nome_coluna(col)
            if col_normalizado in sinonimos_normalizados:
                return col
        
        return None
    
    def _normalizar_dataframe(self, df):
        """
        Normaliza o DataFrame identificando e renomeando colunas automaticamente
        
        Args:
            df: DataFrame com colunas variadas
            
        Returns:
            DataFrame com colunas padronizadas (SKU, Descrição, Preço)
        """
        df_norm = df.copy()
        
        # Encontrar e renomear colunas
        col_id = self._encontrar_coluna(df_norm, "id")
        col_descricao = self._encontrar_coluna(df_norm, "descricao")
        col_preco = self._encontrar_coluna(df_norm, "preco")
        
        # Validar se encontrou as colunas essenciais
        if not col_id or not col_descricao or not col_preco:
            colunas_faltantes = []
            if not col_id:
                colunas_faltantes.append("ID (SKU/MLB/ID do Produto)")
            if not col_descricao:
                colunas_faltantes.append("Descrição (Título/Nome)")
            if not col_preco:
                colunas_faltantes.append("Preço")
            
            raise ValueError(f"Não foi possível identificar as colunas: {', '.join(colunas_faltantes)}. Colunas disponíveis: {list(df_norm.columns)}")
        
        # Renomear colunas para o padrão interno
        df_norm = df_norm.rename(columns={
            col_id: "SKU",
            col_descricao: "Descrição",
            col_preco: "Preço"
        })
        
        return df_norm
    
    def filtrar_por_categoria(self, df, categoria="oportunidade", margem_minima=15.0):
        """
        Filtra produtos por categoria (Curva ABC ou Oportunidades)
        
        Args:
            df: DataFrame com dados de produtos
            categoria: "oportunidade", "curva_a", "curva_b", "curva_c", "saudavel", "alerta", "prejuizo"
            margem_minima: Margem mínima para considerar como oportunidade
            
        Returns:
            DataFrame filtrado
        """
        df_filtrado = df.copy()
        
        if categoria.lower() == "oportunidade":
            # Produtos de oportunidade (Curva B/C com margem alta e saudáveis)
            if "Curva ABC" in df_filtrado.columns and "Status" in df_filtrado.columns:
                curva_bc = (df_filtrado["Curva ABC"].astype(str).str.contains("B", na=False)) | \
                           (df_filtrado["Curva ABC"].astype(str).str.contains("C", na=False))
                status_saudavel = df_filtrado["Status"] == "🟢 Saudável"
                
                # Se temos coluna de margem, filtrar por margem
                if "Margem Bruta %" in df_filtrado.columns:
                    margem_alta = df_filtrado["Margem Bruta %"] >= margem_minima
                    df_filtrado = df_filtrado[curva_bc & status_saudavel & margem_alta]
                else:
                    df_filtrado = df_filtrado[curva_bc & status_saudavel]
        
        elif categoria.lower() == "curva_a":
            # Apenas Curva A
            if "Curva ABC" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Curva ABC"].astype(str).str.contains("A", na=False)]
        
        elif categoria.lower() == "curva_b":
            # Apenas Curva B
            if "Curva ABC" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Curva ABC"].astype(str).str.contains("B", na=False)]
        
        elif categoria.lower() == "curva_c":
            # Apenas Curva C
            if "Curva ABC" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Curva ABC"].astype(str).str.contains("C", na=False)]
        
        elif categoria.lower() == "saudavel":
            # Produtos saudáveis
            if "Status" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Status"] == "🟢 Saudável"]
        
        elif categoria.lower() == "alerta":
            # Produtos em alerta
            if "Status" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Status"].astype(str).str.contains("🟡 Alerta", na=False)]
        
        elif categoria.lower() == "prejuizo":
            # Produtos em prejuízo
            if "Status" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Status"].astype(str).str.contains("🔴 Prejuízo", na=False)]
        
        return df_filtrado.reset_index(drop=True)
    
    def mapear_dados_para_marketplace(self, df, desconto_percent=0.0):
        """
        Mapeia dados do dashboard para o formato do marketplace
        
        Args:
            df: DataFrame com dados de produtos
            desconto_percent: Percentual de desconto a aplicar (ex: 0.05 para 5%)
            
        Returns:
            DataFrame formatado para o marketplace
        """
        # Normalizar DataFrame para identificar colunas automaticamente
        df_export = self._normalizar_dataframe(df)
        
        # Calcular preço com desconto
        df_export["Preço_Desconto"] = (df_export["Preço"] * (1 - desconto_percent)).round(2)
        
        # Criar DataFrame no formato do marketplace
        df_marketplace = pd.DataFrame()
        
        for col_marketplace, col_origem in self.template["mapeamento"].items():
            if col_origem is None:
                # Coluna vazia
                df_marketplace[col_marketplace] = ""
            else:
                # Mapear coluna
                df_marketplace[col_marketplace] = df_export[col_origem].astype(str)
        
        return df_marketplace
    
    def exportar_para_excel(self, df_marketplace, nome_sheet="Promoções"):
        """
        Exporta dados para Excel formatado profissionalmente
        
        Args:
            df_marketplace: DataFrame no formato do marketplace
            nome_sheet: Nome da aba Excel
            
        Returns:
            BytesIO com arquivo Excel
        """
        wb = Workbook()
        ws = wb.active
        ws.title = nome_sheet
        
        # Escrever dados
        for r_idx, row in enumerate(dataframe_to_rows(df_marketplace, index=False, header=True), 1):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                
                # Formatação do cabeçalho
                if r_idx == 1:
                    cell.font = Font(bold=True, color="FFFFFF", size=11)
                    cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    # Alternância de cores
                    if r_idx % 2 == 0:
                        cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
                    # Formatação de números (preços)
                    if isinstance(value, (int, float)):
                        cell.number_format = '#,##0.00'
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                
                # Bordas
                thin_border = Border(
                    left=Side(style="thin", color="CCCCCC"),
                    right=Side(style="thin", color="CCCCCC"),
                    top=Side(style="thin", color="CCCCCC"),
                    bottom=Side(style="thin", color="CCCCCC")
                )
                cell.border = thin_border
        
        # Ajustar largura das colunas automaticamente
        for idx, col in enumerate(self.template["colunas"], 1):
            ws.column_dimensions[chr(64 + idx)].width = 20
        
        # Congelar primeira linha
        ws.freeze_panes = "A2"
        
        # Salvar em BytesIO
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    def calcular_impacto(self, df_marketplace, df_original):
        """
        Calcula o impacto econômico das promoções
        
        Args:
            df_marketplace: DataFrame no formato do marketplace
            df_original: DataFrame original com preços
            
        Returns:
            dict com métricas de impacto
        """
        economia_por_produto = df_original["Preço"] - df_marketplace["Preço de desconto"].astype(float)
        desconto_medio_percent = (economia_por_produto / df_original["Preço"] * 100).mean()
        
        return {
            "economia_total": economia_por_produto.sum(),
            "economia_media": economia_por_produto.mean(),
            "desconto_medio_percent": desconto_medio_percent,
            "quantidade_produtos": len(df_marketplace),
        }
    
    def gerar_relatorio_impacto(self, df_marketplace, df_original):
        """
        Gera relatório detalhado do impacto das promoções
        
        Args:
            df_marketplace: DataFrame no formato do marketplace
            df_original: DataFrame original com preços
            
        Returns:
            dict com informações do relatório
        """
        impacto = self.calcular_impacto(df_marketplace, df_original)
        
        return {
            "total_produtos": len(df_marketplace),
            "economia_total": impacto["economia_total"],
            "economia_media_por_produto": impacto["economia_media"],
            "desconto_medio_percent": impacto["desconto_medio_percent"],
            "preco_medio_original": df_original["Preço"].mean(),
            "preco_medio_desconto": df_marketplace["Preço de desconto"].astype(float).mean(),
        }
