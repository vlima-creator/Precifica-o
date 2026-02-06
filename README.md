# 💰 Carblue Pricing & Promo Manager

Aplicativo Streamlit para precificação inteligente e gestão de promoções do Mercado Livre, integrado com toda a lógica da planilha de precificação V3.

## 🎯 Objetivo

Automatizar o processo de:
1. **Carregar relatórios de vendas** do Mercado Livre (30, 60 ou 180 dias)
2. **Classificar produtos** em Curva ABC baseado em faturamento
3. **Configurar regras de promoção** por curva
4. **Gerar relatório pronto** para upload no Mercado Livre

## 🚀 Como Usar

### 1. Instalação

```bash
# Clonar repositório
git clone <seu-repositorio>
cd carblue-streamlit

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Aplicativo

```bash
streamlit run app.py
```

O aplicativo abrirá em `http://localhost:8501`

### 3. Fluxo de Uso

#### **Passo 1: Configurar Marketplace e Impostos**
- Acesse o sidebar e ajuste as taxas de comissão dos marketplaces
- Configure os regimes tributários (IBS, CBS, Impostos)
- Defina suas margens alvo (Bruta e Líquida Mínima)

#### **Passo 2: Carregar Relatório**
- Vá para aba **"Carregar Relatório"**
- Importe seu arquivo Excel ou CSV do Mercado Livre
- O sistema valida e normaliza os dados automaticamente

#### **Passo 3: Análise ABC**
- Acesse aba **"Análise ABC"**
- Veja a classificação automática dos produtos:
  - **Curva A**: 80% do faturamento
  - **Curva B**: 15% do faturamento
  - **Curva C**: 5% do faturamento
- Visualize gráficos de distribuição

#### **Passo 4: Configurar Promoções**
- Vá para aba **"Promoções"**
- Defina o desconto desejado para cada curva:
  - Curva A: 0% (produtos campeões, sem desconto)
  - Curva B: 5% (estimular vendas)
  - Curva C: 10% (impulsionar produtos lentos)
- Veja o impacto das promoções em tempo real

#### **Passo 5: Gerar Relatório Final**
- Acesse aba **"Relatório Final"**
- Revise os dados com preços promocionais
- Baixe o arquivo Excel pronto para Mercado Livre

## 📊 Estrutura do Projeto

```
carblue-streamlit/
├── app.py                          # Aplicativo principal Streamlit
├── config.py                       # Configurações e constantes
├── pricing_calculator.py           # Cálculos de precificação
├── abc_classifier.py               # Classificação ABC
├── promotion_manager.py            # Gerenciamento de promoções
├── mercado_livre_processor.py      # Processamento de relatórios
├── session_manager.py              # Gerenciamento de estado
├── requirements.txt                # Dependências
├── test_app.py                     # Testes dos módulos
├── exemplo_relatorio.xlsx          # Arquivo de exemplo
└── README.md                       # Este arquivo
```

## 🔧 Módulos

### **config.py**
Define configurações padrão:
- Marketplaces (Mercado Livre, Shopee, Amazon, etc.)
- Regimes tributários (Simples Nacional, Lucro Presumido, Lucro Real, MEI)
- Limites de Curva ABC (80%, 95%, 100%)

### **pricing_calculator.py**
Realiza cálculos de:
- Custos variáveis (comissão, taxa fixa, impostos, ads)
- Margens bruta e líquida
- Preço sugerido para atingir margem alvo
- Desconto máximo permitido
- Avaliação de saúde da precificação

### **abc_classifier.py**
Classifica produtos em Curva ABC:
- Ordena por faturamento decrescente
- Calcula faturamento acumulado
- Classifica em A (80%), B (95%), C (100%)
- Gera resumo estatístico
- Identifica oportunidades (B/C com margem alta)

### **promotion_manager.py**
Gerencia promoções:
- Define regras de desconto por curva
- Calcula preço promocional
- Valida desconto seguro
- Gera relatório de impacto
- Exporta para Mercado Livre

### **mercado_livre_processor.py**
Processa relatórios:
- Detecta formato (Excel/CSV)
- Normaliza nomes de colunas
- Valida dados
- Agrega por SKU
- Exporta para Excel

### **session_manager.py**
Gerencia estado da sessão Streamlit:
- Inicializa variáveis de sessão
- Atualiza configurações
- Persiste dados entre interações

## 📋 Formato de Entrada

### Arquivo do Mercado Livre
Deve conter as seguintes colunas (nomes podem variar):
- **SKU** ou ID do produto
- **Título** ou Descrição
- **Preço** ou Preço de Venda
- **Quantidade Vendida** ou Vendas
- **Faturamento** (opcional, calculado automaticamente)

### Exemplo:
| SKU | Título | Preço | Quantidade Vendida |
|-----|--------|-------|-------------------|
| MLB123456789 | Produto A | 150.00 | 50 |
| MLB987654321 | Produto B | 200.00 | 30 |

## 📤 Formato de Saída

O relatório final contém:
- **SKU/MLB**: Código do produto
- **Título**: Nome do produto
- **Preço Atual**: Preço original
- **Preço Promoção**: Preço com desconto
- **Desconto %**: Percentual de desconto
- **Curva**: Classificação ABC

Pronto para upload direto no Mercado Livre!

## 🧪 Testes

Para testar os módulos:

```bash
python3 test_app.py
```

Isso executará testes de:
- Processamento de relatórios
- Classificação ABC
- Gerenciamento de promoções
- Cálculos de precificação

## 📊 Exemplo de Uso

1. **Arquivo de entrada**: `exemplo_relatorio.xlsx`
2. **Configurações padrão**:
   - Marketplace: Mercado Livre Premium (19% comissão)
   - Regime: Lucro Real
   - Margem Bruta Alvo: 30%
   - Margem Líquida Mínima: 10%

3. **Regras de Promoção**:
   - Curva A: 0% (sem desconto)
   - Curva B: 5% (estimular)
   - Curva C: 10% (impulsionar)

4. **Resultado**: Arquivo Excel com 30 produtos classificados e com preços promocionais

## 🔐 Segurança

- Nenhum dado é enviado para servidores externos
- Tudo funciona localmente
- Dados são processados apenas durante a sessão

## 🐛 Troubleshooting

### Erro: "Coluna obrigatória não encontrada"
- Certifique-se que o arquivo tem colunas: SKU, Preço, Quantidade Vendida
- Nomes de colunas podem variar (o sistema tenta normalizar)

### Erro: "Relatório deve ter pelo menos 5 produtos"
- Importe um arquivo com mais de 5 produtos

### Erro: "Faturamento total deve ser maior que zero"
- Verifique se os preços e quantidades estão preenchidos corretamente

## 📝 Notas

- A classificação ABC é dinâmica baseada no faturamento real
- Descontos são validados contra o desconto máximo permitido
- Margens são calculadas considerando todos os custos
- Relatórios podem ser regenerados quantas vezes quiser

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!

## 📄 Licença

MIT License

## 📞 Suporte

Para dúvidas ou problemas, entre em contato com o time Carblue.

---

**Desenvolvido com ❤️ para sua precificação inteligente**
