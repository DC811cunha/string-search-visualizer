# Relatório Final - Comparação de Algoritmos de Busca em Strings

**Disciplina:** Algoritmos Avançados  
**Aplicação web desenvolvida com Python, Flask e padrão Strategy**  
**Autor:** Diego Cunha

**Objetivo:** Desenvolver uma aplicação capaz de carregar arquivos `.txt`, receber uma string de busca, executar diferentes algoritmos de busca de padrões, mostrar a execução passo a passo e comparar o desempenho prático com a complexidade teórica.

---

## 1. Visão Geral da Solução

A aplicação foi construída como uma interface web com backend em Flask. O usuário pode enviar um ou mais arquivos `.txt`, informar o padrão a ser pesquisado, escolher um algoritmo específico ou comparar todos os algoritmos, além de visualizar a execução passo a passo. Durante o processamento, a solução apresenta tempo médio de execução, número de comparações, tamanho do texto e do padrão e as estruturas auxiliares relevantes de cada algoritmo.

### Arquitetura Adotada

- Padrão **Strategy** para encapsular os algoritmos e permitir troca dinâmica em tempo de execução.
- Rotas **Flask** separadas para upload, busca, passo a passo, comparação e listagem de algoritmos.
- Frontend em **HTML, CSS e JavaScript** para visualização de resultados e animação da execução passo a passo.
- **Testes automatizados** para verificar consistência entre os algoritmos e funcionamento das rotas principais.

---

## 2. Algoritmos Implementados

| Algoritmo | Ideia Principal | Complexidade Esperada |
|---|---|---|
| Naive | Compara o padrão em todas as posições possíveis do texto. | O(n × m) |
| Rabin-Karp | Usa hash para comparar janelas e só confirma quando o hash coincide. | O(n + m) médio |
| KMP | Evita recomparações com a tabela LPS (Longest Prefix Suffix). | O(n + m) |
| Boyer-Moore (Bad Character) | Compara da direita para a esquerda e usa saltos maiores. | Melhor caso sublinear |

No passo a passo, a aplicação mostra índices comparados, total de comparações, deslocamento do padrão e estruturas auxiliares:

- **KMP** — exibe a tabela LPS.
- **Boyer-Moore** — exibe a tabela Bad Character.
- **Rabin-Karp** — mostra o hash da janela e o hash do padrão.

---

## 3. Critérios de Medição

Para reduzir o ruído natural da medição de tempo em Python, cada busca é executada várias vezes e a aplicação utiliza o **tempo médio em nanossegundos**. Além do tempo real, também são apresentados o melhor tempo, o pior tempo, a quantidade de comparações realizadas, o tamanho do texto e o tamanho do padrão. Esse procedimento torna a comparação mais justa e aproxima a análise prática do comportamento esperado na teoria.

---

## 4. Resultados Experimentais

| Cenário | Algoritmo | Tempo Médio (ms) | Comparações | Ocorrências |
|---|---|---|---|---|
| Cenário A — texto curto com repetições | Naive (Força Bruta) | 0,1711 | 1437 | 240 |
| Cenário A — texto curto com repetições | Rabin-Karp | 0,2747 | 720 | 240 |
| Cenário A — texto curto com repetições | Knuth-Morris-Pratt (KMP) | 0,1248 | 960 | 240 |
| Cenário A — texto curto com repetições | Boyer-Moore (Bad Character) | 0,1501 | 840 | 240 |
| Cenário B — texto médio com padrão textual | Naive (Força Bruta) | 1,3117 | 10995 | 220 |
| Cenário B — texto médio com padrão textual | Rabin-Karp | 3,0721 | 1100 | 220 |
| Cenário B — texto médio com padrão textual | Knuth-Morris-Pratt (KMP) | 1,1102 | 9900 | 220 |
| Cenário B — texto médio com padrão textual | Boyer-Moore (Bad Character) | 0,8484 | 4620 | 220 |
| Cenário C — texto grande com padrão raro | Naive (Força Bruta) | 1,6071 | 13510 | 1 |
| Cenário C — texto grande com padrão raro | Rabin-Karp | 4,3015 | 7 | 1 |
| Cenário C — texto grande com padrão raro | Knuth-Morris-Pratt (KMP) | 1,3876 | 13510 | 1 |
| Cenário C — texto grande com padrão raro | Boyer-Moore (Bad Character) | 0,6639 | 2706 | 1 |

Os resultados mostram que a teoria se confirma na prática: algoritmos com uso de estruturas auxiliares ou heurísticas tendem a reduzir o volume de comparações. O Naive se mantém competitivo em casos pequenos, mas perde eficiência quando o texto cresce ou quando existem muitas recomparações. O KMP apresenta comportamento estável, enquanto o Boyer-Moore se beneficia principalmente de padrões maiores e alfabetos mais variados. O Rabin-Karp se destaca quando o hash ajuda a descartar rapidamente janelas não candidatas.

---

## 5. Discussão: Quando Cada Algoritmo é Mais Eficiente

### Naive
Adequado para fins didáticos, entradas pequenas e situações em que simplicidade de implementação é prioridade.

### Rabin-Karp
Vantajoso quando o uso de hashing ajuda a eliminar grande parte das janelas rapidamente ou quando se pensa em extensões para múltiplos padrões.

### KMP
Especialmente eficiente quando o padrão possui repetições internas, pois a tabela LPS evita voltar no texto e elimina trabalho redundante.

### Boyer-Moore
Tende a ser muito forte em textos longos, principalmente porque compara da direita para a esquerda e pode aplicar saltos maiores que um caractere.

---

## 6. Atendimento ao Enunciado

- Upload de um ou vários arquivos `.txt`.
- Campo de entrada para a string de busca.
- Quatro algoritmos obrigatórios implementados.
- Execução normal e execução passo a passo.
- Exibição de índices comparados, comparações, deslocamentos e estruturas auxiliares.
- Tempo de execução, número de comparações, tamanho do texto e tamanho do padrão.
- Comparação entre tempo real e complexidade teórica.
- Uso do padrão Strategy, conforme exigido.

---

## 7. Conclusão

A atividade foi concluída com uma solução completa, funcional e alinhada aos requisitos propostos. O projeto não apenas executa os algoritmos, mas também os transforma em uma experiência visual e analítica, permitindo observar como cada estratégia se comporta em cenários diferentes. Com isso, o trabalho atende à parte prática da disciplina e também contribui para o entendimento conceitual de complexidade, otimização e escolha de algoritmo adequada ao problema.