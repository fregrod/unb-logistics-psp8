# Guia Prático de Execução no Databricks e Registro de Evidências

Este documento orienta a execução do pipeline de dados no **Databricks Community Edition** (gratuito) e detalha o roteiro para captura das evidências visuais exigidas no barema de avaliação (Seções 5.2 e 7 do manual de PSP8).

---

## 1. Acesso e Criação do Cluster no Databricks Community Edition

1. Acesse: [https://community.cloud.databricks.com/](https://community.cloud.databricks.com/) e faça login com sua conta.
2. No menu lateral esquerdo, clique em **Compute**.
3. Clique em **Create Compute** (ou **Create Cluster**):
   * **Cluster Name:** `cluster-psp8-mvp`
   * **Databricks Runtime Version:** Escolha a versão recomendada padrão LTS (ex.: *Runtime 13.3 LTS ou 14.3 LTS - Scala 2.12, Spark 3.4/3.5*).
   * O cluster gratuito é do tipo *Single Node* com 15 GB de memória.
4. Clique em **Create Cluster** e aguarde 2 a 3 minutos até o ícone de status ficar verde (**Running**).

> **📸 Evidência 1 a Capturar:**  
> Tire um print da tela do **Compute** mostrando o cluster com status **Running** e salve como `evidencias/01_cluster_ativo_databricks.png`.

---

## 2. Importação dos Notebooks

1. No menu lateral esquerdo, clique em **Workspace**.
2. Clique na pasta do seu usuário (**Users / seu_email**).
3. Clique com o botão direito (ou na seta para baixo) e selecione **Import**:
   * Escolha **File** e faça o upload do arquivo `notebooks/01_pipeline_etl_databricks.ipynb`.
   * Repita a operação para importar `notebooks/02_analise_exploratoria_e_decisao.ipynb`.

---

## 3. Execução do Pipeline ETL na Nuvem

1. Abra o notebook `01_pipeline_etl_databricks`.
2. No canto superior esquerdo do notebook, vincule o cluster ativo `cluster-psp8-mvp` no dropdown **Connect**.
3. Clique no botão **Run All** (ou execute célula por célula com `Shift + Enter`):
   * A Célula 1 instalará as bibliotecas necessárias via `%pip`.
   * A Célula 2 fará o download da base da Olist e copiará os CSVs para o DBFS.
   * As Células 3 a 6 processarão os dados distribuídos com PySpark.
   * A Célula 7 salvará as tabelas no formato **Delta Lake** (`gold_fato_entregas_pedidos`, etc.).
   * A Célula 8 executará a consulta Spark SQL de validação.

> **📸 Evidência 2 Registrada:**  
> Print da execução bem-sucedida das tabelas no catálogo Delta e da consulta Spark SQL:
>
> ![Execução do Pipeline e Tabelas Delta no Databricks](02_execucao_pipeline_etl_nuvem.png)

---

## 4. Verificação das Tabelas no Catálogo de Dados da Nuvem

1. No menu lateral esquerdo do Databricks, clique em **Catalog** (ou **Data**).
2. Expanda o banco de dados dedicado criado pelo pipeline: **`psp8_olist_dw`**:
   * Você verá todas as tabelas gerenciadas em formato **Delta Lake**:
     * **Camada Gold (Dimensional):**
       * `fato_entregas_pedidos`
       * `dim_clientes`
       * `dim_vendedores`
       * `dim_produtos`
       * `dim_rotas_logisticas`
       * `dim_tempo`
     * **Camada Bronze (Data Lake Bruto):**
       * `bronze_orders`, `bronze_order_items`, `bronze_customers`, etc.
3. Clique sobre `fato_entregas_pedidos` e veja a aba **Schema**, **Details** (formato DELTA) e **Sample Data**.

> **📸 Evidência 3 a Capturar:**  
> Tire um print do catálogo da nuvem mostrando o banco `psp8_olist_dw` e as tabelas Delta criadas e salve como `evidencias/03_tabelas_delta_persistidas_nuvem.png`.

---

## 5. Execução do Notebook de Análise e Decisão

1. Abra o notebook `02_analise_exploratoria_e_decisao`.
2. Conecte ao mesmo cluster e execute as células para visualização das respostas às perguntas de negócio.

> **📸 Evidência 4 a Capturar:**  
> Tire um print de um dos gráficos gerados dentro do notebook do Databricks e salve como `evidencias/04_dashboard_analise_decisao.png`.

---

## Resumo dos Arquivos de Evidência

| Arquivo Esperado | O que deve mostrar |
| :--- | :--- |
| `evidencias/01_cluster_ativo_databricks.png` | Cluster Spark ativo e em execução no Databricks Community Edition |
| `evidencias/02_execucao_pipeline_etl_nuvem.png` | Células do pipeline executadas com sucesso e saída Spark SQL |
| `evidencias/03_tabelas_delta_persistidas_nuvem.png` | Catálogo de dados (Data/Catalog) comprovando a persistência física das tabelas Delta |
| `evidencias/04_dashboard_analise_decisao.png` | Célula analítica com gráficos executada no ambiente de nuvem |
