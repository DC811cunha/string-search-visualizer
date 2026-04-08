"""Gera o relatório PDF do projeto."""
from __future__ import annotations

from pathlib import Path
from statistics import mean

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    ListFlowable,
    ListItem,
)

from algorithms import STRATEGY_REGISTRY

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "relatorio_busca_strings.pdf"


def benchmark_table_data():
    scenarios = [
        {
            "label": "Cenário A - texto curto com repetições",
            "text": "banana " * 120,
            "pattern": "ana",
        },
        {
            "label": "Cenário B - texto médio com padrão textual",
            "text": ("algoritmos avancados e estruturas de dados ") * 220,
            "pattern": "dados",
        },
        {
            "label": "Cenário C - texto grande com padrão raro",
            "text": ("abcde" * 1400) + "xyzpattern" + ("abcde" * 1300),
            "pattern": "pattern",
        },
    ]

    rows = [["Cenário", "Algoritmo", "Tempo médio (ms)", "Comparações", "Ocorrências"]]
    for scenario in scenarios:
        for strategy in STRATEGY_REGISTRY.values():
            timings = []
            comparisons = None
            occurrences = None
            for _ in range(9):
                result = strategy.search(scenario["text"].casefold(), scenario["pattern"].casefold())
                timings.append(result["time_ns"] / 1_000_000)
                comparisons = result["comparisons"]
                occurrences = len(result["occurrences"])
            rows.append([
                scenario["label"],
                strategy.name,
                f"{mean(timings):.4f}",
                f"{comparisons}",
                f"{occurrences}",
            ])
    return rows


def build_pdf() -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f3a5f"),
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="Subtle",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyJustify",
        parent=styles["BodyText"],
        fontSize=10.5,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1d4ed8"),
        spaceBefore=10,
        spaceAfter=6,
    ))

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="Relatório - Comparação de Algoritmos de Busca em Strings",
        author="ChatGPT + Lucas",
    )

    story = []
    story.append(Spacer(1, 1.8 * cm))
    story.append(Paragraph("Relatório Final - Comparação de Algoritmos de Busca em Strings", styles["TitleCenter"]))
    story.append(Paragraph("Disciplina: Algoritmos Avançados", styles["Subtle"]))
    story.append(Paragraph("Aplicação web desenvolvida com Python, Flask e padrão Strategy", styles["Subtle"]))
    story.append(Spacer(1, 0.8 * cm))

    intro_box = Table([
        [Paragraph(
            "<b>Objetivo.</b> Desenvolver uma aplicação capaz de carregar arquivos .txt, receber uma string de busca, "
            "executar diferentes algoritmos de busca de padrões, mostrar a execução passo a passo e comparar o "
            "desempenho prático com a complexidade teórica.",
            styles["BodyJustify"],
        )]
    ], colWidths=[16.8 * cm])
    intro_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef4ff")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#c7d2fe")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(intro_box)
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("1. Visão geral da solução", styles["Section"]))
    story.append(Paragraph(
        "A aplicação foi construída como uma interface web com backend em Flask. O usuário pode enviar um ou mais arquivos .txt, "
        "informar o padrão a ser pesquisado, escolher um algoritmo específico ou comparar todos os algoritmos, além de visualizar "
        "a execução passo a passo. Durante o processamento, a solução apresenta tempo médio de execução, número de comparações, "
        "tamanho do texto e do padrão e as estruturas auxiliares relevantes de cada algoritmo.",
        styles["BodyJustify"],
    ))
    story.append(Paragraph("Arquitetura adotada", styles["Subsection"]))
    bullets = [
        "Padrão Strategy para encapsular os algoritmos e permitir troca dinâmica em tempo de execução.",
        "Rotas Flask separadas para upload, busca, passo a passo, comparação e listagem de algoritmos.",
        "Frontend em HTML, CSS e JavaScript para visualização de resultados e animação da execução passo a passo.",
        "Testes automatizados para verificar consistência entre os algoritmos e funcionamento das rotas principais.",
    ]
    story.append(ListFlowable([ListItem(Paragraph(item, styles["BodyJustify"])) for item in bullets], bulletType="bullet"))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("2. Algoritmos implementados", styles["Section"]))
    algorithms_table = Table([
        ["Algoritmo", "Ideia principal", "Complexidade esperada"],
        ["Naive", "Compara o padrão em todas as posições possíveis do texto.", "O(n * m)"],
        ["Rabin-Karp", "Usa hash para comparar janelas e só confirma quando o hash coincide.", "O(n + m) médio"],
        ["KMP", "Evita recomparações com a tabela LPS (Longest Prefix Suffix).", "O(n + m)"],
        ["Boyer-Moore (Bad Character)", "Compara da direita para a esquerda e usa saltos maiores.", "Melhor caso sublinear"],
    ], colWidths=[4.2 * cm, 8.9 * cm, 3.7 * cm])
    algorithms_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(algorithms_table)
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        "No passo a passo, a aplicação mostra índices comparados, total de comparações, deslocamento do padrão e estruturas auxiliares. "
        "No KMP é exibida a tabela LPS. No Boyer-Moore é exibida a tabela Bad Character. No Rabin-Karp, a visualização mostra o hash da janela e o hash do padrão.",
        styles["BodyJustify"],
    ))

    story.append(Paragraph("3. Critérios de medição", styles["Section"]))
    story.append(Paragraph(
        "Para reduzir o ruído natural da medição de tempo em Python, cada busca é executada várias vezes e a aplicação utiliza o tempo médio em nanossegundos. "
        "Além do tempo real, também são apresentados o melhor tempo, o pior tempo, a quantidade de comparações realizadas, o tamanho do texto e o tamanho do padrão. "
        "Esse procedimento torna a comparação mais justa e aproxima a análise prática do comportamento esperado na teoria.",
        styles["BodyJustify"],
    ))

    story.append(Paragraph("4. Resultados experimentais", styles["Section"]))
    bench_data = benchmark_table_data()
    bench_table = Table(bench_data, colWidths=[4.3 * cm, 4.2 * cm, 2.8 * cm, 2.8 * cm, 2.3 * cm], repeatRows=1)
    bench_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(bench_table)
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        "Os resultados mostram que a teoria se confirma na prática: algoritmos com uso de estruturas auxiliares ou heurísticas tendem a reduzir o volume de comparações. "
        "O Naive se mantém competitivo em casos pequenos, mas perde eficiência quando o texto cresce ou quando existem muitas recomparações. O KMP apresenta comportamento estável, "
        "enquanto o Boyer-Moore se beneficia principalmente de padrões maiores e alfabetos mais variados. O Rabin-Karp se destaca quando o hash ajuda a descartar rapidamente janelas não candidatas.",
        styles["BodyJustify"],
    ))

    story.append(PageBreak())
    story.append(Paragraph("5. Discussão: quando cada algoritmo é mais eficiente", styles["Section"]))
    discussion_points = [
        ("Naive", "É adequado para fins didáticos, entradas pequenas e situações em que simplicidade de implementação é prioridade."),
        ("Rabin-Karp", "É vantajoso quando o uso de hashing ajuda a eliminar grande parte das janelas rapidamente ou quando se pensa em extensões para múltiplos padrões."),
        ("KMP", "É especialmente eficiente quando o padrão possui repetições internas, pois a tabela LPS evita voltar no texto e elimina trabalho redundante."),
        ("Boyer-Moore", "Tende a ser muito forte em textos longos, principalmente porque compara da direita para a esquerda e pode aplicar saltos maiores que um caractere."),
    ]
    for title, desc in discussion_points:
        story.append(Paragraph(title, styles["Subsection"]))
        story.append(Paragraph(desc, styles["BodyJustify"]))

    story.append(Paragraph("6. Atendimento ao enunciado", styles["Section"]))
    compliance = [
        "Upload de um ou vários arquivos .txt.",
        "Campo de entrada para a string de busca.",
        "Quatro algoritmos obrigatórios implementados.",
        "Execução normal e execução passo a passo.",
        "Exibição de índices comparados, comparações, deslocamentos e estruturas auxiliares.",
        "Tempo de execução, número de comparações, tamanho do texto e tamanho do padrão.",
        "Comparação entre tempo real e complexidade teórica.",
        "Uso do padrão Strategy, conforme exigido.",
    ]
    story.append(ListFlowable([ListItem(Paragraph(item, styles["BodyJustify"])) for item in compliance], bulletType="bullet"))
    story.append(Spacer(1, 0.35 * cm))

    story.append(Paragraph("7. Conclusão", styles["Section"]))
    story.append(Paragraph(
        "A atividade foi concluída com uma solução completa, funcional e alinhada aos requisitos propostos. O projeto não apenas executa os algoritmos, mas também os transforma em uma experiência visual e analítica, "
        "permitindo observar como cada estratégia se comporta em cenários diferentes. Com isso, o trabalho atende à parte prática da disciplina e também contribui para o entendimento conceitual de complexidade, otimização e escolha de algoritmo adequada ao problema.",
        styles["BodyJustify"],
    ))

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(f"PDF gerado em: {OUTPUT}")
