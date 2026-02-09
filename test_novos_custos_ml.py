"""
Testes para validar a nova lógica de custos do Mercado Livre (Válido a partir de 02/03/2026)
"""

from mercado_livre_costs import MercadoLivreCostsCalculator
from pricing_calculator_v2 import PricingCalculatorV2
from config import DEFAULT_MARKETPLACES, DEFAULT_REGIMES


def testar_custo_operacional_full():
    """Testa o cálculo de custo operacional para logística Full."""
    print("=" * 80)
    print("TESTE 1: Custo Operacional para Logística Full (Produtos abaixo de R$ 79)")
    print("=" * 80)
    
    # Caso 1: Produto de 400g vendido a R$ 45
    resultado = MercadoLivreCostsCalculator.calcular_custo_operacional_full(45.00, 0.4, "Produtos Comuns")
    print(f"\nProduto: 400g, Preço: R$ 45,00")
    print(f"Resultado: R$ {resultado['custo_operacional']:.2f}")
    print(f"Faixa de Peso: {resultado['faixa_peso']}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['custo_operacional'] == 6.65, "Custo esperado: R$ 6,65"
    print("✓ PASSOU")
    
    # Caso 2: Produto de 300g vendido a R$ 12
    resultado = MercadoLivreCostsCalculator.calcular_custo_operacional_full(12.00, 0.25, "Produtos Comuns")
    print(f"\nProduto: 250g, Preço: R$ 12,00")
    print(f"Resultado: R$ {resultado['custo_operacional']:.2f}")
    print(f"Faixa de Peso: {resultado['faixa_peso']}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['custo_operacional'] == 5.65, "Custo esperado: R$ 5,65"
    print("✓ PASSOU")
    
    # Caso 3: Livro de 500g vendido a R$ 35
    resultado = MercadoLivreCostsCalculator.calcular_custo_operacional_full(35.00, 0.5, "Livros")
    print(f"\nLivro: 500g, Preço: R$ 35,00")
    print(f"Resultado: R$ {resultado['custo_operacional']:.2f}")
    print(f"Faixa de Peso: {resultado['faixa_peso']}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['custo_operacional'] == 3.38, "Custo esperado: R$ 3,38"
    print("✓ PASSOU")


def testar_taxa_fixa_flex():
    """Testa o cálculo de taxa fixa para logística Flex."""
    print("\n" + "=" * 80)
    print("TESTE 2: Taxa Fixa para Logística Flex (Produtos abaixo de R$ 79)")
    print("=" * 80)
    
    # Caso 1: Produto vendido a R$ 15
    resultado = MercadoLivreCostsCalculator.calcular_taxa_fixa_flex(15.00, "Produtos Comuns")
    print(f"\nProduto: Preço R$ 15,00")
    print(f"Resultado: R$ {resultado['taxa_fixa']:.2f}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['taxa_fixa'] == 6.25, "Taxa esperada: R$ 6,25"
    print("✓ PASSOU")
    
    # Caso 2: Produto vendido a R$ 35
    resultado = MercadoLivreCostsCalculator.calcular_taxa_fixa_flex(35.00, "Produtos Comuns")
    print(f"\nProduto: Preço R$ 35,00")
    print(f"Resultado: R$ {resultado['taxa_fixa']:.2f}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['taxa_fixa'] == 6.65, "Taxa esperada: R$ 6,65"
    print("✓ PASSOU")
    
    # Caso 3: Livro vendido a R$ 25
    resultado = MercadoLivreCostsCalculator.calcular_taxa_fixa_flex(25.00, "Livros")
    print(f"\nLivro: Preço R$ 25,00")
    print(f"Resultado: R$ {resultado['taxa_fixa']:.2f}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['taxa_fixa'] == 3.50, "Taxa esperada: R$ 3,50"
    print("✓ PASSOU")


def testar_frete_gratis_full():
    """Testa o cálculo de frete para logística Full com produtos acima de R$ 79."""
    print("\n" + "=" * 80)
    print("TESTE 3: Frete Grátis para Logística Full (Produtos acima de R$ 79)")
    print("=" * 80)
    
    # Caso 1: Produto de 400g vendido a R$ 90 (exemplo do comunicado)
    resultado = MercadoLivreCostsCalculator.calcular_frete_gratis_full(90.00, 0.4, "Produtos Comuns")
    print(f"\nProduto: 400g, Preço: R$ 90,00")
    print(f"Resultado: R$ {resultado['custo_frete']:.2f}")
    print(f"Faixa de Peso: {resultado['faixa_peso']}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado['custo_frete'] == 13.25, "Custo esperado: R$ 13,25"
    print("✓ PASSOU (Exemplo do comunicado: 300-500g entre R$ 79-99,99 = R$ 13,25)")
    
    # Caso 2: Produto de 300g vendido a R$ 150
    resultado = MercadoLivreCostsCalculator.calcular_frete_gratis_full(150.00, 0.25, "Produtos Comuns")
    print(f"\nProduto: 250g, Preço: R$ 150,00")
    print(f"Resultado: R$ {resultado['custo_frete']:.2f}")
    print(f"Faixa de Peso: {resultado['faixa_peso']}")
    print(f"Faixa de Preço: {resultado['faixa_preco']}")
    print(f"Tipo: {resultado['tipo']}")
    assert resultado["custo_frete"] == 18.45, "Custo esperado: R$ 18,45"
    print("✓ PASSOU")


def testar_integracao_pricing_calculator():
    """Testa a integração com a PricingCalculatorV2."""
    print("\n" + "=" * 80)
    print("TESTE 4: Integração com PricingCalculatorV2")
    print("=" * 80)
    
    calculator = PricingCalculatorV2(
        marketplaces=DEFAULT_MARKETPLACES,
        regimes=DEFAULT_REGIMES,
        margem_bruta_alvo=30.0,
        margem_liquida_minima=10.0,
        percent_publicidade=0.0,
        custo_fixo_operacional=0.0,
        taxa_devolucao=2.0
    )
    
    # Teste 1: Produto com logística Full, preço abaixo de R$ 79
    resultado = calculator.calcular_linha(
        sku="MLB123456789",
        descricao="Produto Teste 1",
        custo_produto=20.00,
        frete=5.00,
        preco_atual=45.00,
        marketplace="Mercado Livre",
        regime_tributario="Lucro Real",
        tipo_anuncio="Clássico",
        peso_kg=0.4,
        tipo_logistica_ml="Full",
        categoria_ml="Produtos Comuns"
    )
    
    print(f"\nTeste 1: Produto com Logística Full, Preço R$ 45,00, Peso 400g")
    print(f"Taxa Fixa: R$ {resultado['Taxa Fixa R$']:.2f}")
    print(f"Faixa: {resultado['Faixa Taxa Fixa']}")
    print(f"Lucro: R$ {resultado['Lucro R$']:.2f}")
    print(f"Margem: {resultado['Margem Bruta %']:.2f}%")
    print(f"Status: {resultado['Status']}")
    assert resultado['Taxa Fixa R$'] == 6.65, "Taxa fixa esperada: R$ 6,65"
    print("✓ PASSOU")
    
    # Teste 2: Produto com logística Flex, preço abaixo de R$ 79
    resultado = calculator.calcular_linha(
        sku="MLB987654321",
        descricao="Produto Teste 2",
        custo_produto=20.00,
        frete=5.00,
        preco_atual=45.00,
        marketplace="Mercado Livre",
        regime_tributario="Lucro Real",
        tipo_anuncio="Clássico",
        peso_kg=0.4,
        tipo_logistica_ml="Flex",
        categoria_ml="Produtos Comuns"
    )
    
    print(f"\nTeste 2: Produto com Logística Flex, Preço R$ 45,00")
    print(f"Taxa Fixa: R$ {resultado['Taxa Fixa R$']:.2f}")
    print(f"Faixa: {resultado['Faixa Taxa Fixa']}")
    print(f"Lucro: R$ {resultado['Lucro R$']:.2f}")
    print(f"Margem: {resultado['Margem Bruta %']:.2f}%")
    print(f"Status: {resultado['Status']}")
    assert resultado['Taxa Fixa R$'] == 6.65, "Taxa fixa esperada: R$ 6,65"
    print("✓ PASSOU")
    
    # Teste 3: Produto com logística Full, preço acima de R$ 79
    resultado = calculator.calcular_linha(
        sku="MLB555555555",
        descricao="Produto Teste 3",
        custo_produto=40.00,
        frete=0.00,
        preco_atual=90.00,
        marketplace="Mercado Livre",
        regime_tributario="Lucro Real",
        tipo_anuncio="Clássico",
        peso_kg=0.4,
        tipo_logistica_ml="Full",
        categoria_ml="Produtos Comuns"
    )
    
    print(f"\nTeste 3: Produto com Logística Full, Preço R$ 90,00, Peso 400g (Frete Grátis)")
    print(f"Taxa Fixa: R$ {resultado['Taxa Fixa R$']:.2f}")
    print(f"Faixa: {resultado['Faixa Taxa Fixa']}")
    print(f"Lucro: R$ {resultado['Lucro R$']:.2f}")
    print(f"Margem: {resultado['Margem Bruta %']:.2f}%")
    print(f"Status: {resultado['Status']}")
    assert resultado['Taxa Fixa R$'] == 13.25, "Taxa fixa esperada: R$ 13,25"
    print("✓ PASSOU")


if __name__ == "__main__":
    try:
        testar_custo_operacional_full()
        testar_taxa_fixa_flex()
        testar_frete_gratis_full()
        testar_integracao_pricing_calculator()
        
        print("\n" + "=" * 80)
        print("✓ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 80)
        print("\nA nova lógica de custos do Mercado Livre foi implementada corretamente.")
        print("Válida a partir de 02 de março de 2026.")
        
    except AssertionError as e:
        print(f"\n✗ TESTE FALHOU: {e}")
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
