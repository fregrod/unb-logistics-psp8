"""
Geração de Gráficos e Evidências Analíticas — Olist E-Commerce
Disciplina: Sistemas de Apoio à Decisão (PSP8) - Engenharia de Produção / UnB
Autor: Rodrigo Fregonasse

Este script carrega a Camada Gold (Parquet) e gera visualizações estatísticas de alta resolução
para responder às 5 perguntas de negócio formuladas, alinhadas aos conceitos dos Módulos 1, 2 e 3.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração global de estilo visual profissional
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#eeeeee'
plt.rcParams['grid.linestyle'] = '--'

OUTPUT_DIR = 'evidencias/graficos'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def carregar_dados():
    print("Carregando tabelas da Camada Gold...")
    fato = pd.read_parquet('data/processed/fato_entregas_pedidos.parquet')
    clientes = pd.read_parquet('data/processed/dim_clientes.parquet')
    produtos = pd.read_parquet('data/processed/dim_produtos.parquet')
    rotas = pd.read_parquet('data/processed/dim_rotas_logisticas.parquet')
    tempo = pd.read_parquet('data/processed/dim_tempo.parquet')
    
    # Merge analítico
    df = fato.merge(clientes[['cliente_id', 'estado_cliente', 'regiao_cliente']], on='cliente_id', how='left')
    df = df.merge(produtos[['produto_id', 'categoria_pt', 'categoria_en', 'faixa_peso', 'peso_gramas']], on='produto_id', how='left')
    df = df.merge(rotas[['rota_id', 'tipo_rota', 'regiao_origem', 'regiao_destino']], on='rota_id', how='left')
    return df

def gerar_grafico_1_regional(df):
    print("Gerando Gráfico 1: Disparidade Regional de Lead Time...")
    
    agg = df.groupby('regiao_cliente').agg(
        lead_time_medio=('lead_time_real_dias', 'mean'),
        lead_time_mediana=('lead_time_real_dias', 'median'),
        taxa_atraso_pct=('flag_atrasado', lambda x: x.mean() * 100),
        total_pedidos=('pedido_id', 'count')
    ).sort_values(by='lead_time_medio', ascending=False).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Subplot 1: Média vs Mediana de Lead Time
    bar_width = 0.35
    x = np.arange(len(agg))
    
    rects1 = ax1.bar(x - bar_width/2, agg['lead_time_medio'], bar_width, label='Lead Time Médio', color='#1f77b4', alpha=0.9)
    rects2 = ax1.bar(x + bar_width/2, agg['lead_time_mediana'], bar_width, label='Lead Time Mediana', color='#aec7e8', alpha=0.9)
    
    ax1.set_title('Lead Time Real de Entrega por Região de Destino (Dias)', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Região de Destino (Cliente)', fontsize=11, labelpad=10)
    ax1.set_ylabel('Dias Decorridos (Compra até Entrega)', fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(agg['regiao_cliente'], fontsize=10)
    ax1.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    # Anotações nas barras
    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f'{h:.1f}d', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for rect in rects2:
        h = rect.get_height()
        ax1.annotate(f'{h:.1f}d', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=9)

    # Subplot 2: Taxa de Atraso por Região
    colors = ['#d62728' if r in ['Nordeste', 'Norte'] else '#2ca02c' for r in agg['regiao_cliente']]
    bars = ax2.bar(agg['regiao_cliente'], agg['taxa_atraso_pct'], color=colors, alpha=0.85, width=0.55)
    ax2.set_title('Taxa de Atraso na Entrega (%) por Região de Destino', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xlabel('Região de Destino (Cliente)', fontsize=11, labelpad=10)
    ax2.set_ylabel('Percentual de Pedidos Fora do Prazo (%)', fontsize=11)
    
    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f'{h:.2f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '01_disparidade_regional_lead_time.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Salvo: {output_path}")

def gerar_grafico_2_boxplot(df):
    print("Gerando Gráfico 2: Boxplot Comparativo de Lead Time por Região...")
    
    plt.figure(figsize=(12, 6))
    order = ['Sudeste', 'Sul', 'Centro-Oeste', 'Nordeste', 'Norte']
    
    sns.boxplot(
        x='regiao_cliente',
        y='lead_time_real_dias',
        data=df,
        order=order,
        palette='Blues_r',
        showmeans=True,
        meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"red", "markersize":"6"},
        flierprops={"marker":"o", "markersize":3, "alpha":0.2, "color":"gray"}
    )
    
    plt.ylim(0, 60) # Foco até 60 dias para legibilidade do IQR e whiskers
    plt.title('Distribuição do Lead Time de Entrega por Região (Boxplot com Médias e Outliers)', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Região de Destino (Cliente)', fontsize=11, labelpad=10)
    plt.ylabel('Lead Time Real (Dias)', fontsize=11)
    plt.annotate('Ponto Vermelho: Média | Linha Central: Mediana', xy=(0.02, 0.93), xycoords='axes fraction',
                 fontsize=10, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    output_path = os.path.join(OUTPUT_DIR, '02_boxplot_lead_time_regiao.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Salvo: {output_path}")

def gerar_grafico_3_burden_frete(df):
    print("Gerando Gráfico 3: Razão Frete/Preço vs Atrasos e Satisfação...")
    
    df_valid = df[(df['valor_preco'] > 0) & (df['review_score'].notnull())].copy()
    
    # Criar faixas de Burden de Frete
    bins = [0, 0.10, 0.20, 0.35, 0.50, 1.0, 50.0]
    labels = ['<10%', '10-20%', '20-35%', '35-50%', '50-100%', '>100%']
    df_valid['faixa_burden'] = pd.cut(df_valid['razao_frete_preco'], bins=bins, labels=labels, right=False)
    
    agg = df_valid.groupby('faixa_burden', observed=True).agg(
        review_medio=('review_score', 'mean'),
        taxa_detratores=('flag_detrator', lambda x: x.mean() * 100),
        taxa_atraso=('flag_atrasado', lambda x: x.mean() * 100),
        total_itens=('pedido_id', 'count')
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    ax2 = ax1.twinx()
    
    bar_width = 0.35
    x = np.arange(len(agg))
    
    bars1 = ax1.bar(x - bar_width/2, agg['review_medio'], bar_width, label='Score Médio de Avaliação (1 a 5)', color='#1f77b4', alpha=0.85)
    bars2 = ax2.bar(x + bar_width/2, agg['taxa_detratores'], bar_width, label='% Clientes Detratores (Score 1-2)', color='#d62728', alpha=0.85)
    
    ax1.set_title('Impacto do Peso Relativo do Frete (Frete / Preço) na Satisfação do Cliente', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Razão Frete / Preço do Produto', fontsize=11, labelpad=10)
    ax1.set_ylabel('Nota Média de Avaliação (Escala 1 a 5)', fontsize=11, color='#1f77b4')
    ax2.set_ylabel('% de Avaliações Detratoras (Notas 1 e 2)', fontsize=11, color='#d62728')
    
    ax1.set_ylim(3.0, 5.0)
    ax2.set_ylim(0, 30)
    ax1.set_xticks(x)
    ax1.set_xticklabels(agg['faixa_burden'], fontsize=10)
    
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#a00')

    # Combinar legendas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', frameon=True, facecolor='white')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '03_burden_frete_vs_satisfacao.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Salvo: {output_path}")

def gerar_grafico_4_top_categorias(df):
    print("Gerando Gráfico 4: Top Categorias com Maior Taxa de Atraso...")
    
    cat_summary = df.groupby('categoria_pt').agg(
        total_itens=('pedido_id', 'count'),
        taxa_atraso_pct=('flag_atrasado', lambda x: x.mean() * 100),
        peso_medio_kg=('peso_gramas', lambda x: x.mean() / 1000.0)
    )
    # Filtrar categorias relevantes com pelo menos 500 itens
    cat_top = cat_summary[cat_summary['total_itens'] >= 500].sort_values(by='taxa_atraso_pct', ascending=True).tail(12)

    plt.figure(figsize=(12, 7))
    bars = plt.barh(cat_top.index, cat_top['taxa_atraso_pct'], color='#3182bd', alpha=0.9, height=0.6)
    
    plt.title('Top Categorias com Maior Incidência de Atrasos na Entrega (Mín. 500 itens)', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Taxa de Atraso na Entrega (%)', fontsize=11, labelpad=10)
    plt.ylabel('Categoria do Produto', fontsize=11)
    plt.xlim(0, 12)
    
    for bar, peso, total in zip(bars, cat_top['peso_medio_kg'], cat_top['total_itens']):
        w = bar.get_width()
        plt.text(w + 0.15, bar.get_y() + bar.get_height()/2, f'{w:.2f}% (Peso Médio: {peso:.1f}kg | n={total:,})',
                 ha='left', va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '04_top_categorias_atraso.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Salvo: {output_path}")

def gerar_grafico_5_matriz_rotas(df):
    print("Gerando Gráfico 5: Matriz de Atrasos Origem x Destino...")
    
    # Tabela cruzada Região Origem x Região Destino
    crosstab = pd.crosstab(
        df['regiao_origem'],
        df['regiao_destino'],
        values=df['flag_atrasado'] * 100,
        aggfunc='mean'
    )
    
    # Reordenar para consistência
    ordem = ['Sudeste', 'Sul', 'Centro-Oeste', 'Nordeste', 'Norte']
    crosstab = crosstab.reindex(index=ordem, columns=ordem)

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        crosstab,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Taxa de Atraso Médio (%)'},
        linewidths=0.5,
        linecolor='white'
    )
    
    plt.title('Matriz de Taxa de Atraso (%) por Região de Origem (Vendedor) vs Destino (Cliente)', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Região de Destino (Cliente)', fontsize=11, labelpad=10)
    plt.ylabel('Região de Origem (Vendedor)', fontsize=11, labelpad=10)

    output_path = os.path.join(OUTPUT_DIR, '05_matriz_rotas_taxa_atraso.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Salvo: {output_path}")

def gerar_grafico_6_csat_impacto(df):
    print("Gerando Gráfico 6: Impacto do Atraso no CSAT e % Detratores...")
    
    df_reviews = df[df['review_score'].notnull()].copy()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. Distribuição das Notas (No Prazo vs Atrasado)
    dist = pd.crosstab(df_reviews['flag_atrasado'], df_reviews['review_score'], normalize='index') * 100
    dist.index = ['No Prazo', 'Atrasado']
    
    dist.plot(kind='bar', stacked=True, ax=ax1, colormap='RdYlGn', alpha=0.9, width=0.45)
    ax1.set_title('Composição das Notas de Avaliação (1 a 5 Estrelas)', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xlabel('Status de Cumprimento do Prazo', fontsize=11, labelpad=10)
    ax1.set_ylabel('Proporção de Pedidos (%)', fontsize=11)
    ax1.set_xticklabels(['No Prazo', 'Com Atraso'], rotation=0, fontsize=11, fontweight='bold')
    ax1.legend(title='Estrelas', bbox_to_anchor=(1.02, 1), loc='upper left')

    # 2. Taxa de Detratores e Média do CSAT
    resumo = df_reviews.groupby('flag_atrasado').agg(
        score_medio=('review_score', 'mean'),
        pct_detratores=('flag_detrator', lambda x: x.mean() * 100)
    ).reset_index()
    resumo['status'] = ['No Prazo (88.1k)', 'Com Atraso (7.6k)']
    
    bars = ax2.bar(resumo['status'], resumo['pct_detratores'], color=['#2ca02c', '#d62728'], width=0.45, alpha=0.85)
    ax2.set_title('Percentual de Clientes Detratores (Notas 1 e 2)', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xlabel('Status de Cumprimento do Prazo', fontsize=11, labelpad=10)
    ax2.set_ylabel('% de Avaliações Detratoras', fontsize=11)
    ax2.set_ylim(0, 65)
    
    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=12, fontweight='bold')
        
    ax2.annotate('Salto de 5.8x na insatisfação\nquando há atraso na entrega', xy=(1, 55), xytext=(0.5, 58),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#fee', edgecolor='#d62728'))

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, '06_impacto_atraso_csat.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"-> Salvo: {output_path}")

def main():
    df = carregar_dados()
    gerar_grafico_1_regional(df)
    gerar_grafico_2_boxplot(df)
    gerar_grafico_3_burden_frete(df)
    gerar_grafico_4_top_categorias(df)
    gerar_grafico_5_matriz_rotas(df)
    gerar_grafico_6_csat_impacto(df)
    print("\nTodos os gráficos foram gerados e salvos com sucesso em evidencias/graficos/")

if __name__ == '__main__':
    main()
