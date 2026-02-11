"""
Testes para validar a nova lógica de custos do Mercado Livre 2026
"""

import sys
sys.path.insert(0, '/home/ubuntu/Precifica-o')

from mercado_livre_costs import MercadoLivreCostsCalculator as MLCalc


def teste_comissao_categoria():
    """Testa o cálculo de comissão por categoria"""
    print("\n" + "="*60)
    print("TESTE 1: Comissão por Categoria")
    print("="*60)
    
    # Teste Acessórios para Veículos
    comissao_classico = MLCalc.calcular_comissao_categoria("Acessórios para Veículos", "Clássico")
    comissao_premium = MLCalc.calcular_comissao_categoria("Acessórios para Veículos", "Premium")
    
    print(f"Acessórios para Veículos - Clássico: {comissao_classico*100:.1f}% (esperado: 12%)")
    print(f"Acessórios para Veículos - Premium: {comissao_premium*100:.1f}% (esperado: 17%)")
    
    # Teste Livros
    comissao_livros_classico = MLCalc.calcular_comissao_categoria("Livros", "Clássico")
    comissao_livros_premium = MLCalc.calcular_comissao_categoria("Livros", "Premium")
    
    print(f"Livros - Clássico: {comissao_livros_classico*100:.1f}% (esperado: 6.5%)")
    print(f"Livros - Premium: {comissao_livros_premium*100:.1f}% (esperado: 11.5%)")
    
    assert comissao_classico == 0.12, "Comissão Acessórios Clássico incorreta"
    assert comissao_premium == 0.17, "Comissão Acessórios Premium incorreta"
    assert comissao_livros_classico == 0.065, "Comissão Livros Clássico incorreta"
    
    print("✓ Teste de comissão passou!")


def teste_custo_operacional_full():
    """Testa o cálculo de custo operacional para logística Full"""
    print("\n" + "="*60)
    print("TESTE 2: Custo Operacional - Logística Full")
    print("="*60)
    
    # Produto leve (até 0,3kg) com preço R$ 45
    custo_1 = MLCalc.calcular_custo_operacional_full(45.0, 0.25, "Geral")
    print(f"Produto 0,25kg, R$ 45: R$ {custo_1:.2f} (esperado: R$ 6.55)")
    assert custo_1 == 6.55, f"Custo incorreto: {custo_1}"
    
    # Produto médio (0,55kg) com preço R$ 60 (faixa 0,5 a 1kg)
    custo_2 = MLCalc.calcular_custo_operacional_full(60.0, 0.55, "Geral")
    print(f"Produto 0,55kg, R$ 60: R$ {custo_2:.2f} (esperado: R$ 7.95)")
    assert custo_2 == 7.95, f"Custo incorreto: {custo_2}"
    
    # Produto com preço acima de R$ 79 (deve retornar 0)
    custo_3 = MLCalc.calcular_custo_operacional_full(85.0, 0.3, "Geral")
    print(f"Produto 0,3kg, R$ 85: R$ {custo_3:.2f} (esperado: R$ 0.00 - acima do limite)")
    assert custo_3 == 0.0, f"Custo deveria ser 0 para preço > 79: {custo_3}"
    
    # Livro com preço R$ 30
    custo_4 = MLCalc.calcular_custo_operacional_full(30.0, 0.3, "Livros")
    print(f"Livro 0,3kg, R$ 30: R$ {custo_4:.2f} (esperado: R$ 3.28)")
    assert custo_4 == 3.28, f"Custo livro incorreto: {custo_4}"
    
    # Supermercado com preço R$ 25
    custo_5 = MLCalc.calcular_custo_operacional_full(25.0, 0.3, "Supermercado")
    print(f"Supermercado 0,3kg, R$ 25: R$ {custo_5:.2f} (esperado: R$ 1.50)")
    assert custo_5 == 1.50, f"Custo supermercado incorreto: {custo_5}"
    
    print("✓ Teste de custo operacional passou!")


def teste_taxa_fixa_flex():
    """Testa o cálculo de taxa fixa para logística Flex"""
    print("\n" + "="*60)
    print("TESTE 3: Taxa Fixa - Logística Flex")
    print("="*60)
    
    # Produto com preço R$ 25 (Geral)
    taxa_1 = MLCalc.calcular_taxa_fixa_flex(25.0, "Geral")
    print(f"Produto R$ 25 (Geral): R$ {taxa_1:.2f} (esperado: R$ 6.65)")
    assert taxa_1 == 6.65, f"Taxa incorreta: {taxa_1}"
    
    # Livro com preço R$ 35
    taxa_2 = MLCalc.calcular_taxa_fixa_flex(35.0, "Livros")
    print(f"Livro R$ 35: R$ {taxa_2:.2f} (esperado: R$ 3.50)")
    assert taxa_2 == 3.50, f"Taxa livro incorreta: {taxa_2}"
    
    # Produto com preço acima de R$ 79 (isento)
    taxa_3 = MLCalc.calcular_taxa_fixa_flex(85.0, "Geral")
    print(f"Produto R$ 85: R$ {taxa_3:.2f} (esperado: R$ 0.00 - isento)")
    assert taxa_3 == 0.0, f"Taxa deveria ser 0 para preço > 79: {taxa_3}"
    
    print("✓ Teste de taxa fixa passou!")


def teste_frete_gratis_full():
    """Testa o cálculo de frete para produtos acima de R$ 79"""
    print("\n" + "="*60)
    print("TESTE 4: Frete Grátis - Logística Full (Preço > R$ 79)")
    print("="*60)
    
    # Produto 250g, R$ 85
    frete_1 = MLCalc.calcular_frete_gratis_full(85.0, 0.25)
    print(f"Produto 250g, R$ 85: R$ {frete_1:.2f} (esperado: R$ 11.97)")
    assert frete_1 == 11.97, f"Frete incorreto: {frete_1}"
    
    # Produto 400g, R$ 150
    frete_2 = MLCalc.calcular_frete_gratis_full(150.0, 0.4)
    print(f"Produto 400g, R$ 150: R$ {frete_2:.2f} (esperado: R$ 19.85)")
    assert frete_2 == 19.85, f"Frete incorreto: {frete_2}"
    
    # Produto 1,5kg, R$ 250 (faixa 1kg a 2kg)
    frete_3 = MLCalc.calcular_frete_gratis_full(250.0, 1.5)
    print(f"Produto 1,5kg, R$ 250: R$ {frete_3:.2f} (esperado: R$ 23.45)")
    assert frete_3 == 23.45, f"Frete incorreto: {frete_3}"
    
    print("✓ Teste de frete passou!")


def teste_custo_total_ml():
    """Testa o cálculo completo de custo do Mercado Livre"""
    print("\n" + "="*60)
    print("TESTE 5: Custo Total - Mercado Livre")
    print("="*60)
    
    # Cenário 1: Produto Full, preço R$ 50, 300g, Clássico
    resultado_1 = MLCalc.calcular_custo_total_ml(50.0, 0.3, "Full", "Geral", "Clássico")
    print(f"\nCenário 1: Produto Full, R$ 50, 300g, Clássico")
    print(f"  Comissão (14%): R$ {resultado_1['comissao']:.2f}")
    print(f"  Custo Operacional: R$ {resultado_1['custo_operacional']:.2f}")
    print(f"  Custo Total: R$ {resultado_1['custo_total']:.2f}")
    
    # Cenário 2: Produto Flex, preço R$ 35, Livro
    resultado_2 = MLCalc.calcular_custo_total_ml(35.0, 0.3, "Flex", "Livros", "Clássico")
    print(f"\nCenário 2: Produto Flex, R$ 35, Livro")
    print(f"  Comissão (6.5%): R$ {resultado_2['comissao']:.2f}")
    print(f"  Taxa Fixa: R$ {resultado_2['custo_operacional']:.2f}")
    print(f"  Custo Total: R$ {resultado_2['custo_total']:.2f}")
    
    # Cenário 3: Produto Full, preço R$ 120, 500g, Premium
    resultado_3 = MLCalc.calcular_custo_total_ml(120.0, 0.5, "Full", "Geral", "Premium")
    print(f"\nCenário 3: Produto Full, R$ 120, 500g, Premium (Frete)")
    print(f"  Comissão (19%): R$ {resultado_3['comissao']:.2f}")
    print(f"  Frete: R$ {resultado_3['frete']:.2f}")
    print(f"  Custo Total: R$ {resultado_3['custo_total']:.2f}")
    
    print("\n✓ Teste de custo total passou!")


def teste_limites_preco_baixo():
    """Testa as regras de limite para produtos de preço baixo"""
    print("\n" + "="*60)
    print("TESTE 6: Limites para Produtos de Preço Baixo")
    print("="*60)
    
    # Produto com preço R$ 10 (abaixo de R$ 12,50)
    # Custo não deve exceder 50% do valor
    custo_1 = MLCalc.calcular_custo_operacional_full(10.0, 0.3, "Geral")
    print(f"Produto R$ 10, 300g: R$ {custo_1:.2f} (máximo 50% = R$ 5.00)")
    assert custo_1 <= 5.0, f"Custo excedeu 50% do preço: {custo_1}"
    
    # Supermercado com preço R$ 20 (abaixo de R$ 29)
    # Custo não deve exceder 25% do valor
    custo_2 = MLCalc.calcular_custo_operacional_full(20.0, 0.3, "Supermercado")
    print(f"Supermercado R$ 20, 300g: R$ {custo_2:.2f} (máximo 25% = R$ 5.00)")
    assert custo_2 <= 5.0, f"Custo excedeu 25% do preço: {custo_2}"
    
    print("✓ Teste de limites passou!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTES DO MERCADO LIVRE 2026")
    print("="*60)
    
    try:
        teste_comissao_categoria()
        teste_custo_operacional_full()
        teste_taxa_fixa_flex()
        teste_frete_gratis_full()
        teste_custo_total_ml()
        teste_limites_preco_baixo()
        
        print("\n" + "="*60)
        print("✓ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ ERRO NO TESTE: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERRO INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
