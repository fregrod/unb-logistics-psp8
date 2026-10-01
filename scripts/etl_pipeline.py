"""
Pipeline de Engenharia de Dados e ETL — Olist E-Commerce Logistics
Disciplina: Sistemas de Apoio à Decisão (PSP8) - Engenharia de Produção / UnB
Autor: Rodrigo Fregonasse
Professor: André Luiz Marques Serrano

Descrição:
Este script executa o pipeline completo de Extração, Transformação e Carga (ETL):
1. Ingestão dos dados brutos (Raw/Bronze)
2. Limpeza, tratamento de tipos e valores faltantes
3. Aplicação de regras de negócio (Lead Time, Desvio de Prazo, Burden de Frete, Rotas)
4. Construção da Modelagem Dimensional (Esquema Estrela / Star Schema)
5. Persistência dos dados analíticos (Silver/Gold) em formato colunar Parquet
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

# Mapeamento oficial de UFs para Macrorregiões do IBGE
UF_TO_REGION = {
    'SP': 'Sudeste', 'RJ': 'Sudeste', 'MG': 'Sudeste', 'ES': 'Sudeste',
    'PR': 'Sul', 'SC': 'Sul', 'RS': 'Sul',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'BA': 'Nordeste', 'PE': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
    'PB': 'Nordeste', 'RN': 'Nordeste', 'AL': 'Nordeste', 'PI': 'Nordeste', 'SE': 'Nordeste',
    'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'TO': 'Norte',
    'AC': 'Norte', 'AP': 'Norte', 'RR': 'Norte'
}

def ensure_directories():
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('evidencias', exist_ok=True)

def load_raw_data(data_dir='data/raw'):
    print("=" * 60)
    print("1. EXTRAÇÃO: Carregando arquivos brutos (Camada Bronze)...")
    print("=" * 60)
    
    files_needed = [
        'olist_orders_dataset.csv',
        'olist_order_items_dataset.csv',
        'olist_customers_dataset.csv',
        'olist_sellers_dataset.csv',
        'olist_products_dataset.csv',
        'olist_order_reviews_dataset.csv',
        'product_category_name_translation.csv'
    ]
    
    # Se os arquivos não existirem em data/raw, buscar do cache do kagglehub
    for f in files_needed:
        target = os.path.join(data_dir, f)
        if not os.path.exists(target):
            cache_path = os.path.expanduser('~/.cache/kagglehub/datasets/olistbr/brazilian-ecommerce/versions/2')
            source = os.path.join(cache_path, f)
            if os.path.exists(source):
                import shutil
                shutil.copy(source, target)
                print(f"Copiado do cache: {f}")
            else:
                raise FileNotFoundError(f"Arquivo {f} não encontrado em {data_dir} nem no cache.")

    orders = pd.read_csv(os.path.join(data_dir, 'olist_orders_dataset.csv'))
    items = pd.read_csv(os.path.join(data_dir, 'olist_order_items_dataset.csv'))
    customers = pd.read_csv(os.path.join(data_dir, 'olist_customers_dataset.csv'))
    sellers = pd.read_csv(os.path.join(data_dir, 'olist_sellers_dataset.csv'))
    products = pd.read_csv(os.path.join(data_dir, 'olist_products_dataset.csv'))
    reviews = pd.read_csv(os.path.join(data_dir, 'olist_order_reviews_dataset.csv'))
    translations = pd.read_csv(os.path.join(data_dir, 'product_category_name_translation.csv'))
    
    print(f"-> Pedidos brutos carregados: {len(orders):,}")
    print(f"-> Itens de pedidos: {len(items):,}")
    print(f"-> Clientes: {len(customers):,}")
    print(f"-> Vendedores: {len(sellers):,}")
    print(f"-> Produtos: {len(products):,}")
    print(f"-> Avaliações: {len(reviews):,}")
    
    return orders, items, customers, sellers, products, reviews, translations

def transform_and_build_dimensions(orders, items, customers, sellers, products, reviews, translations):
    print("\n" + "=" * 60)
    print("2. TRANSFORMAÇÃO: Aplicando regras de negócio e modelagem...")
    print("=" * 60)
    
    # 2.1 Filtrar pedidos entregues e converter timestamps
    df_orders = orders[orders['order_status'] == 'delivered'].copy()
    date_cols = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for c in date_cols:
        df_orders[c] = pd.to_datetime(df_orders[c])
        
    # Descartar registros com inconsistência física (sem data de entrega ao cliente)
    df_orders = df_orders.dropna(subset=['order_delivered_customer_date', 'order_purchase_timestamp'])
    print(f"-> Pedidos entregues válidos após limpeza de datas: {len(df_orders):,}")
    
    # 2.2 Deduplicar avaliações (manter a mais recente por pedido)
    reviews_clean = reviews.sort_values(by='review_answer_timestamp', ascending=False).drop_duplicates(subset=['order_id'])
    
    # 2.3 Construir Dimensão Clientes
    dim_clientes = customers.copy()
    dim_clientes.rename(columns={
        'customer_id': 'cliente_id',
        'customer_unique_id': 'cliente_hash_unico',
        'customer_zip_code_prefix': 'cep_prefixo_cliente',
        'customer_city': 'cidade_cliente',
        'customer_state': 'estado_cliente'
    }, inplace=True)
    dim_clientes['regiao_cliente'] = dim_clientes['estado_cliente'].map(UF_TO_REGION).fillna('Indefinido')
    
    # 2.4 Construir Dimensão Vendedores
    dim_vendedores = sellers.copy()
    dim_vendedores.rename(columns={
        'seller_id': 'vendedor_id',
        'seller_zip_code_prefix': 'cep_prefixo_vendedor',
        'seller_city': 'cidade_vendedor',
        'seller_state': 'estado_vendedor'
    }, inplace=True)
    dim_vendedores['regiao_vendedor'] = dim_vendedores['estado_vendedor'].map(UF_TO_REGION).fillna('Indefinido')
    
    # 2.5 Construir Dimensão Produtos
    dim_produtos = products.merge(translations, on='product_category_name', how='left').copy()
    dim_produtos['categoria_pt'] = dim_produtos['product_category_name'].fillna('outros')
    dim_produtos['categoria_en'] = dim_produtos['product_category_name_english'].fillna('other')
    dim_produtos['peso_gramas'] = dim_produtos['product_weight_g'].fillna(dim_produtos['product_weight_g'].median())
    
    # Volume em cm3 (Comprimento * Altura * Largura)
    dim_produtos['volume_cm3'] = (
        dim_produtos['product_length_cm'].fillna(dim_produtos['product_length_cm'].median()) *
        dim_produtos['product_height_cm'].fillna(dim_produtos['product_height_cm'].median()) *
        dim_produtos['product_width_cm'].fillna(dim_produtos['product_width_cm'].median())
    )
    
    # Faixa de peso (Discretização em Bins)
    def classificar_peso(p):
        if p < 1000:
            return '1. Leve (<1kg)'
        elif p <= 5000:
            return '2. Médio (1-5kg)'
        elif p <= 15000:
            return '3. Pesado (5-15kg)'
        else:
            return '4. Muito Pesado (>15kg)'
            
    dim_produtos['faixa_peso'] = dim_produtos['peso_gramas'].apply(classificar_peso)
    dim_produtos = dim_produtos[['product_id', 'categoria_pt', 'categoria_en', 'peso_gramas', 'volume_cm3', 'faixa_peso']]
    dim_produtos.rename(columns={'product_id': 'produto_id'}, inplace=True)
    
    # 2.6 Construir a Tabela Fato (Junção dos Itens com Pedidos)
    fato = items.merge(df_orders, on='order_id', how='inner')
    fato = fato.merge(customers[['customer_id', 'customer_state']], on='customer_id', how='left')
    fato = fato.merge(sellers[['seller_id', 'seller_state']], on='seller_id', how='left')
    fato = fato.merge(reviews_clean[['order_id', 'review_score']], on='order_id', how='left')
    
    # 2.7 Regras de Negócio e Cálculos de Métricas Temporais
    fato['lead_time_real_dias'] = (fato['order_delivered_customer_date'] - fato['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    fato['prazo_prometido_dias'] = (fato['order_estimated_delivery_date'] - fato['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    fato['dias_desvio_prazo'] = (fato['order_delivered_customer_date'] - fato['order_estimated_delivery_date']).dt.total_seconds() / 86400.0
    
    # Flags de atraso
    fato['flag_atrasado'] = (fato['dias_desvio_prazo'] > 0).astype(int)
    fato['flag_atraso_grave_48h'] = (fato['dias_desvio_prazo'] > 2.0).astype(int)
    
    # Tempos intermediários
    fato['tempo_aprovacao_dias'] = (fato['order_approved_at'] - fato['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    fato['tempo_despacho_dias'] = (fato['order_delivered_carrier_date'] - fato['order_approved_at']).dt.total_seconds() / 86400.0
    fato['tempo_transporte_dias'] = (fato['order_delivered_customer_date'] - fato['order_delivered_carrier_date']).dt.total_seconds() / 86400.0
    
    # Métricas financeiras
    fato['valor_preco'] = fato['price']
    fato['valor_frete'] = fato['freight_value']
    fato['valor_total'] = fato['valor_preco'] + fato['valor_frete']
    fato['razao_frete_preco'] = np.where(fato['valor_preco'] > 0, fato['valor_frete'] / fato['valor_preco'], 0)
    
    # Chave para dimensão tempo (YYYYMMDD)
    fato['data_pedido_id'] = fato['order_purchase_timestamp'].dt.strftime('%Y%m%d').astype(int)
    
    # Chave para rota logística
    fato['estado_origem'] = fato['seller_state'].fillna('XX')
    fato['estado_destino'] = fato['customer_state'].fillna('XX')
    fato['rota_id'] = fato['estado_origem'] + '-' + fato['estado_destino']
    
    # Avaliação e flag de detrator
    fato['flag_detrator'] = np.where(fato['review_score'].notnull() & (fato['review_score'] <= 2), 1, 0)
    
    # Renomear identificadores
    fato.rename(columns={
        'order_id': 'pedido_id',
        'order_item_id': 'item_id',
        'customer_id': 'cliente_id',
        'seller_id': 'vendedor_id',
        'product_id': 'produto_id'
    }, inplace=True)
    
    # Seleção final de colunas da FATO
    colunas_fato = [
        'pedido_id', 'item_id', 'cliente_id', 'vendedor_id', 'produto_id',
        'data_pedido_id', 'rota_id',
        'valor_preco', 'valor_frete', 'valor_total', 'razao_frete_preco',
        'tempo_aprovacao_dias', 'tempo_despacho_dias', 'tempo_transporte_dias',
        'lead_time_real_dias', 'prazo_prometido_dias', 'dias_desvio_prazo',
        'flag_atrasado', 'flag_atraso_grave_48h',
        'review_score', 'flag_detrator'
    ]
    fato_entregas_pedidos = fato[colunas_fato].copy()
    
    # 2.8 Construir Dimensão Rotas Logísticas
    rotas_unicas = fato[['rota_id', 'estado_origem', 'estado_destino']].drop_duplicates().copy()
    rotas_unicas['regiao_origem'] = rotas_unicas['estado_origem'].map(UF_TO_REGION).fillna('Indefinido')
    rotas_unicas['regiao_destino'] = rotas_unicas['estado_destino'].map(UF_TO_REGION).fillna('Indefinido')
    
    def classificar_tipo_rota(r):
        if r['estado_origem'] == r['estado_destino']:
            return '1. Intraestadual'
        elif r['regiao_origem'] == r['regiao_destino']:
            return '2. Interestadual (Mesma Região)'
        else:
            return '3. Inter-regional'
            
    rotas_unicas['tipo_rota'] = rotas_unicas.apply(classificar_tipo_rota, axis=1)
    dim_rotas_logisticas = rotas_unicas[['rota_id', 'estado_origem', 'estado_destino', 'regiao_origem', 'regiao_destino', 'tipo_rota']].copy()
    
    # 2.9 Construir Dimensão Tempo
    datas_unicas = df_orders['order_purchase_timestamp'].dt.normalize().drop_duplicates().sort_values()
    dim_tempo = pd.DataFrame({'data_completa': datas_unicas})
    dim_tempo['data_id'] = dim_tempo['data_completa'].dt.strftime('%Y%m%d').astype(int)
    dim_tempo['ano'] = dim_tempo['data_completa'].dt.year
    dim_tempo['mes'] = dim_tempo['data_completa'].dt.month
    dim_tempo['dia'] = dim_tempo['data_completa'].dt.day
    meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
    dim_tempo['nome_mes'] = dim_tempo['mes'].map(meses_pt)
    dias_pt = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira',
               4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
    dim_tempo['dia_semana'] = dim_tempo['data_completa'].dt.dayofweek.map(dias_pt)
    dim_tempo['flag_fim_de_semana'] = dim_tempo['data_completa'].dt.dayofweek.isin([5, 6]).astype(int)
    dim_tempo['trimestre'] = dim_tempo['data_completa'].dt.quarter
    dim_tempo = dim_tempo[['data_id', 'data_completa', 'ano', 'mes', 'dia', 'nome_mes', 'dia_semana', 'flag_fim_de_semana', 'trimestre']]
    
    print(f"-> Fato Entregas gerada com: {len(fato_entregas_pedidos):,} registros")
    print(f"-> Dimensão Clientes: {len(dim_clientes):,} registros")
    print(f"-> Dimensão Vendedores: {len(dim_vendedores):,} registros")
    print(f"-> Dimensão Produtos: {len(dim_produtos):,} registros")
    print(f"-> Dimensão Rotas: {len(dim_rotas_logisticas):,} registros")
    print(f"-> Dimensão Tempo: {len(dim_tempo):,} registros")
    
    return fato_entregas_pedidos, dim_clientes, dim_vendedores, dim_produtos, dim_rotas_logisticas, dim_tempo

def save_gold_layer(fato, clientes, vendedores, produtos, rotas, tempo, out_dir='data/processed'):
    print("\n" + "=" * 60)
    print("3. CARGA: Persistindo tabelas analíticas (Camada Gold)...")
    print("=" * 60)
    
    tabelas = {
        'fato_entregas_pedidos': fato,
        'dim_clientes': clientes,
        'dim_vendedores': vendedores,
        'dim_produtos': produtos,
        'dim_rotas_logisticas': rotas,
        'dim_tempo': tempo
    }
    
    for nome, df in tabelas.items():
        parquet_path = os.path.join(out_dir, f"{nome}.parquet")
        csv_path = os.path.join(out_dir, f"{nome}.csv")
        df.to_parquet(parquet_path, index=False)
        # Salvar também uma amostra ou CSV compactado para fácil inspeção
        if len(df) > 50000:
            df.head(1000).to_csv(os.path.join(out_dir, f"{nome}_amostra_1000.csv"), index=False)
        else:
            df.to_csv(csv_path, index=False)
        print(f"Tabela persistida: {parquet_path} ({len(df):,} linhas)")
        
    print("\nETL Finalizado com Sucesso!")

def main():
    ensure_directories()
    orders, items, customers, sellers, products, reviews, translations = load_raw_data()
    fato, clientes, vendedores, produtos, rotas, tempo = transform_and_build_dimensions(
        orders, items, customers, sellers, products, reviews, translations
    )
    save_gold_layer(fato, clientes, vendedores, produtos, rotas, tempo)

if __name__ == '__main__':
    main()
