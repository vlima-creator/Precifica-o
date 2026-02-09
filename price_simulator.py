"""
Módulo para Simulador de Preço Alvo V2
Implementa a lógica automática baseada em dados do relatório
"""

import pandas as pd
import numpy as np
from config import MERCADO_LIVRE_AD_TYPES


class PriceSimulator:
    """Simula preços alvo de forma automática baseado em dados do relatório."""

    def __init__(self, marketplaces, regimes, margem_bruta_alvo, margem_liquida_minima, percent_publicidade,
                 custo_fixo_operacional=0.0, taxa_devolucao=0.0):
        """
        Inicializa o simulador
        
        Args:
            marketplaces: Dict com configurações de marketplaces
            regimes: Dict com configurações de regimes tributários
            margem_bruta_alvo: Margem bruta alvo (%)
            margem_liquida_minima: Margem líquida mínima (%)
            percent_publicidade: % de publicidade
            custo_fixo_operacional: Custo fixo operacional (R$)
            taxa_devolucao: Taxa de devoluções e trocas (%)
        """
        self.marketplaces = marketplaces
        self.regimes = regimes
        self.margem_bruta_alvo = margem_bruta_alvo
        self.margem_liquida_minima = margem_liquida_minima
        self.percent_publicidade = percent_publicidade
        self.custo_fixo_operacional = custo_fixo_operacional
        self.taxa_devolucao = taxa_devolucao

    def obter_config_marketplace(self, marketplace, tipo_anuncio=""):
        """
        Obtém configuração do marketplace, considerando tipo de anúncio para Mercado Livre
        
        Args:
            marketplace: Nome do marketplace
            tipo_anuncio: Tipo de anúncio (para Mercado Livre: "Clássico" ou "Premium")
            
        Returns:
            Dict com configuração (comissao, custo_fixo)
        """
        # Se é Mercado Livre e tem tipo de anúncio especificado
        if marketplace == "Mercado Livre" and tipo_anuncio and tipo_anuncio in MERCADO_LIVRE_AD_TYPES:
            return MERCADO_LIVRE_AD_TYPES[tipo_anuncio]
        
        # Caso contrário, usar configuração padrão do marketplace
        return self.marketplaces.get(marketplace, {"comissao": 0.0, "custo_fixo": 0.0})

    def calcular_linha(self, sku, descricao, custo_produto, frete, 
                       marketplace, regime_tributario, tipo_anuncio=""):
        """
        Calcula simulação de preço para uma linha
        
        Args:
            sku: SKU do produto
            descricao: Descrição do produto
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            marketplace: Nome do marketplace
            regime_tributario: Regime tributário
            tipo_anuncio: Tipo de anúncio (opcional, para Mercado Livre)
            
        Returns:
            Dict com simulação de preço
        """
        # Obter configurações (considerando tipo de anúncio)
        mp_config = self.obter_config_marketplace(marketplace, tipo_anuncio)
        comissao_percent = mp_config.get("comissao", 0.0)
        taxa_fixa = mp_config.get("custo_fixo", 0.0)
        
        regime_config = self.regimes.get(regime_tributario, {})
        impostos_percent = regime_config.get("impostos_encargos", 0.0)
        
        # Custo total direto
        custo_total_direto = custo_produto + frete + taxa_fixa + self.custo_fixo_operacional
        
        # Taxas variáveis (em decimal)
        taxas_variaveis = (comissao_percent + impostos_percent + (self.percent_publicidade / 100) + (self.taxa_devolucao / 100))
        
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
            df: DataFrame com colunas: SKU, Descrição, Custo Produto, Frete, Tipo de Anúncio (opcional)
            marketplace: Marketplace selecionado
            regime_tributario: Regime tributário selecionado
                
        Returns:
            DataFrame com simulação de preços
        """
        resultados = []
        
        for _, row in df.iterrows():
            tipo_anuncio = row.get("Tipo de Anúncio", "")
            
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                descricao=row.get("Descrição", ""),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                marketplace=marketplace,
                regime_tributario=regime_tributario,
                tipo_anuncio=tipo_anuncio,
            )
            resultados.append(resultado)
        
        df_resultado = pd.DataFrame(resultados)
        
        # Calcular Curva ABC se houver coluna de Quantidade Vendida
        if "Quantidade Vendida" in df.columns:
            # Calcular faturamento (preco_atual * quantidade_vendida)
            df_temp = df.copy()
            df_temp['Faturamento'] = df_temp['Preço Atual'] * df_temp['Quantidade Vendida']
            
            # Calcular Curva ABC
            curva_abc = self.calcular_curva_abc(df_temp)
            df_resultado['Curva ABC'] = curva_abc['Curva ABC']
        
        return df_resultado
    
    def calcular_curva_abc(self, df):
        """
        Calcula a Curva ABC baseado no faturamento
        
        Args:
            df: DataFrame com coluna 'Faturamento'
            
        Returns:
            DataFrame com coluna 'Curva ABC' (A, B ou C)
        """
        if 'Faturamento' not in df.columns or len(df) == 0:
            return pd.DataFrame({'Curva ABC': ['C'] * len(df)})
        
        # Ordenar por faturamento (maior para menor)
        df_sorted = df.sort_values('Faturamento', ascending=False).reset_index(drop=True)
        
        # Calcular faturamento total
        total_faturamento = df_sorted['Faturamento'].sum()
        
        if total_faturamento == 0:
            return pd.DataFrame({'Curva ABC': ['C'] * len(df)})
        
        # Calcular faturamento acumulado em percentual
        df_sorted['Faturamento Acumulado %'] = (df_sorted['Faturamento'].cumsum() / total_faturamento * 100)
        
        # Classificar em Curva A (80%), B (15%), C (5%)
        def classificar_curva(percentual):
            if percentual <= 80:
                return 'A'
            elif percentual <= 95:
                return 'B'
            else:
                return 'C'
        
        df_sorted['Curva ABC'] = df_sorted['Faturamento Acumulado %'].apply(classificar_curva)
        
        # Retornar na ordem original
        return df_sorted[['Curva ABC']].reset_index(drop=True)
