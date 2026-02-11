
"""
Módulo para Calculadora de Precificação V2
Implementa a lógica automática baseada em dados do relatório
"""

import pandas as pd
import numpy as np
from config import MERCADO_LIVRE_AD_TYPES, MERCADO_LIVRE_LIMITE_FRETE_GRATIS, SHOPEE_FAIXAS_PRECO, \
    MERCADO_LIVRE_COMISSOES_POR_CATEGORIA_2026, MERCADO_LIVRE_CUSTO_OPERACIONAL_GERAL_2026, \
    MERCADO_LIVRE_SUPERMERCADO_2026, MERCADO_LIVRE_LIVROS_2026


class PricingCalculatorV2:
    """Calcula precificação automática baseada em dados do relatório."""

    def __init__(self, marketplaces, regimes, margem_bruta_alvo, margem_liquida_minima, percent_publicidade, 
                 custo_fixo_operacional=0.0, taxa_devolucao=0.0):
        self.marketplaces = marketplaces
        self.regimes = regimes
        self.margem_bruta_alvo = margem_bruta_alvo
        self.margem_liquida_minima = margem_liquida_minima
        self.percent_publicidade = percent_publicidade
        self.custo_fixo_operacional = custo_fixo_operacional
        self.taxa_devolucao = taxa_devolucao

    def calcular_comissao_shopee(self, preco_venda):
        for faixa in SHOPEE_FAIXAS_PRECO:
            if faixa["min"] <= preco_venda <= faixa["max"]:
                return {
                    "comissao_percent": faixa["comissao_percent"],
                    "comissao_fixa": faixa["comissao_fixa"],
                    "subsidio_pix_percent": faixa["subsidio_pix_percent"],
                    "faixa": faixa["descricao"]
                }
        return {"comissao_percent": 0.20, "comissao_fixa": 4.0, "subsidio_pix_percent": 0.0, "faixa": "Nao identificada"}

    def _calcular_custo_operacional_ml_2026(self, preco_venda, peso, categoria="Produtos Comuns"):
        """
        Calcula o custo operacional do Mercado Livre para 2026.
        Segue rigorosamente as faixas de preço e peso da planilha.
        """
        custo_operacional = 0.0
        faixa_identificada = "N/A"
        cobrada = False

        # Selecionar tabela correta
        tabela_custo = MERCADO_LIVRE_CUSTO_OPERACIONAL_GERAL_2026
        if "Livros" in categoria:
            tabela_custo = MERCADO_LIVRE_LIVROS_2026
        elif "Supermercado" in categoria or "Alimentos e Bebidas" in categoria:
            tabela_custo = MERCADO_LIVRE_SUPERMERCADO_2026

        # Encontrar linha de peso
        linha_peso = None
        for linha in tabela_custo:
            if linha["Peso"] == peso:
                linha_peso = linha
                break
        
        if not linha_peso:
            # Fallback para o primeiro peso se não encontrar exato
            linha_peso = tabela_custo[0]

        # Lógica de faixas de preço (Rigorosa conforme planilha)
        if "Supermercado" in categoria or "Alimentos e Bebidas" in categoria:
            if preco_venda <= 18.99:
                custo_operacional = linha_peso.get("R$ 0-18,99", 0.0)
                faixa_identificada = "R$ 0-18,99"
            elif preco_venda <= 28.99:
                custo_operacional = linha_peso.get("R$ 19-28,99", 0.0)
                faixa_identificada = "R$ 19-28,99"
            elif preco_venda <= 48.99:
                custo_operacional = linha_peso.get("R$ 29-48,99", 0.0)
                faixa_identificada = "R$ 29-48,99"
            elif preco_venda <= 78.99:
                custo_operacional = linha_peso.get("R$ 49-78,99", 0.0)
                faixa_identificada = "R$ 49-78,99"
            elif preco_venda <= 98.99:
                custo_operacional = linha_peso.get("R$ 79-98,99", 0.0)
                faixa_identificada = "R$ 79-98,99"
            elif preco_venda <= 198.99:
                custo_operacional = linha_peso.get("R$ 99-198,99", 0.0)
                faixa_identificada = "R$ 99-198,99"
            else:
                custo_operacional = linha_peso.get("A partir de R$ 199", 0.0)
                faixa_identificada = "A partir de R$ 199"
        else:
            # Geral e Livros
            if preco_venda <= 18.99:
                custo_operacional = linha_peso.get("R$ 0-18,99", 0.0)
                faixa_identificada = "R$ 0-18,99"
            elif preco_venda <= 48.99:
                custo_operacional = linha_peso.get("R$ 19-48,99", 0.0)
                faixa_identificada = "R$ 19-48,99"
            elif preco_venda <= 78.99:
                custo_operacional = linha_peso.get("R$ 49-78,99", 0.0)
                faixa_identificada = "R$ 49-78,99"
            elif preco_venda <= 99.99:
                custo_operacional = linha_peso.get("R$ 79-99,99", 0.0)
                faixa_identificada = "R$ 79-99,99"
            elif preco_venda <= 119.99:
                custo_operacional = linha_peso.get("R$ 100-119,99", 0.0)
                faixa_identificada = "R$ 100-119,99"
            elif preco_venda <= 149.99:
                custo_operacional = linha_peso.get("R$ 120-149,99", 0.0)
                faixa_identificada = "R$ 120-149,99"
            elif preco_venda <= 199.99:
                custo_operacional = linha_peso.get("R$ 150-199,99", 0.0)
                faixa_identificada = "R$ 150-199,99"
            else:
                custo_operacional = linha_peso.get("A partir de R$ 200", 0.0)
                faixa_identificada = "A partir de R$ 200"

        # Conforme solicitado, o Custo Fixo foi extinto. 
        # No entanto, a planilha ainda mostra valores para faixas abaixo de R$ 79.
        # Se o usuário quer "retirar a parte de Regras Custo Fixo", isso significa que 
        # para produtos < R$ 79, o custo operacional deve ser 0.
        if preco_venda < MERCADO_LIVRE_LIMITE_FRETE_GRATIS:
            custo_operacional = 0.0
            cobrada = False
        else:
            cobrada = True

        return {"custo_operacional": custo_operacional, "cobrada": cobrada, "faixa": faixa_identificada}

    def calcular_curva_abc(self, df_com_faturamento):
        faturamento_total = df_com_faturamento['Faturamento'].sum()
        df_ordenado = df_com_faturamento.sort_values('Faturamento', ascending=False).reset_index(drop=True)
        df_ordenado['Faturamento_Acumulado'] = df_ordenado['Faturamento'].cumsum()
        df_ordenado['Percentual_Acumulado'] = (df_ordenado['Faturamento_Acumulado'] / faturamento_total) * 100
        def classificar_abc(percentual):
            if percentual <= 80: return "A"
            elif percentual <= 95: return "B"
            else: return "C"
        df_ordenado['Curva ABC'] = df_ordenado['Percentual_Acumulado'].apply(classificar_abc)
        return df_ordenado[['Curva ABC']].reset_index(drop=True)
    
    def obter_config_marketplace(self, marketplace, tipo_anuncio="", categoria="Produtos Comuns"):
        if marketplace == "Mercado Livre":
            comissoes_categoria = MERCADO_LIVRE_COMISSOES_POR_CATEGORIA_2026.get(categoria, {"classico": 0.14, "premium": 0.19})
            if tipo_anuncio == "Clássico":
                return {"comissao": comissoes_categoria["classico"], "custo_fixo": 0.0}
            elif tipo_anuncio == "Premium":
                return {"comissao": comissoes_categoria["premium"], "custo_fixo": 0.0}
            else:
                return {"comissao": comissoes_categoria["classico"], "custo_fixo": 0.0}
        return self.marketplaces.get(marketplace, {"comissao": 0.0, "custo_fixo": 0.0})

    def calcular_linha(self, sku, descricao, custo_produto, frete, preco_atual, marketplace, regime_tributario, 
                       tipo_anuncio="", categoria="Produtos Comuns", peso="Até 0,3 kg"):
        config_mkt = self.obter_config_marketplace(marketplace, tipo_anuncio, categoria)
        taxa_comissao = config_mkt["comissao"]
        
        # Cálculo do Custo Operacional (Frete Grátis) para Mercado Livre 2026
        taxa_fixa_cobrada = False
        faixa_taxa_fixa = "N/A"
        if marketplace == "Mercado Livre":
            res_ml = self._calcular_custo_operacional_ml_2026(preco_atual, peso, categoria)
            taxa_fixa = res_ml["custo_operacional"]
            taxa_fixa_cobrada = res_ml["cobrada"]
            faixa_taxa_fixa = res_ml["faixa"]
        elif marketplace == "Shopee":
            res_shopee = self.calcular_comissao_shopee(preco_atual)
            taxa_comissao = res_shopee["comissao_percent"]
            taxa_fixa = res_shopee["comissao_fixa"]
            faixa_taxa_fixa = res_shopee["faixa"]
        else:
            taxa_fixa = config_mkt["custo_fixo"]

        # Impostos
        config_regime = self.regimes.get(regime_tributario, self.regimes["Simples Nacional"])
        impostos_percent = config_regime["ibs"] + config_regime["cbs"] + config_regime["impostos_encargos"]
        impostos_valor = preco_atual * impostos_percent

        # Comissões e Taxas
        comissao_valor = preco_atual * taxa_comissao
        publicidade_valor = preco_atual * (self.percent_publicidade / 100)
        
        # Margens
        margem_bruta_valor = preco_atual - custo_produto - frete - comissao_valor - taxa_fixa - impostos_valor
        margem_bruta_percent = (margem_bruta_valor / preco_atual) * 100 if preco_atual > 0 else 0
        
        margem_liquida_valor = margem_bruta_valor - publicidade_valor
        margem_liquida_percent = (margem_liquida_valor / preco_atual) * 100 if preco_atual > 0 else 0

        # Status
        status = "🟢 Saudável"
        if margem_liquida_percent < 0:
            status = "🔴 Prejuízo/Abaixo"
        elif margem_liquida_percent < self.margem_liquida_minima:
            status = "🟡 Alerta"

        return {
            "SKU ou MLB": sku,
            "Titulo": descricao,
            "Tipo de Anuncio": tipo_anuncio,
            "Preco Atual (R$)": preco_atual,
            "Custo Produto": custo_produto,
            "Frete": frete,
            "Taxa Comissao %": f"{taxa_comissao*100:.2f}%",
            "Taxa Fixa R$": taxa_fixa,
            "Taxa Fixa Cobrada": "Sim" if taxa_fixa_cobrada else "Não",
            "Faixa Taxa Fixa": faixa_taxa_fixa,
            "Comissao R$": comissao_valor,
            "Impostos": impostos_valor,
            "Publicidade": publicidade_valor,
            "Lucro R$": margem_liquida_valor,
            "Margem Bruta %": margem_bruta_percent,
            "Margem Liquida %": margem_liquida_percent,
            "Status": status
        }

    def calcular_dataframe(self, df, marketplace, regime_tributario):
        """
        Calcula precificação para múltiplas linhas
        """
        resultados = []
        
        for _, row in df.iterrows():
            tipo_anuncio = row.get("Tipo de Anúncio", row.get("Tipo de Anuncio", ""))
            categoria = row.get("Categoria", "Produtos Comuns")
            peso = row.get("Peso", "Até 0,3 kg")
            
            resultado = self.calcular_linha(
                sku=row.get("SKU", row.get("SKU ou MLB", "")),
                descricao=row.get("Título", row.get("Titulo", row.get("Descrição", ""))),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                preco_atual=float(row.get("Preço Atual", row.get("Preco Atual (R$)", 0)) or 0),
                marketplace=marketplace,
                regime_tributario=regime_tributario,
                tipo_anuncio=tipo_anuncio,
                categoria=categoria,
                peso=peso
            )
            resultados.append(resultado)
        
        df_resultado = pd.DataFrame(resultados)
        
        # Calcular Curva ABC se houver coluna de Quantidade Vendida ou Vendas/Mês
        col_vendas = "Quantidade Vendida" if "Quantidade Vendida" in df.columns else ("Vendas/Mês" if "Vendas/Mês" in df.columns else None)
        if col_vendas:
            df_temp = df.copy()
            preco_col = "Preço Atual" if "Preço Atual" in df.columns else "Preco Atual (R$)"
            df_temp['Faturamento'] = df_temp[preco_col] * df_temp[col_vendas]
            curva_abc = self.calcular_curva_abc(df_temp)
            df_resultado['Curva ABC'] = curva_abc['Curva ABC']
        else:
            df_resultado['Curva ABC'] = "N/A"
        
        # Filtrar colunas baseado no marketplace
        colunas_exibir = self.obter_colunas_por_marketplace(marketplace)
        colunas_existentes = [col for col in colunas_exibir if col in df_resultado.columns]
        
        return df_resultado[colunas_existentes]

    def obter_colunas_por_marketplace(self, marketplace):
        """
        Retorna as colunas que devem ser exibidas baseado no marketplace
        """
        if marketplace == "Mercado Livre":
            return [
                "SKU ou MLB", "Titulo", "Tipo de Anuncio", "Taxa Comissao %", "Taxa Fixa R$", 
                "Taxa Fixa Cobrada", "Faixa Taxa Fixa", "Preco Atual (R$)", "Custo Produto", 
                "Frete", "Comissao R$", "Impostos", "Publicidade", "Lucro R$", 
                "Margem Bruta %", "Margem Liquida %", "Curva ABC", "Status"
            ]
        elif marketplace == "Shopee":
            return [
                "SKU ou MLB", "Titulo", "Taxa Comissao %", "Taxa Fixa R$", "Faixa Taxa Fixa", 
                "Preco Atual (R$)", "Custo Produto", "Frete", "Comissao R$", "Impostos", 
                "Publicidade", "Lucro R$", "Margem Bruta %", "Margem Liquida %", "Curva ABC", "Status"
            ]
        else:
            return [
                "SKU ou MLB", "Titulo", "Taxa Comissao %", "Preco Atual (R$)", "Custo Produto", 
                "Frete", "Comissao R$", "Impostos", "Publicidade", "Lucro R$", 
                "Margem Bruta %", "Margem Liquida %", "Curva ABC", "Status"
            ]
