"""
Gera um relatório em PDF com os dados de estoque salvos no Google Sheets.

Pré-requisitos:
    - O arquivo .env já configurado (GOOGLE_CREDENTIALS_PATH e SPREADSHEET_ID),
      do mesmo jeito que é usado pelo main.py.
    - pip install reportlab

Uso:
    python gerar_relatorio.py

O arquivo "relatorio_estoque.pdf" será criado na mesma pasta.
"""

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from repository import GoogleSheetsRepository


NOME_ARQUIVO_SAIDA = "relatorio_estoque.pdf"


def montar_tabela_produtos(produtos, styles):
    """Monta uma tabela formatada de produtos, destacando estoque baixo em vermelho."""
    cabecalho = ["SKU", "Nome", "Categoria", "Qtd. Atual", "Nível Mín.", "Status"]
    linhas = [cabecalho]

    for p in produtos:
        status = "Ativo" if p.ativo else "Inativo"
        if p.ativo and p.verificar_estoque_baixo():
            status = "[!] Estoque baixo"
        linhas.append([
            p.sku, p.nome, p.categoria,
            str(p.quantidade), str(p.nivel_minimo), status
        ])

    tabela = Table(linhas, colWidths=[2.6*cm, 4.2*cm, 3.2*cm, 2.3*cm, 2.3*cm, 3.4*cm], repeatRows=1)

    estilo = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (3, 0), (4, -1), "CENTER"),
        ("ALIGN", (5, 0), (5, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F7")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])

    # Destaca em vermelho as linhas de produtos ativos com estoque baixo
    for idx, p in enumerate(produtos, start=1):
        if p.ativo and p.verificar_estoque_baixo():
            estilo.add("TEXTCOLOR", (0, idx), (-1, idx), colors.HexColor("#C0392B"))
            estilo.add("FONTNAME", (0, idx), (-1, idx), "Helvetica-Bold")
        if not p.ativo:
            estilo.add("TEXTCOLOR", (0, idx), (-1, idx), colors.HexColor("#909497"))

    tabela.setStyle(estilo)
    return tabela


def gerar_relatorio():
    print("⚡ Conectando ao Google Sheets...")
    repo = GoogleSheetsRepository()
    todos_produtos = repo.listar_todos()
    print(f"✅ {len(todos_produtos)} produto(s) carregado(s).")

    ativos = [p for p in todos_produtos if p.ativo]
    inativos = [p for p in todos_produtos if not p.ativo]
    estoque_baixo = [p for p in ativos if p.verificar_estoque_baixo()]

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "TituloCustom", parent=styles["Title"], textColor=colors.HexColor("#2C3E50")
    )
    subtitulo_style = ParagraphStyle(
        "SubtituloCustom", parent=styles["Normal"], textColor=colors.HexColor("#566573"), spaceAfter=12
    )
    secao_style = ParagraphStyle(
        "SecaoCustom", parent=styles["Heading2"], textColor=colors.HexColor("#2C3E50"), spaceBefore=18
    )

    doc = SimpleDocTemplate(
        NOME_ARQUIVO_SAIDA, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm, leftMargin=1.8*cm, rightMargin=1.8*cm
    )
    story = []

    # Cabeçalho
    story.append(Paragraph("Relatório de Estoque — StockFlow", titulo_style))
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    story.append(Paragraph(f"Gerado em {agora}", subtitulo_style))

    # Resumo
    resumo_dados = [
        ["Produtos ativos", str(len(ativos))],
        ["Produtos inativos", str(len(inativos))],
        ["Produtos com estoque baixo", str(len(estoque_baixo))],
    ]
    resumo_tabela = Table(resumo_dados, colWidths=[8*cm, 4*cm])
    resumo_tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2F8")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AED6F1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(resumo_tabela)

    # Alerta de estoque baixo
    if estoque_baixo:
        story.append(Paragraph("Produtos em Alerta de Estoque Baixo", secao_style))
        story.append(montar_tabela_produtos(estoque_baixo, styles))

    # Lista completa de produtos ativos
    story.append(Paragraph("Produtos Ativos", secao_style))
    if ativos:
        story.append(montar_tabela_produtos(ativos, styles))
    else:
        story.append(Paragraph("Nenhum produto ativo cadastrado.", styles["Normal"]))

    # Produtos inativos (histórico)
    if inativos:
        story.append(PageBreak())
        story.append(Paragraph("Produtos Inativos (excluídos logicamente)", secao_style))
        story.append(montar_tabela_produtos(inativos, styles))

    doc.build(story)
    print(f"📄 Relatório gerado com sucesso: {NOME_ARQUIVO_SAIDA}")


if __name__ == "__main__":
    try:
        gerar_relatorio()
    except Exception as e:
        print(f"❌ [Erro ao gerar relatório]: {e}")