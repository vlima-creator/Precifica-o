# 🚀 Guia de Deployment no Streamlit Cloud

## O Que é Streamlit Cloud?

Streamlit Cloud é a plataforma oficial para hospedar aplicativos Streamlit gratuitamente. Seu app fica disponível em uma URL pública e é atualizado automaticamente quando você faz push no GitHub.

## Pré-requisitos

- ✅ Conta GitHub (já configurada)
- ✅ Repositório no GitHub (`vlima-creator/Precifica-o`)
- ✅ Arquivo `requirements.txt` com dependências
- ✅ Arquivo `app.py` como entrada principal

## Passo a Passo

### 1️⃣ Acessar Streamlit Cloud

1. Abra: https://share.streamlit.io/
2. Faça login com sua conta GitHub
3. Autorize o Streamlit Cloud a acessar seus repositórios

### 2️⃣ Criar Novo App

1. Clique no botão **"New app"** (canto superior direito)
2. Você será redirecionado para criar um novo app

### 3️⃣ Configurar o Deploy

Preencha os campos:

**Repository (Repositório):**
```
vlima-creator/Precifica-o
```

**Branch (Ramo):**
```
main
```

**Main file path (Arquivo Principal):**
```
app.py
```

### 4️⃣ Iniciar o Deploy

1. Clique em **"Deploy"**
2. Aguarde o Streamlit Cloud:
   - ✅ Clonar o repositório
   - ✅ Instalar dependências
   - ✅ Iniciar o aplicativo
   - ✅ Gerar URL pública

### 5️⃣ Acessar Seu App

Após o deploy, você receberá uma URL como:
```
https://seu-app-name.streamlit.app
```

## Atualizações Automáticas

Sempre que você fizer push no GitHub:

```bash
git add .
git commit -m "sua mensagem"
git push origin main
```

O Streamlit Cloud detectará automaticamente as mudanças e fará o redeploy em poucos minutos!

## Estrutura Esperada

```
vlima-creator/Precifica-o/
├── app.py                    ← Arquivo principal
├── config.py                 ← Configurações
├── pricing_calculator.py     ← Módulo de cálculos
├── abc_classifier.py         ← Módulo de classificação
├── promotion_manager.py      ← Módulo de promoções
├── mercado_livre_processor.py ← Módulo de processamento
├── session_manager.py        ← Módulo de estado
├── requirements.txt          ← Dependências
├── .streamlit/
│   └── config.toml          ← Configuração do Streamlit
├── README.md                 ← Documentação
└── exemplo_relatorio.xlsx    ← Arquivo de exemplo
```

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named..."

**Solução:** Verifique se todas as dependências estão em `requirements.txt`

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push origin main
```

### ❌ "FileNotFoundError: exemplo_relatorio.xlsx"

**Solução:** Certifique-se que o arquivo está no repositório

```bash
git add exemplo_relatorio.xlsx
git commit -m "Add example file"
git push origin main
```

### ❌ App carrega lentamente

**Solução:** Otimize o código ou use `@st.cache_data` para cache

```python
@st.cache_data
def carregar_dados():
    return pd.read_excel("exemplo_relatorio.xlsx")
```

### ❌ Erro ao fazer upload de arquivo

**Solução:** Aumente o limite de upload em `.streamlit/config.toml`

```toml
[server]
maxUploadSize = 200  # em MB
```

## Monitoramento

### Acessar Logs

1. Vá para https://share.streamlit.io/
2. Clique no seu app
3. Clique em **"Manage app"**
4. Vá para **"Logs"** para ver erros

### Métricas

No painel de controle você pode ver:
- Número de usuários ativos
- Tempo de resposta
- Uso de memória
- Status do app

## Segurança

### Variáveis de Ambiente

Para dados sensíveis (API keys, senhas), use secrets:

1. Vá para **"Manage app"** → **"Secrets"**
2. Adicione suas variáveis:

```toml
[secrets]
MINHA_API_KEY = "sua-chave-aqui"
```

3. Acesse no código:

```python
import streamlit as st
api_key = st.secrets["MINHA_API_KEY"]
```

## Limites de Recursos

**Plano Gratuito:**
- ✅ Aplicativos ilimitados
- ✅ 1 GB de memória
- ✅ Tempo de inatividade: 15 minutos
- ✅ Reinicialização automática

**Plano Pro (Opcional):**
- ✅ Mais memória
- ✅ Sem tempo de inatividade
- ✅ Suporte prioritário

## Dicas de Performance

### 1. Use Cache

```python
@st.cache_data
def processar_dados(arquivo):
    return pd.read_excel(arquivo)
```

### 2. Limite o Tamanho de Dados

```python
df = df.head(1000)  # Limitar a 1000 linhas
```

### 3. Otimize Gráficos

```python
# Usar Plotly em vez de Matplotlib
import plotly.express as px
fig = px.pie(...)
st.plotly_chart(fig, use_container_width=True)
```

### 4. Lazy Loading

```python
if st.button("Carregar dados"):
    dados = processar_dados()
    st.write(dados)
```

## Próximas Etapas

1. ✅ Deploy no Streamlit Cloud
2. ✅ Testar com dados reais
3. ✅ Coletar feedback
4. ✅ Fazer melhorias
5. ✅ Escalar para produção

## Links Úteis

- **Streamlit Cloud:** https://share.streamlit.io/
- **Documentação:** https://docs.streamlit.io/
- **Community:** https://discuss.streamlit.io/
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues

## Suporte

Para problemas com o Streamlit Cloud:
- Documentação: https://docs.streamlit.io/streamlit-cloud/get-started
- Community: https://discuss.streamlit.io/
- Email: support@streamlit.io

---

**Seu aplicativo estará online em poucos minutos!** 🎉
