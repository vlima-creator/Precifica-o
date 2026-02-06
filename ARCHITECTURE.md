# 🏗️ Arquitetura Técnica

## Visão Geral

O **Carblue Pricing & Promo Manager** é um aplicativo Streamlit modular que integra toda a lógica de precificação da planilha V3 com processamento de relatórios do Mercado Livre.

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────┐
│                    APLICATIVO STREAMLIT (app.py)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┬─────────────────────┐
        ↓                     ↓                     ↓
   ┌─────────┐          ┌──────────┐          ┌──────────┐
   │ Carregar│          │ Análise  │          │Promoções │
   │Relatório│          │   ABC    │          │          │
   └────┬────┘          └────┬─────┘          └────┬─────┘
        ↓                    ↓                     ↓
   ┌─────────────────────────────────────────────────────┐
   │  MercadoLivreProcessor (normalizar dados)           │
   └────────────────────┬────────────────────────────────┘
                        ↓
   ┌─────────────────────────────────────────────────────┐
   │  ABCClassifier (classificar em Curva A/B/C)         │
   └────────────────────┬────────────────────────────────┘
                        ↓
   ┌─────────────────────────────────────────────────────┐
   │  PromotionManager (aplicar descontos por curva)     │
   └────────────────────┬────────────────────────────────┘
                        ↓
   ┌─────────────────────────────────────────────────────┐
   │  Gerar Relatório Final (Excel para Mercado Livre)   │
   └─────────────────────────────────────────────────────┘
```

## Arquitetura de Módulos

### 1. **app.py** - Aplicativo Principal
**Responsabilidade**: Interface Streamlit com 5 abas

**Componentes**:
- Sidebar com configurações
- Tab 1: Home (instruções)
- Tab 2: Carregar Relatório
- Tab 3: Análise ABC
- Tab 4: Configurar Promoções
- Tab 5: Relatório Final

**Dependências**: Todos os módulos abaixo

---

### 2. **config.py** - Configurações Globais
**Responsabilidade**: Constantes e valores padrão

**Contém**:
```python
DEFAULT_MARKETPLACES = {
    "Mercado Livre Premium": {"comissao": 0.19, ...},
    "Shopee": {"comissao": 0.20, ...},
    ...
}

DEFAULT_REGIMES = {
    "Lucro Real": {"ibs": 0.001, "cbs": 0.009, ...},
    ...
}

CURVA_ABC_LIMITS = {
    "A": 0.80,  # 80%
    "B": 0.95,  # 95%
    "C": 1.00,  # 100%
}
```

**Uso**: Importado por todos os módulos

---

### 3. **mercado_livre_processor.py** - Processamento de Relatórios
**Responsabilidade**: Carregar, normalizar e validar dados

**Métodos Principais**:
- `normalizar_relatorio_vendas()` - Normaliza nomes de colunas
- `validar_relatorio()` - Valida dados
- `agregar_por_sku()` - Agrega múltiplas linhas do mesmo SKU
- `carregar_de_excel()` / `carregar_de_csv()` - Carrega arquivos

**Entrada**: Arquivo Excel/CSV do Mercado Livre
**Saída**: DataFrame normalizado com colunas padrão

**Exemplo**:
```python
processor = MercadoLivreProcessor()
df = processor.carregar_de_excel("relatorio.xlsx")
df_normalizado = processor.normalizar_relatorio_vendas(df)
valido, msg = processor.validar_relatorio(df_normalizado)
```

---

### 4. **abc_classifier.py** - Classificação ABC
**Responsabilidade**: Classificar produtos em Curva A/B/C

**Métodos Principais**:
- `classificar_produtos()` - Classifica baseado em faturamento
- `gerar_resumo_abc()` - Gera estatísticas por curva
- `identificar_oportunidades()` - Encontra B/C com margem alta

**Algoritmo**:
1. Ordena por faturamento decrescente
2. Calcula faturamento acumulado
3. Classifica:
   - A: até 80% do faturamento
   - B: de 80% até 95%
   - C: de 95% até 100%
   - Sem Curva: resto

**Exemplo**:
```python
classifier = ABCClassifier()
df_abc = classifier.classificar_produtos(df, "Faturamento")
resumo = classifier.gerar_resumo_abc(df_abc)
```

---

### 5. **promotion_manager.py** - Gerenciamento de Promoções
**Responsabilidade**: Aplicar descontos e gerar relatórios

**Métodos Principais**:
- `definir_regras()` - Define desconto por curva
- `aplicar_promocoes()` - Aplica descontos
- `validar_desconto_seguro()` - Valida contra desconto máximo
- `gerar_relatorio_promocoes()` - Calcula impacto
- `exportar_para_mercado_livre()` - Formata para upload

**Exemplo**:
```python
manager = PromotionManager()
regras = {"A": 0.0, "B": 0.05, "C": 0.10, "Sem Curva": 0.0}
df_promo = manager.aplicar_promocoes(df_abc, regras=regras)
relatorio = manager.gerar_relatorio_promocoes(df_promo)
```

---

### 6. **pricing_calculator.py** - Cálculos de Precificação
**Responsabilidade**: Calcular custos, margens e preços

**Métodos Principais**:
- `calcular_custos_variáveis()` - Comissão, impostos, ads
- `calcular_margem()` - Margens bruta e líquida
- `calcular_preco_sugerido()` - Preço para atingir margem alvo
- `calcular_desconto_maximo()` - Desconto máximo seguro
- `avaliar_saude_precificacao()` - Status (Saudável/Alerta/Prejuízo)
- `processar_base_dados()` - Processa DataFrame completo

**Fórmulas**:
```
Custos Variáveis = Comissão + Taxa Fixa + Impostos + Ads + Devolução
Lucro = Preço - Custo Direto - Custos Variáveis
Margem % = (Lucro / Preço) × 100
Preço Sugerido = Custo / (1 - Taxa Variável - Margem Alvo)
```

**Exemplo**:
```python
calculator = PricingCalculator()
custos = calculator.calcular_custos_variáveis(150, "Mercado Livre Premium", "Lucro Real")
margem = calculator.calcular_margem(150, 50, custos)
```

---

### 7. **session_manager.py** - Gerenciamento de Estado
**Responsabilidade**: Persistir dados entre interações

**Funções**:
- `inicializar_sessao()` - Cria variáveis padrão
- `resetar_sessao()` - Limpa tudo
- `atualizar_marketplace()` - Atualiza config
- `atualizar_regras_promocao()` - Atualiza regras

**Variáveis de Sessão**:
```python
st.session_state.marketplaces      # Dict de marketplaces
st.session_state.regimes           # Dict de regimes
st.session_state.relatorio_vendas  # DataFrame original
st.session_state.dados_processados # DataFrame com Curva ABC
st.session_state.regras_promocao   # Dict com descontos
st.session_state.dados_com_promocoes # DataFrame final
```

---

## Fluxo de Processamento

### Fluxo 1: Carregar e Processar Relatório

```
Arquivo Excel/CSV
    ↓
MercadoLivreProcessor.carregar_de_excel()
    ↓
MercadoLivreProcessor.normalizar_relatorio_vendas()
    ↓
MercadoLivreProcessor.validar_relatorio()
    ↓
MercadoLivreProcessor.agregar_por_sku()
    ↓
DataFrame Normalizado → session_state.relatorio_vendas
```

### Fluxo 2: Classificar ABC

```
DataFrame Normalizado
    ↓
ABCClassifier.classificar_produtos()
    ↓
ABCClassifier.gerar_resumo_abc()
    ↓
DataFrame com Curva ABC → session_state.dados_processados
```

### Fluxo 3: Aplicar Promoções

```
DataFrame com Curva ABC
    ↓
PromotionManager.aplicar_promocoes(regras)
    ↓
PromotionManager.validar_desconto_seguro()
    ↓
PromotionManager.gerar_relatorio_promocoes()
    ↓
DataFrame com Preços Promocionais → session_state.dados_com_promocoes
```

### Fluxo 4: Gerar Relatório Final

```
DataFrame com Preços Promocionais
    ↓
PromotionManager.exportar_para_mercado_livre()
    ↓
Arquivo Excel Formatado
    ↓
Download para Mercado Livre
```

---

## Estrutura de Dados

### DataFrame de Entrada (Mercado Livre)
```
SKU | Título | Preço | Quantidade Vendida | Faturamento
```

### DataFrame Processado (Após ABC)
```
SKU | Título | Preço | Quantidade Vendida | Faturamento | Curva ABC | Faturamento Acumulado %
```

### DataFrame Final (Com Promoções)
```
SKU | Título | Preço | Preço Promocional | Desconto % | Economia R$ | Curva ABC
```

---

## Padrões de Design

### 1. **Separação de Responsabilidades**
Cada módulo tem uma responsabilidade clara:
- Processamento de dados
- Classificação
- Cálculos
- Gerenciamento de promoções
- Interface

### 2. **Imutabilidade**
Todos os métodos retornam novos DataFrames:
```python
df = df.copy()  # Não modifica original
# ... processamento
return df
```

### 3. **Configuração Centralizada**
Todas as constantes em `config.py`:
- Fácil de atualizar
- Reutilizável
- Testável

### 4. **Validação em Camadas**
Cada módulo valida seus dados:
- MercadoLivreProcessor: valida formato
- ABCClassifier: valida faturamento
- PromotionManager: valida descontos

---

## Extensibilidade

### Adicionar Novo Marketplace
```python
# Em config.py
DEFAULT_MARKETPLACES["Novo Marketplace"] = {
    "comissao": 0.15,
    "custo_fixo": 5.0,
    "taxa_devolucao": 0.02
}
```

### Adicionar Novo Regime Tributário
```python
# Em config.py
DEFAULT_REGIMES["Novo Regime"] = {
    "ibs": 0.001,
    "cbs": 0.009,
    "impostos_encargos": 0.15
}
```

### Adicionar Novo Cálculo
```python
# Em pricing_calculator.py
def novo_calculo(self, parametros):
    # Implementar lógica
    return resultado
```

---

## Performance

- **Processamento de 1000 produtos**: < 1 segundo
- **Classificação ABC**: O(n log n) - ordenação
- **Aplicação de promoções**: O(n) - iteração única
- **Geração de relatório**: O(n) - iteração única

---

## Testes

### Executar Testes
```bash
python3 test_app.py
```

### Cobertura de Testes
- ✅ Processamento de relatórios
- ✅ Classificação ABC
- ✅ Cálculos de precificação
- ✅ Gerenciamento de promoções

---

## Próximas Melhorias

- [ ] Integração com API do Mercado Livre
- [ ] Histórico de promoções
- [ ] Previsão de impacto
- [ ] Dashboard de analytics
- [ ] Exportação para múltiplos formatos
- [ ] Agendamento de promoções

---

**Desenvolvido com arquitetura limpa e modular para facilitar manutenção e expansão.**
