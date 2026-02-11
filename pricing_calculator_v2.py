"""
Módulo para Calculadora de Precificação V2 - ATUALIZADO PARA MARÇO 2026
Implementa a lógica automática baseada em dados do relatório
Versão com suporte às novas regras de custo operacional do Mercado Livre
"""

import pandas as pd
import numpy as np
from config import MERCADO_LIVRE_AD_TYPES, MERCADO_LIVRE_LIMITE_TAXA_FIXA, SHOPEE_FAIXAS_PRECO
from mercado_livre_costs import MercadoLivreCostsCalculator


class PricingCalculatorV2:
    """Calcula precificação automática baseada em dados do relatório."""

    def __init__(self, marketplaces, regimes, margem_bruta_alvo, margem_liquida_minima, percent_publicidade, 
                 custo_fixo_operacional=0.0, taxa_devolucao=0.0):
        """
        Inicializa a calculadora
        
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

    def calcular_comissao_shopee(self, preco_venda):
        """
        Calcula a comissao e subsidio Pix da Shopee baseado na faixa de preco
        
        Args:
            preco_venda: Preco de venda em R$
            
        Returns:
            dict com comissao_percent, comissao_fixa, subsidio_pix_percent e faixa
        """
        for faixa in SHOPEE_FAIXAS_PRECO:
            if faixa["min"] <= preco_venda <= faixa["max"]:
                return {
                    "comissao_percent": faixa["comissao_percent"],
                    "comissao_fixa": faixa["comissao_fixa"],
                    "subsidio_pix_percent": faixa["subsidio_pix_percent"],
                    "faixa": faixa["descricao"]
                }
        
        # Fallback (nao deve chegar aqui)
        return {
            "comissao_percent": 0.20,
            "comissao_fixa": 4.0,
            "subsidio_pix_percent": 0.0,
            "faixa": "Nao identificada"
        }
    
    def calcular_taxa_fixa_mercado_livre(self, preco_venda, categoria="Produtos Comuns"):
        """
        DEPRECADO: Use MercadoLivreCostsCalculator em vez desta função.
        Mantida para compatibilidade com código legado.
        
        Calcula a taxa fixa do Mercado Livre baseada na faixa de preço (Válido até 01/03/2026)
        
        Args:
            preco_venda: Preço de venda em R$
            categoria: Categoria do produto ("Produtos Comuns" ou "Livros")
            
        Returns:
            dict com taxa_fixa (valor em R$) e cobrada (bool)
        """
        # Se preço > limite, não cobra taxa fixa
        if preco_venda > MERCADO_LIVRE_LIMITE_TAXA_FIXA:
            return {"taxa_fixa": 0.0, "cobrada": False, "faixa": "Acima de R$ 79,00"}
        
        # Buscar faixa correta
        faixas = MERCADO_LIVRE_TAXA_FIXA.get(categoria, MERCADO_LIVRE_TAXA_FIXA["Produtos Comuns"])
        
        for faixa in faixas:
            if faixa["min"] <= preco_venda <= faixa["max"]:
                return {
                    "taxa_fixa": faixa["taxa_fixa"],
                    "cobrada": True,
                    "faixa": f"R$ {faixa['min']:.0f} - R$ {faixa['max']:.0f}"
                }
        
        # Fallback (não deve chegar aqui)
        return {"taxa_fixa": 0.0, "cobrada": False, "faixa": "Não identificada"}
    
    def calcular_curva_abc(self, df_com_faturamento):
        """
        Calcula a Curva ABC baseado no faturamento de cada produto
        
        Args:
            df_com_faturamento: DataFrame com coluna Faturamento calculada
            
        Returns:
            Series com classificacao ABC para cada linha
        """
        # Calcular faturamento total
        faturamento_total = df_com_faturamento['Faturamento'].sum()
        
        # Ordenar por faturamento em ordem decrescente
        df_ordenado = df_com_faturamento.sort_values('Faturamento', ascending=False).reset_index(drop=True)
        
        # Calcular faturamento acumulado
        df_ordenado['Faturamento_Acumulado'] = df_ordenado['Faturamento'].cumsum()
        df_ordenado['Percentual_Acumulado'] = (df_ordenado['Faturamento_Acumulado'] / faturamento_total) * 100
        
        # Classificar em A, B ou C
        def classificar_abc(percentual):
            if percentual <= 80:
                return "A"
            elif percentual <= 95:
                return "B"
            else:
                return "C"
        
        df_ordenado['Curva ABC'] = df_ordenado['Percentual_Acumulado'].apply(classificar_abc)
        
        # Retornar em ordem original
        return df_ordenado[['Curva ABC']].reset_index(drop=True)
    
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

    def calcular_linha(self, sku, descricao, custo_produto, frete, preco_atual, 
                       marketplace, regime_tributario, tipo_anuncio="", peso_kg=0.0, tipo_logistica_ml="Full", categoria_ml="Produtos Comuns"):
        """
        Calcula uma linha da Calculadora de Precificação
        
        Args:
            sku: SKU do produto
            descricao: Descrição do produto
            custo_produto: Custo do produto (R$)
            frete: Frete (R$)
            preco_atual: Preço atual (R$)
            marketplace: Nome do marketplace
            regime_tributario: Regime tributário
            tipo_anuncio: Tipo de anúncio (opcional, para Mercado Livre)
            peso_kg: Peso do produto em kg (novo parâmetro para Mercado Livre - válido a partir de 02/03/2026)
            tipo_logistica_ml: Tipo de logística do Mercado Livre ("Full" ou "Flex") - válido a partir de 02/03/2026
            categoria_ml: Categoria do produto no Mercado Livre ("Produtos Comuns" ou "Livros")
            
        Returns:
            Dict com todos os cálculos
        """
        # Inicializar variaveis
        taxa_fixa_info = {"cobrada": False, "faixa": "Nao aplicavel"}
        subsidio_pix = 0.0
        subsidio_pix_info = {"subsidio_pix_percent": 0.0, "faixa": "Nao aplicavel"}
        
        # Calcular comissao e taxa fixa baseado no marketplace
        if marketplace == "Shopee":
            # Para Shopee, usar comissao variavel por faixa de preco
            shopee_config = self.calcular_comissao_shopee(preco_atual)
            comissao_percent = shopee_config["comissao_percent"]
            taxa_fixa = shopee_config["comissao_fixa"]
            subsidio_pix = preco_atual * shopee_config["subsidio_pix_percent"]
            subsidio_pix_info = {
                "subsidio_pix_percent": shopee_config["subsidio_pix_percent"] * 100,
                "faixa": shopee_config["faixa"]
            }
        else:
            # Para Mercado Livre e outros marketplaces, usar configuracao padrao
            mp_config = self.obter_config_marketplace(marketplace, tipo_anuncio)
            comissao_percent = mp_config.get("comissao", 0.0)
            taxa_fixa = mp_config.get("custo_fixo", 0.0)
        
        # Obter configurações do regime tributário
        regime_config = self.regimes.get(regime_tributario, {})
        impostos_percent = regime_config.get("impostos_encargos", 0.0)
        
        # Calcular taxa fixa/custo operacional do Mercado Livre se aplicavel (Valido a partir de 02/03/2026)
        if marketplace == "Mercado Livre":
            # Usar novo calculo de custos operacionais baseado em peso e logistica
            custo_info = MercadoLivreCostsCalculator.calcular_custo_total_ml(
                preco_atual, peso_kg, tipo_logistica_ml, categoria_ml
            )
            
            # Extrair o custo (pode ser custo_operacional, taxa_fixa ou custo_frete)
            if "custo_operacional" in custo_info:
                taxa_fixa = custo_info["custo_operacional"]
                taxa_fixa_info = {
                    "cobrada": True,
                    "faixa": custo_info["faixa_peso"] + " | " + custo_info["faixa_preco"],
                    "tipo": custo_info["tipo"]
                }
            elif "taxa_fixa" in custo_info:
                taxa_fixa = custo_info["taxa_fixa"]
                taxa_fixa_info = {
                    "cobrada": taxa_fixa > 0,
                    "faixa": custo_info["faixa_preco"],
                    "tipo": custo_info["tipo"]
                }
            elif "custo_frete" in custo_info:
                taxa_fixa = custo_info["custo_frete"]
                taxa_fixa_info = {
                    "cobrada": True,
                    "faixa": custo_info["faixa_peso"] + " | " + custo_info["faixa_preco"],
                    "tipo": custo_info["tipo"]
                }
            else:
                taxa_fixa = 0.0
                taxa_fixa_info = {"cobrada": False, "faixa": "Erro no calculo", "tipo": "Erro"}
        
        # Calculos
        comissao = preco_atual * comissao_percent
        impostos = preco_atual * impostos_percent
        publicidade = preco_atual * (self.percent_publicidade / 100)
        devoluoes = preco_atual * (self.taxa_devolucao / 100)
        lucro = preco_atual - custo_produto - frete - comissao - taxa_fixa - impostos - publicidade - devoluoes - (self.custo_fixo_operacional / 100 * preco_atual) + subsidio_pix
        
        # Calcular custos operacionais em valor (era percentual)
        custo_fixo_op_valor = (self.custo_fixo_operacional / 100 * preco_atual)
        
        margem_bruta = (lucro / preco_atual * 100) if preco_atual > 0 else 0
        
        # Determinar status
        if margem_bruta >= self.margem_bruta_alvo:
            status = "🟢 Saudável"
        elif margem_bruta >= self.margem_liquida_minima:
            status = "🟡 Alerta"
        else:
            status = "🔴 Prejuízo"
        
        # Determinar tipo de anúncio para exibição
        tipo_anuncio_exibicao = tipo_anuncio if tipo_anuncio else "Padrão"
        if marketplace != "Mercado Livre":
            tipo_anuncio_exibicao = "N/A"
        
        return {
            "SKU ou MLB": sku,
            "Titulo": descricao,
            "Tipo de Anuncio": tipo_anuncio_exibicao,
            "Taxa Comissao %": f"{comissao_percent * 100:.2f}%",
            "Taxa Fixa R$": taxa_fixa,
            "Taxa Fixa Cobrada": "Sim" if taxa_fixa_info["cobrada"] else "Nao",
            "Faixa Taxa Fixa": taxa_fixa_info["faixa"],
            "Faixa Shopee": subsidio_pix_info["faixa"],
            "Subsidio Pix %": f"{subsidio_pix_info['subsidio_pix_percent']:.2f}%",
            "Subsidio Pix R$": subsidio_pix,
            "Preco Atual (R$)": preco_atual,
            "Custo Produto": custo_produto,
            "Frete": frete,
            "Comissao R$": comissao,
            "Custo Fixo Op.": self.custo_fixo_operacional,
            "Impostos": impostos,
            "Publicidade": publicidade,
            "Subsidio Pix (Credito)": subsidio_pix,
            "Lucro R$": lucro,
            "Margem Bruta %": margem_bruta,
            "Margem Liquida %": margem_bruta,
            "Status": status,
        }

    def obter_colunas_por_marketplace(self, marketplace):
        """
        Retorna as colunas que devem ser exibidas baseado no marketplace
        
        Args:
            marketplace: Nome do marketplace
            
        Returns:
            Lista de colunas a exibir
        """
        if marketplace == "Mercado Livre":
            # Colunas especificas do Mercado Livre
            return [
                "SKU ou MLB",
                "Titulo",
                "Tipo de Anuncio",
                "Taxa Comissao %",
                "Taxa Fixa R$",
                "Taxa Fixa Cobrada",
                "Faixa Taxa Fixa",
                "Preco Atual (R$)",
                "Custo Produto",
                "Frete",
                "Comissao R$",
                "Impostos",
                "Publicidade",
                "Lucro R$",
                "Margem Bruta %",
                "Margem Liquida %",
                "Curva ABC",
                "Categoria",
                "Status",
            ]
        elif marketplace == "Shopee":
            # Colunas especificas da Shopee
            return [
                "SKU ou MLB",
                "Titulo",
                "Taxa Comissao %",
                "Faixa Shopee",
                "Subsidio Pix %",
                "Preco Atual (R$)",
                "Custo Produto",
                "Frete",
                "Comissao R$",
                "Impostos",
                "Publicidade",
                "Lucro R$",
                "Margem Bruta %",
                "Status",
            ]
        else:
            # Colunas padrão para outros marketplaces
            return [
                "SKU ou MLB",
                "Titulo",
                "Taxa Comissao %",
                "Preco Atual (R$)",
                "Custo Produto",
                "Frete",
                "Comissao R$",
                "Impostos",
                "Publicidade",
                "Lucro R$",
                "Margem Bruta %",
                "Status",
            ]

    def calcular_dataframe(self, df, marketplace, regime_tributario):
        """
        Calcula precificação para múltiplas linhas
        
        Args:
            df: DataFrame com colunas: SKU, Descrição, Custo Produto, Frete, Preço Atual, Tipo de Anúncio (opcional), Peso (opcional para ML)
            marketplace: Marketplace selecionado
            regime_tributario: Regime tributário selecionado
                
        Returns:
            DataFrame com cálculos completos
        """
        resultados = []
        
        for _, row in df.iterrows():
            tipo_anuncio = row.get("Tipo de Anúncio", "")
            
            # Novos parâmetros para Mercado Livre (válido a partir de 02/03/2026)
            peso_kg = float(row.get("Peso", 0.0) or 0.0) if "Peso" in row else 0.0
            tipo_logistica_ml = row.get("Tipo de Logística", "Full") if "Tipo de Logística" in row else "Full"
            
            # Mapeamento automático de categoria (se vazio ou não informado)
            categoria_ml = row.get("Categoria", "")
            if not categoria_ml or categoria_ml == "" or categoria_ml == "nan":
                # Tentar identificar pelo título/descrição
                titulo = str(row.get("Descrição", "")).lower()
                if any(word in titulo for word in ["livro", "book", "bíblia", "biblia", "hq", "manga"]):
                    categoria_ml = "Livros"
                elif any(word in titulo for word in ["bebida", "comida", "alimento", "snack", "doce", "café", "azeite"]):
                    categoria_ml = "Supermercado"
                else:
                    categoria_ml = "Produtos Comuns"
            
            resultado = self.calcular_linha(
                sku=row.get("SKU", ""),
                descricao=row.get("Descrição", ""),
                custo_produto=float(row.get("Custo Produto", 0) or 0),
                frete=float(row.get("Frete", 0) or 0),
                preco_atual=float(row.get("Preço Atual", 0) or 0),
                marketplace=marketplace,
                regime_tributario=regime_tributario,
                tipo_anuncio=tipo_anuncio,
                peso_kg=peso_kg,
                tipo_logistica_ml=tipo_logistica_ml,
                categoria_ml=categoria_ml,
            )
            resultados.append(resultado)
        
        df_resultado = pd.DataFrame(resultados)
        
        # Adicionar coluna de Categoria ao resultado final
        if "Categoria" not in df_resultado.columns:
            # Re-extrair categorias para o dataframe de resultado
            categorias_finais = []
            for _, row in df.iterrows():
                cat = row.get("Categoria", "")
                if not cat or cat == "" or cat == "nan":
                    titulo = str(row.get("Descrição", "")).lower()
                    if any(word in titulo for word in ["livro", "book", "bíblia", "biblia", "hq", "manga"]): cat = "Livros"
                    elif any(word in titulo for word in ["bebida", "comida", "alimento", "snack", "doce", "café", "azeite"]): cat = "Supermercado"
                    else: cat = "Produtos Comuns"
                categorias_finais.append(cat)
            df_resultado["Categoria"] = categorias_finais

        # Calcular Curva ABC se houver coluna de Quantidade Vendida
        if "Quantidade Vendida" in df.columns:
            # Calcular faturamento (preco_atual * quantidade_vendida)
            df_temp = df.copy()
            df_temp['Faturamento'] = df_temp['Preço Atual'] * df_temp['Quantidade Vendida']
            
            # Calcular Curva ABC
            curva_abc = self.calcular_curva_abc(df_temp)
            df_resultado['Curva ABC'] = curva_abc['Curva ABC']
        
        # Filtrar colunas baseado no marketplace
        colunas_exibir = self.obter_colunas_por_marketplace(marketplace)
        colunas_existentes = [col for col in colunas_exibir if col in df_resultado.columns]
        
        return df_resultado[colunas_existentes]
