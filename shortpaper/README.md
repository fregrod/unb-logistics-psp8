# Short Paper Acadêmico — MVP Logística & SAD (PSP8 / UnB)

Este diretório contém o **artigo científico (Short Paper)** derivado do MVP de Sistemas de Apoio à Decisão Logística no E-Commerce Brasileiro. O artigo segue a estrutura clássica de publicações científicas de Engenharia de Produção e Ciência da Computação (duas colunas, formatação A4, equações matemáticas, tabelas formais e citações via BibTeX).

---

## 📄 Informações do Artigo

* **Título:** *Sistema de Apoio à Decisão para Otimização Logística no E-Commerce Brasileiro: Diagnóstico de Lead Time, Custos de Frete e Nível de Serviço*
* **Título em Inglês:** *A Decision Support System for Logistics Optimization in Brazilian E-Commerce: Lead Time Diagnosis, Freight Burden, and Service Level Assessment*
* **Autores:** Rodrigo Fregonasse e André Luiz Marques Serrano
* **Instituição:** Departamento de Engenharia de Produção — Faculdade de Tecnologia — Universidade de Brasília (UnB)
* **Extensão:** 6 páginas (formato padrão de *short paper* em conferências)

---

## 🏛️ Estrutura do Artigo

1. **Cabeçalho:** Título em Português e Inglês, Autores, Filiação Institucional e Contatos.
2. **Resumo e Abstract:** Síntese executiva com palavras-chave e *keywords*.
3. **1. Introdução:** Contextualização do *last-mile*, gargalos logísticos no Brasil, formulação prévia das 5 perguntas de negócio e estrutura do trabalho.
4. **2. Fundamentação Teórica:** Metodologia KDD, Arquitetura Lakehouse (Delta Lake / ACID), Modelagem Dimensional de Ralph Kimball (Esquema Estrela) e Gestão de Nível de Serviço (CSAT e Detratores).
5. **3. Materiais e Métodos:** Base de dados Olist ($96.470$ pedidos entregues auditados), conformidade com a LGPD, auditoria em 6 dimensões de qualidade de dados (AED), arquitetura dimensional e ambiente Databricks.
6. **4. Resultados Empíricos e Discussão:** Resolução das 5 perguntas com tabelas profissionais (`booktabs`), gráficos estatísticos e análises críticas:
   * **P1:** Disparidade regional Norte/Nordeste vs. Sul/Sudeste (taxa de atraso de $14,33\%$ no Nordeste).
   * **P2:** *Burden* de frete vs. satisfação (dobro de detratores quando frete $>$ produto).
   * **P3:** Efeito da cubagem e carga pesada (móveis e eletrônicos).
   * **P4:** Complexidade da rota (atrasos severos dobram em divisas interestaduais).
   * **P5:** Impacto destrutivo do atraso no CSAT ($5,8\times$ mais detratores) e modelo de sensibilidade ($50\%$ de redução).
7. **5. Implicações para a Tomada de Decisão:** Recomendações prescritivas de Engenharia de Produção (descentralização de estoques no Nordeste, SLAs por cubagem, subsídios estratégicos e alerta preditivo no checkout).
8. **6. Autoavaliação do MVP e Trabalhos Futuros:** Validação da tríade técnica, financeira e de desejabilidade; limitações dos dados e evolução com ML supervisionado.
9. **7. Conclusão:** Fechamento e impacto para o comércio eletrônico nacional.
10. **Agradecimentos & Referências Bibliográficas:** Citações canônicas em BibTeX (Kimball, Fayyad, Chopra, Christopher, Reichheld, Ballou, Novaes, etc.).

---

## 📂 Arquivos no Diretório

```text
shortpaper/
├── main.tex           <- Código-fonte principal em LaTeX
├── referencias.bib    <- Base de dados bibliográfica em BibTeX
├── compile.sh         <- Script de compilação em 1 clique
├── Makefile           <- Automação para comando make / make clean / make view
├── main.pdf           <- PDF final compilado (6 páginas)
├── apresentacao_mvp_sad.pptx <- Apresentação de slides minimalista (13 slides 16:9)
├── figuras/           <- Imagens e gráficos em alta resolução incorporados no artigo
└── README.md          <- Este guia de documentação
```

---

## 🚀 Como Compilar

### Opção 1: Via Script Shell (Mais Fácil)
No terminal, dentro da pasta do projeto:
```bash
cd shortpaper
./compile.sh
```

### Opção 2: Via Makefile
```bash
cd shortpaper
make        # Compila o PDF completo com referências
make view   # Abre o PDF gerado
make clean  # Limpa arquivos auxiliares (.aux, .bbl, etc.)
```

### Opção 3: No Overleaf
Se desejar editar no [Overleaf](https://www.overleaf.com):
1. Compacte a pasta `shortpaper` em um arquivo `.zip`.
2. Acesse o Overleaf, clique em **New Project** $\rightarrow$ **Upload Project** e submeta o arquivo `.zip`.
3. Defina `main.tex` como arquivo principal e compile diretamente no navegador.
