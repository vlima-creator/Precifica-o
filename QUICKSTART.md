# 🚀 Guia de Início Rápido

## 5 Minutos para Começar

### 1️⃣ Instalar e Executar

```bash
# Entrar no diretório
cd carblue-streamlit

# Instalar dependências
pip install -r requirements.txt

# Executar aplicativo
streamlit run app.py
```

O app abrirá em: **http://localhost:8501**

### 2️⃣ Usar o Arquivo de Exemplo

1. Vá para aba **"Carregar Relatório"**
2. Clique em **"Browse files"**
3. Selecione **`exemplo_relatorio.xlsx`**
4. Clique em **"Análise ABC"**

### 3️⃣ Configurar Promoções

1. Vá para aba **"Promoções"**
2. Defina descontos:
   - Curva A: **0%** (produtos campeões)
   - Curva B: **5%** (estimular)
   - Curva C: **10%** (impulsionar)
3. Veja o impacto em tempo real

### 4️⃣ Gerar Relatório

1. Vá para aba **"Relatório Final"**
2. Clique em **"📥 Baixar Relatório (Excel)"**
3. Importe no Mercado Livre!

## 📊 O Que Você Vai Ver

### Análise ABC
- **Curva A**: 80% do faturamento (9 produtos)
- **Curva B**: 15% do faturamento (5 produtos)
- **Curva C**: 5% do faturamento (6 produtos)

### Impacto de Promoções
- **Total de Economia**: R$ 122,11
- **Economia Média**: R$ 6,11 por produto
- **Produtos com Promoção**: 11

### Relatório Final
Arquivo Excel com:
- SKU/MLB
- Título
- Preço Atual
- Preço Promoção
- Desconto %
- Curva ABC

## 🎯 Próximos Passos

1. **Carregar seu relatório real** do Mercado Livre
2. **Ajustar configurações** de marketplace e impostos
3. **Definir regras de promoção** conforme sua estratégia
4. **Gerar e aplicar** no Mercado Livre

## ⚙️ Configurações Importantes

### Sidebar - Marketplaces
Ajuste as taxas de comissão dos seus marketplaces:
- Mercado Livre Premium: 19%
- Shopee: 20%
- Amazon: 15%

### Sidebar - Regimes Tributários
Configure seu regime fiscal:
- Simples Nacional
- Lucro Presumido
- Lucro Real
- MEI

### Sidebar - Margens Alvo
Defina suas margens:
- Margem Bruta Alvo: 30%
- Margem Líquida Mínima: 10%

## 💡 Dicas

✅ **Sempre comece com a Curva A** (0% desconto) para proteger seus produtos campeões

✅ **Use Curva B** (5-10%) para estimular produtos com bom potencial

✅ **Curva C** (10-20%) para impulsionar produtos lentos

✅ **Teste com o arquivo de exemplo** antes de usar dados reais

✅ **Baixe o relatório** e revise antes de aplicar no Mercado Livre

## 🆘 Problemas Comuns

### "Coluna obrigatória não encontrada"
- Seu arquivo precisa ter: SKU, Preço, Quantidade Vendida
- Nomes podem variar (o sistema tenta normalizar)

### "Relatório deve ter pelo menos 5 produtos"
- Importe um arquivo com mais de 5 produtos

### Aplicativo não abre
- Verifique: `streamlit run app.py`
- Acesse: http://localhost:8501

## 📞 Suporte

Dúvidas? Consulte o **README.md** para documentação completa!

---

**Pronto para começar? Execute: `streamlit run app.py`** 🚀
