# Mapa de Mudanças: Novas Regras de Custo do Mercado Livre

Este documento detalha as alterações necessárias no código para adaptar o aplicativo às novas regras de custo do Mercado Livre, que entram em vigor em 2 de março de 2026.

## 1. Análise da Mudança Principal

A alteração mais significativa é a **substituição da "Taxa Fixa" por um "Custo Operacional"** para produtos abaixo de R$ 79,00 enviados via logística do Mercado Livre (Full, Coleta, Agências). Este novo custo não é mais um valor fixo por faixa de preço, mas sim uma matriz complexa que cruza **faixa de preço** com **peso do produto**.

- **Lógica Antiga (até 01/03/2026):** Uma taxa fixa era aplicada com base em 3 faixas de preço (ex: R$ 6,25 para produtos até R$ 29).
- **Lógica Nova (a partir de 02/03/2026):** Um custo operacional é determinado por uma tabela de dupla entrada (preço x peso). Por exemplo, um produto de 400g vendido a R$ 45 terá um custo diferente de um produto de 800g vendido ao mesmo preço.

Para envios com logística própria (Flex, etc.), a "Taxa Fixa" foi mantida, mas os valores e as faixas de preço foram atualizados.

## 2. Módulos a Serem Modificados

### `config.py`

Este arquivo é o ponto central para armazenar as novas tabelas de custos. As seguintes ações são necessárias:

1.  **Renomear `MERCADO_LIVRE_TAXA_FIXA`**: A estrutura atual não comporta a nova lógica de peso. Ela deve ser substituída ou complementada.
2.  **Criar `MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO`**: Uma nova estrutura de dados (provavelmente um dicionário de listas de dicionários) deve ser criada para armazenar a matriz de Preço x Peso para a logística do ML.
    - A estrutura deve ser pensada para facilitar a consulta no `pricing_calculator_v2.py`.
    - Exemplo de estrutura:
      ```python
      MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO = {
          "Produtos Comuns": [
              {"peso_max_kg": 0.3, "custos_por_faixa": [{"preco_max": 18.99, "custo": 5.65}, ... ]},
              {"peso_max_kg": 0.5, "custos_por_faixa": [{"preco_max": 18.99, "custo": 5.95}, ... ]},
              # ... demais faixas de peso
          ],
          "Livros": [
              # ... estrutura similar para livros
          ]
      }
      ```
3.  **Atualizar `MERCADO_LIVRE_TAXA_FIXA_FLEX`**: Criar uma nova variável para armazenar as taxas fixas atualizadas para envios Flex e de logística própria.
    - Exemplo:
      ```python
      MERCADO_LIVRE_TAXA_FIXA_FLEX = {
          "Produtos Comuns": [
              {"min": 0.0, "max": 18.99, "taxa_fixa": 6.25},
              # ... demais faixas
          ],
          "Livros": [
              # ... faixas para livros
          ]
      }
      ```
4.  **Adicionar Tabela de Frete Grátis**: A tabela de custos para produtos acima de R$ 79 também mudou e depende do peso. Ela deve ser adicionada ao `config.py` de forma similar à do custo operacional.

### `pricing_calculator_v2.py`

Este é o módulo que contém a lógica de cálculo e precisará das modificações mais substanciais.

1.  **Novo Input para o Usuário**: A calculadora agora depende do **peso do produto**. Será necessário adicionar um campo de entrada de "Peso (kg)" na interface do Streamlit (`app.py`) e passá-lo para as funções de cálculo.
2.  **Modificar `calcular_taxa_fixa_mercado_livre`**: O nome desta função se tornou inadequado. Ela deve ser refatorada ou substituída por uma nova função, como `calcular_custo_operacional_ml`.
3.  **Implementar a Nova Lógica de Cálculo**:
    - A nova função deverá receber `preco_venda`, `categoria` e o novo parâmetro `peso_kg`.
    - Ela precisará de um seletor de logística (Logística ML vs. Flex/Própria) para decidir qual tabela de custo usar (`MERCADO_LIVRE_CUSTO_OPERACIONAL_PESO` ou `MERCADO_LIVRE_TAXA_FIXA_FLEX`).
    - A função irá iterar sobre a estrutura de dados definida no `config.py` para encontrar a faixa de peso correspondente e, dentro dela, a faixa de preço para retornar o custo correto.
4.  **Ajustar `calcular_linha`**: A função principal que calcula todos os custos de uma linha de produto deve ser atualizada para:
    - Aceitar os novos parâmetros (`peso_kg`, `tipo_logistica`).
    - Chamar a nova função `calcular_custo_operacional_ml` em vez da antiga.
    - Substituir o valor da "Taxa Fixa" pelo novo "Custo Operacional" no cálculo do lucro.

### `app.py`

As mudanças na interface do usuário são cruciais para que a nova lógica funcione.

1.  **Adicionar Campo de Entrada de Peso**: No formulário ou na tabela onde o usuário insere os dados do produto, um novo campo numérico para "Peso (kg)" deve ser adicionado.
2.  **Adicionar Seletor de Logística**: Um `st.selectbox` ou `st.radio` deve ser adicionado para que o usuário possa escolher o tipo de logística para o cálculo:
    - Opção 1: "Logística Mercado Livre (Full, Coleta, Agências)"
    - Opção 2: "Minha Logística (Flex, Retirada, etc.)"
3.  **Passar Novos Dados**: Os valores de `peso_kg` e `tipo_logistica` selecionados pelo usuário devem ser capturados e passados como argumentos para as funções de cálculo no backend (`PricingCalculatorV2`).

## 3. Plano de Ação

1.  **Fase 1: `config.py`** - Atualizar o arquivo de configuração com todas as novas tabelas de custos (Custo Operacional por Peso, Taxa Fixa Flex, Frete Grátis por Peso).
2.  **Fase 2: `app.py`** - Modificar a interface do Streamlit para incluir os campos de entrada de peso e seletor de logística.
3.  **Fase 3: `pricing_calculator_v2.py`** - Refatorar a lógica de cálculo para incorporar as novas variáveis e tabelas, garantindo que o custo correto seja aplicado com base no preço, peso, categoria e tipo de logística.
4.  **Fase 4: Testes** - Criar casos de teste específicos no `test_app.py` (ou um arquivo de teste temporário) para validar a nova lógica com diferentes combinações de peso, preço e logística, comparando os resultados com os valores esperados das tabelas do Mercado Livre.
