# Catálogo de Dados — Pipeline Analítico de E-Commerce (Olist)

O presente Catálogo de Dados cumpre rigorosamente os requisitos da disciplina de Sistemas de Apoio à Decisão (PSP8 / UnB), detalhando os tipos de dados, descrições semânticas, domínios de validade, regras de obrigatoriedade e a linhagem de ponta a ponta para cada atributo modelado.

---

## 1. Tabela Fato: `fato_entregas_pedidos`

| Nome do Atributo | Tipo | Descrição | Domínio | Obrigatoriedade | Linhagem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pedido_id` | Texto (Hash) | Chave primária do pedido no marketplace | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_orders_dataset.csv` (`order_id`) |
| `item_id` | Numérico (Inteiro) | Número sequencial do item dentro do pedido | Inteiro $\ge 1$ (1 a 21) | Obrigatório (Não nulo) | `olist_order_items_dataset.csv` (`order_item_id`) |
| `cliente_id` | Texto (Hash) | Chave estrangeira que referencia a dimensão de clientes | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_orders_dataset.csv` (`customer_id`) |
| `vendedor_id` | Texto (Hash) | Chave estrangeira que referencia a dimensão de vendedores | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_order_items_dataset.csv` (`seller_id`) |
| `produto_id` | Texto (Hash) | Chave estrangeira que referencia a dimensão de produtos | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_order_items_dataset.csv` (`product_id`) |
| `data_pedido_id` | Numérico (Inteiro) | Chave estrangeira para a dimensão tempo no formato YYYYMMDD | $20160101$ a $20181231$ | Obrigatório (Não nulo) | Derivado de `order_purchase_timestamp` |
| `rota_id` | Categórico | Identificador da rota logística (UF_Origem - UF_Destino) | Siglas de UF brasileiras (ex.: `SP-RJ`, `PR-BA`) | Obrigatório (Não nulo) | Concatenação de `seller_state` e `customer_state` |
| `valor_preco` | Numérico (Contínuo) | Preço unitário do item comercializado em Reais (BRL) | $[0.85, 6735.00]$ | Obrigatório (Não nulo) | `olist_order_items_dataset.csv` (`price`) |
| `valor_frete` | Numérico (Contínuo) | Custo de frete imputado ao item em Reais (BRL) | $[0.00, 409.68]$ | Obrigatório (Não nulo) | `olist_order_items_dataset.csv` (`freight_value`) |
| `valor_total` | Numérico (Contínuo) | Valor total composto (preço + frete) | $[0.85, 6929.41]$ | Obrigatório (Não nulo) | Regra de negócio: `valor_preco + valor_frete` |
| `razao_frete_preco` | Numérico (Contínuo) | Proporção entre o valor do frete e o preço do item | $[0.00, 50.00]$ | Obrigatório (Não nulo) | Regra de negócio: `valor_frete / valor_preco` |
| `tempo_despacho_dias` | Numérico (Contínuo) | Tempo entre aprovação do pedido e expedição à transportadora | $[0.00, 125.00]$ dias | Opcional (Nulo se pendente de envio) | `(order_delivered_carrier_date - order_approved_at)` em dias |
| `tempo_transporte_dias`| Numérico (Contínuo) | Tempo de trânsito sob custódia da transportadora | $[0.00, 205.00]$ dias | Opcional (Nulo se não entregue) | `(order_delivered_customer_date - order_delivered_carrier_date)` em dias |
| `lead_time_real_dias` | Numérico (Contínuo) | Tempo decorrido entre a compra e a entrega ao cliente | $[0.53, 209.63]$ dias | Obrigatório para pedidos entregues | `(order_delivered_customer_date - order_purchase_timestamp)` em dias |
| `prazo_prometido_dias`| Numérico (Contínuo) | Prazo estimado de entrega prometido na compra | $[3.00, 155.00]$ dias | Obrigatório (Não nulo) | `(order_estimated_delivery_date - order_purchase_timestamp)` em dias |
| `dias_desvio_prazo` | Numérico (Contínuo) | Saldo entre data de entrega e data estimada | $[-146.02, 188.98]$ dias | Obrigatório para pedidos entregues | `(order_delivered_customer_date - order_estimated_delivery_date)` em dias |
| `flag_atrasado` | Booleano / Binário | Indicador de estouro do prazo prometido | $\{0, 1\}$ (0 = No prazo; 1 = Atrasado) | Obrigatório (Não nulo) | Regra de negócio: $1$ se `dias_desvio_prazo > 0`, senão $0$ |
| `flag_atraso_grave_48h`| Booleano / Binário | Indicador de atraso crítico superior a 48 horas | $\{0, 1\}$ (0 = Não; 1 = Atraso > 48h) | Obrigatório (Não nulo) | Regra de negócio: $1$ se `dias_desvio_prazo > 2.0`, senão $0$ |
| `review_score` | Numérico (Ordinal) | Nota atribuída pelo cliente na pesquisa de satisfação | $\{1, 2, 3, 4, 5\}$ | Opcional (Se nulo, cliente não avaliou) | `olist_order_reviews_dataset.csv` (`review_score`) |
| `flag_detrator` | Booleano / Binário | Cliente com avaliação negativa (score 1 ou 2) | $\{0, 1\}$ (0 = Neutro/Promotor; 1 = Detrator) | Opcional (Depende de haver avaliação) | Regra de negócio: $1$ se `review_score <= 2`, senão $0$ |

---

## 2. Dimensão Clientes: `dim_clientes`

| Nome do Atributo | Tipo | Descrição | Domínio | Obrigatoriedade | Linhagem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `cliente_id` | Texto (Hash) | Chave primária do cliente por pedido | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_customers_dataset.csv` (`customer_id`) |
| `cliente_hash_unico` | Texto (Hash) | Identificador unificado da pessoa física do cliente | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_customers_dataset.csv` (`customer_unique_id`) |
| `cep_prefixo_cliente` | Numérico (Inteiro) | Primeiros 5 dígitos do código postal de destino | $[1000, 99990]$ | Obrigatório (Não nulo) | `olist_customers_dataset.csv` (`customer_zip_code_prefix`) |
| `cidade_cliente` | Texto | Nome do município de residência do comprador | Texto padronizado em caixa baixa | Obrigatório (Não nulo) | `olist_customers_dataset.csv` (`customer_city`) |
| `estado_cliente` | Categórico | Sigla da Unidade Federativa de entrega | 27 UFs brasileiras (ex.: `SP`, `RJ`, `MG`) | Obrigatório (Não nulo) | `olist_customers_dataset.csv` (`customer_state`) |
| `regiao_cliente` | Categórico | Macrorregião geográfica oficial IBGE | `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul` | Obrigatório (Não nulo) | Regra de negócio: De-Para das 27 UFs para as 5 regiões IBGE |

---

## 3. Dimensão Vendedores: `dim_vendedores`

| Nome do Atributo | Tipo | Descrição | Domínio | Obrigatoriedade | Linhagem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `vendedor_id` | Texto (Hash) | Chave primária do parceiro/lojista cadastrado | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_sellers_dataset.csv` (`seller_id`) |
| `cep_prefixo_vendedor`| Numérico (Inteiro) | Primeiros 5 dígitos do código postal de expedição | $[1000, 99990]$ | Obrigatório (Não nulo) | `olist_sellers_dataset.csv` (`seller_zip_code_prefix`) |
| `cidade_vendedor` | Texto | Município de operação e estoque do vendedor | Texto padronizado em caixa baixa | Obrigatório (Não nulo) | `olist_sellers_dataset.csv` (`seller_city`) |
| `estado_vendedor` | Categórico | Sigla da Unidade Federativa do vendedor | 27 UFs brasileiras | Obrigatório (Não nulo) | `olist_sellers_dataset.csv` (`seller_state`) |
| `regiao_vendedor` | Categórico | Macrorregião geográfica oficial IBGE do vendedor | `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul` | Obrigatório (Não nulo) | Regra de negócio: De-Para das 27 UFs para as 5 regiões IBGE |

---

## 4. Dimensão Produtos: `dim_produtos`

| Nome do Atributo | Tipo | Descrição | Domínio | Obrigatoriedade | Linhagem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `produto_id` | Texto (Hash) | Chave primária do catálogo de mercadorias | Hash hexadecimal de 32 caracteres | Obrigatório (Não nulo) | `olist_products_dataset.csv` (`product_id`) |
| `categoria_pt` | Categórico | Categoria primária em língua portuguesa | 73 categorias padronizadas | Opcional (Se nulo, atribuído 'outros') | `olist_products_dataset.csv` (`product_category_name`) |
| `categoria_en` | Categórico | Categoria traduzida em inglês | 71 categorias padronizadas | Opcional (Se nulo, atribuído 'other') | Join com `product_category_name_translation.csv` |
| `peso_gramas` | Numérico (Inteiro) | Peso bruto declarado da mercadoria embalada | $[2, 40400]$ gramas | Opcional (Tratado por imputação de mediana da categoria) | `olist_products_dataset.csv` (`product_weight_g`) |
| `comprimento_cm` | Numérico (Inteiro) | Dimensão linear de comprimento em centímetros | $[10, 105]$ cm | Opcional | `olist_products_dataset.csv` (`product_length_cm`) |
| `altura_cm` | Numérico (Inteiro) | Dimensão linear de altura em centímetros | $[2, 105]$ cm | Opcional | `olist_products_dataset.csv` (`product_height_cm`) |
| `largura_cm` | Numérico (Inteiro) | Dimensão linear de largura em centímetros | $[10, 118]$ cm | Opcional | `olist_products_dataset.csv` (`product_width_cm`) |
| `volume_cm3` | Numérico (Contínuo) | Volume cubado da embalagem do produto | $[168.0, 296010.0]\text{ cm}^3$ | Opcional | Regra de negócio: $Comprimento \times Altura \times Largura$ |
| `faixa_peso` | Categórico (Ordinal) | Classificação logística operacional de peso | `Leve (<1kg)`, `Médio (1-5kg)`, `Pesado (5-15kg)`, `Muito Pesado (>15kg)` | Obrigatório | Regra de negócio: Discretização de `peso_gramas` em bins |

---

## 5. Dimensão Rotas Logísticas: `dim_rotas_logisticas`

| Nome do Atributo | Tipo | Descrição | Domínio | Obrigatoriedade | Linhagem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `rota_id` | Categórico | Identificador único da rota (Origem-Destino) | Ex.: `SP-SP`, `SP-RJ`, `PR-BA` | Obrigatório (Não nulo) | Chave sintética `estado_vendedor - estado_cliente` |
| `estado_origem` | Categórico | UF de expedição da mercadoria | 27 UFs brasileiras | Obrigatório (Não nulo) | `dim_vendedores.estado_vendedor` |
| `estado_destino` | Categórico | UF de entrega final ao cliente | 27 UFs brasileiras | Obrigatório (Não nulo) | `dim_clientes.estado_cliente` |
| `regiao_origem` | Categórico | Região IBGE de origem do fluxo | 5 Regiões | Obrigatório (Não nulo) | Mapeamento regional da UF origem |
| `regiao_destino` | Categórico | Região IBGE de destino do fluxo | 5 Regiões | Obrigatório (Não nulo) | Mapeamento regional da UF destino |
| `tipo_rota` | Categórico (Ordinal) | Classificação da complexidade da malha | `1. Intraestadual`, `2. Interestadual (Mesma Região)`, `3. Inter-regional` | Obrigatório (Não nulo) | Regra de negócio condicional baseada na igualdade de estados e regiões |

---

## 6. Dimensão Tempo: `dim_tempo`

| Nome do Atributo | Tipo | Descrição | Domínio | Obrigatoriedade | Linhagem |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `data_id` | Numérico (Inteiro) | Chave primária substituta no formato YYYYMMDD | $20160101$ a $20181231$ | Obrigatório (Não nulo) | Gerado a partir da data de compra |
| `data_completa` | Data | Data civil gregoriana correspondente | 2016-01-01 a 2018-12-31 | Obrigatório (Não nulo) | Truncamento diário do timestamp de compra |
| `ano` | Numérico (Inteiro) | Ano civil da compra | $\{2016, 2017, 2018\}$ | Obrigatório (Não nulo) | Extração do componente de ano |
| `mes` | Numérico (Inteiro) | Mês do ano | $[1, 12]$ | Obrigatório (Não nulo) | Extração do componente de mês |
| `dia` | Numérico (Inteiro) | Dia do mês | $[1, 31]$ | Obrigatório (Não nulo) | Extração do componente de dia |
| `nome_mes` | Texto | Nome por extenso do mês | `Janeiro` a `Dezembro` | Obrigatório (Não nulo) | Formatação em português |
| `dia_semana` | Texto | Dia da semana | `Segunda-feira` a `Domingo` | Obrigatório (Não nulo) | Extração do dia da semana |
| `flag_fim_de_semana` | Booleano / Binário | Indicador de sábado ou domingo | $\{0, 1\}$ | Obrigatório (Não nulo) | $1$ se sábado/domingo, senão $0$ |
| `trimestre` | Numérico (Inteiro) | Trimestre civil | $\{1, 2, 3, 4\}$ | Obrigatório (Não nulo) | Mapeamento trimestral |
