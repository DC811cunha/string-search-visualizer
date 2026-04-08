# 🔎 String Search Visualizer

Aplicação interativa para visualização e comparação de algoritmos de busca em strings, com análise de desempenho e execução passo a passo.

---

## 🚀 Destaques do Projeto

- ✔️ Implementação de 4 algoritmos clássicos
- ✔️ Arquitetura com padrão Strategy
- ✔️ Execução passo a passo (debug visual)
- ✔️ Comparação entre tempo real vs complexidade teórica
- ✔️ Interface web interativa
- ✔️ Testes automatizados
- ✔️ Geração de relatório em PDF

---

## 📌 Problema Resolvido

Este projeto resolve um problema comum no ensino de algoritmos:

> _"Entender como algoritmos funcionam internamente e como eles se comportam na prática."_

A solução permite:

- Visualizar comparações em tempo real
- Entender deslocamentos do padrão
- Analisar eficiência prática

---

## 🧠 Algoritmos Implementados

| Algoritmo   | Estratégia             | Complexidade          |
|-------------|------------------------|-----------------------|
| Naive        | Força bruta            | O(n × m)              |
| Rabin-Karp  | Hashing                | O(n + m) (médio)      |
| KMP         | Prefixo/Sufixo (LPS)   | O(n + m)              |
| Boyer-Moore | Bad Character          | O(n / m) (melhor caso)|

---

## ⚙️ Funcionalidades

### 📂 Entrada

- Upload de múltiplos arquivos `.txt`
- Input de padrão de busca
- Seleção dinâmica de algoritmo

### 🔍 Execução

- Execução normal
- Execução passo a passo

### 📊 Visualização

- Índices comparados
- Comparações realizadas
- Movimentação do padrão
- Estruturas auxiliares (LPS, tabela de saltos)

### 📈 Métricas

- ⏱ Tempo de execução (ns)
- 🔁 Número de comparações
- 📏 Tamanho do texto
- 🔎 Tamanho do padrão

---

## 🏗 Arquitetura

```text
SearchStrategy
 ├── NaiveSearch
 ├── RabinKarpSearch
 ├── KMPSearch
 └── BoyerMooreSearch
```

**Stack utilizada:**

- Python + Flask
- HTML / CSS / JavaScript
- ReportLab (PDF)

---

## 🧪 Testes

```bash
python -m unittest discover -s tests -v
```

✔️ Cobertura dos principais cenários:

- Múltiplas ocorrências
- Padrão inexistente
- Edge cases
- Consistência entre algoritmos

---

## ▶️ Execução

```bash
pip install -r requirements.txt
python app.py
```

Acesse:

```
http://localhost:5000
```

---

## 📄 Relatório

Incluído no projeto:

- Análise comparativa
- Explicação dos algoritmos
- Discussão de eficiência

---

## 🎯 Insights Técnicos

- **KMP** evita recomparações com LPS
- **Rabin-Karp** depende de colisões de hash
- **Boyer-Moore** se destaca com padrões maiores
- **Naive** é simples, mas ineficiente em larga escala

---

## 👨‍💻 Autor

**Diego Cunha**  
Engenharia de Software

---

## 📌 Observações

- Boyer-Moore implementado com heurística Bad Character
- Métricas padronizadas para comparação justa
- Projeto preparado para extensão (novos algoritmos)