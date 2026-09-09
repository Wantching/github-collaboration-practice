from pathlib import Path
import html
import re

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "GitHub协作实操手册.md"
OUTPUT = ROOT / "output" / "pdf" / "GitHub协作实操手册.pdf"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

BLUE = colors.HexColor("#0969da")
INK = colors.HexColor("#1f2328")
MUTED = colors.HexColor("#57606a")
PALE = colors.HexColor("#f6f8fa")
LINE = colors.HexColor("#d0d7de")
ORANGE = colors.HexColor("#f97316")


pdfmetrics.registerFont(TTFont("YaHei", FONT_REG))
pdfmetrics.registerFont(TTFont("YaHei-Bold", FONT_BOLD))


class ManualDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name.startswith("H"):
                level = int(style_name[1])
                text = flowable.getPlainText()
                key = f"heading-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=max(0, level - 1), closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def page_header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.line(1.8 * cm, h - 1.25 * cm, w - 1.8 * cm, h - 1.25 * cm)
        canvas.setFont("YaHei", 8.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(1.8 * cm, h - 0.95 * cm, "VS Code + GitHub 图形化协作实操手册")
        canvas.drawRightString(w - 1.8 * cm, 0.8 * cm, f"第 {doc.page - 1} 页")
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(colors.HexColor("#0d1117"))
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(0, h - 1.1 * cm, w, 1.1 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("YaHei-Bold", 28)
    canvas.drawString(2.2 * cm, h - 6.2 * cm, "VS Code + GitHub")
    canvas.setFont("YaHei-Bold", 24)
    canvas.drawString(2.2 * cm, h - 7.5 * cm, "图形化协作实操手册")
    canvas.setFillColor(colors.HexColor("#8c959f"))
    canvas.setFont("YaHei", 12)
    canvas.drawString(2.2 * cm, h - 9.1 * cm, "从第一次分支、Commit 和 Pull Request，到亲手解决合并冲突")
    canvas.setStrokeColor(colors.HexColor("#30363d"))
    canvas.line(2.2 * cm, h - 10.2 * cm, w - 2.2 * cm, h - 10.2 * cm)
    steps = ["Edit", "Stage", "Commit", "Push", "Pull Request", "Review", "Merge"]
    positions = [(2.2, 12.0), (5.0, 12.0), (8.0, 12.0), (11.2, 12.0), (2.2, 13.2), (6.7, 13.2), (10.2, 13.2)]
    for i, (step, (x_cm, y_cm)) in enumerate(zip(steps, positions)):
        x = x_cm * cm
        y = h - y_cm * cm
        canvas.setFillColor(BLUE if i < 4 else ORANGE)
        canvas.circle(x + 0.32 * cm, y, 0.18 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#c9d1d9"))
        canvas.setFont("YaHei", 9.5)
        canvas.drawString(x + 0.62 * cm, y - 0.12 * cm, step)
        x += 2.15 * cm
    canvas.setFillColor(colors.HexColor("#8c959f"))
    canvas.setFont("YaHei", 10)
    canvas.drawString(2.2 * cm, 3.0 * cm, "练习仓库：github.com/Wantching/github-collaboration-practice")
    canvas.drawString(2.2 * cm, 2.3 * cm, "生成日期：2026-09-09 · 面向 Markdown 文档协作初学者")
    canvas.restoreState()


def page_decorations(canvas, doc):
    if doc.page == 1:
        cover(canvas, doc)
    else:
        page_header_footer(canvas, doc)


styles = getSampleStyleSheet()
BASE = ParagraphStyle("BodyCN", fontName="YaHei", fontSize=10.2, leading=17, textColor=INK, spaceAfter=7)
H1 = ParagraphStyle("H1", parent=BASE, fontName="YaHei-Bold", fontSize=20, leading=27, textColor=INK, spaceBefore=14, spaceAfter=10, keepWithNext=True)
H2 = ParagraphStyle("H2", parent=BASE, fontName="YaHei-Bold", fontSize=15, leading=21, textColor=BLUE, spaceBefore=12, spaceAfter=7, keepWithNext=True)
H3 = ParagraphStyle("H3", parent=BASE, fontName="YaHei-Bold", fontSize=12, leading=18, textColor=INK, spaceBefore=9, spaceAfter=5, keepWithNext=True)
TOC_TITLE = ParagraphStyle("TOCTitle", parent=H1)
BULLET = ParagraphStyle("BulletCN", parent=BASE, leftIndent=16, firstLineIndent=-10, bulletIndent=4, spaceAfter=4)
QUOTE = ParagraphStyle("QuoteCN", parent=BASE, leftIndent=15, rightIndent=10, borderColor=BLUE, borderWidth=0, borderPadding=7, backColor=colors.HexColor("#ddf4ff"), textColor=INK)
CAPTION = ParagraphStyle("Caption", parent=BASE, fontSize=8.5, leading=13, textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=9)
CODE = ParagraphStyle("CodeCN", parent=BASE, fontName="YaHei", fontSize=8.5, leading=13, leftIndent=4, rightIndent=4, textColor=colors.HexColor("#24292f"))


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r'<font color="#0550ae">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#0969da">\1</link>', text)
    return text


def image_flow(alt, rel):
    path = ROOT / rel
    with PILImage.open(path) as im:
        iw, ih = im.size
    max_w, max_h = 17.1 * cm, 12.2 * cm
    scale = min(max_w / iw, max_h / ih)
    pic = Image(str(path), width=iw * scale, height=ih * scale)
    return KeepTogether([pic, Paragraph(inline(f"图：{alt}"), CAPTION)])


def code_flow(lines):
    content = "<br/>".join(html.escape(x).replace(" ", "&nbsp;") or "&nbsp;" for x in lines)
    cell = Paragraph(content, CODE)
    table = Table([[cell]], colWidths=[17.1 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def table_flow(rows):
    cols = max(len(r) for r in rows)
    data = []
    for row in rows:
        padded = row + [""] * (cols - len(row))
        data.append([Paragraph(inline(cell.strip()), ParagraphStyle("TableCell", parent=BASE, fontSize=8.2, leading=12)) for cell in padded])
    widths = [17.1 * cm / cols] * cols
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ddf4ff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("FONTNAME", (0, 0), (-1, 0), "YaHei-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def parse_markdown(text):
    lines = text.splitlines()
    story = [Spacer(1, 1), PageBreak()]
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC1", fontName="YaHei-Bold", fontSize=11, leading=17, leftIndent=0, textColor=INK, spaceBefore=5),
        ParagraphStyle("TOC2", fontName="YaHei", fontSize=9.5, leading=15, leftIndent=15, textColor=MUTED),
        ParagraphStyle("TOC3", fontName="YaHei", fontSize=8.5, leading=13, leftIndent=30, textColor=MUTED),
    ]
    story.extend([Paragraph("目录", TOC_TITLE), toc, PageBreak()])
    i = 1  # skip document title, already represented by cover
    paragraph = []

    def flush_para():
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline(" ".join(x.strip() for x in paragraph)), BASE))
            paragraph = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_para()
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            story.extend([code_flow(block), Spacer(1, 7)])
        elif stripped.startswith("!["):
            flush_para()
            match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
            if match:
                story.append(image_flow(match.group(1), match.group(2)))
        elif stripped.startswith("# "):
            flush_para()
        elif stripped.startswith("## "):
            flush_para()
            story.append(Paragraph(inline(stripped[3:]), H1))
        elif stripped.startswith("### "):
            flush_para()
            story.append(Paragraph(inline(stripped[4:]), H2))
        elif stripped.startswith("#### "):
            flush_para()
            story.append(Paragraph(inline(stripped[5:]), H3))
        elif stripped == "---":
            flush_para()
            story.append(Spacer(1, 6))
        elif stripped.startswith("> "):
            flush_para()
            story.append(Paragraph(inline(stripped[2:]), QUOTE))
        elif stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i + 1]):
            flush_para()
            rows = [[c.strip() for c in stripped.strip("|").split("|")]]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            story.extend([table_flow(rows), Spacer(1, 8)])
            continue
        elif re.match(r"^- \[[ xX]\] ", stripped):
            flush_para()
            mark = "☑" if stripped[3].lower() == "x" else "☐"
            story.append(Paragraph(inline(stripped[6:]), BULLET, bulletText=mark))
        elif re.match(r"^[-*] ", stripped):
            flush_para()
            story.append(Paragraph(inline(stripped[2:]), BULLET, bulletText="•"))
        elif re.match(r"^\d+\. ", stripped):
            flush_para()
            num, body = stripped.split(". ", 1)
            story.append(Paragraph(inline(body), BULLET, bulletText=f"{num}."))
        elif not stripped:
            flush_para()
            story.append(Spacer(1, 3))
        else:
            paragraph.append(line)
        i += 1
    flush_para()
    return story


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    frame = Frame(1.8 * cm, 1.25 * cm, page_w - 3.6 * cm, page_h - 2.8 * cm, id="body")
    doc = ManualDoc(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.25 * cm,
        title="VS Code + GitHub 图形化协作实操手册",
        author="Wantching",
    )
    doc.addPageTemplates([
        PageTemplate(id="all", frames=[frame], onPage=page_decorations),
    ])
    story = parse_markdown(SOURCE.read_text(encoding="utf-8"))
    doc.multiBuild(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
