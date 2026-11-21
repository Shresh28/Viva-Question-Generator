"""Plain-text and PDF downloads for validated question sets."""

from io import BytesIO
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from xml.sax.saxutils import escape


def format_txt(result: dict) -> str:
    info = result["project_info"]
    lines = ["VivaPrep AI — Viva Questions", "=" * 40, f"Project: {info['title']}",
             f"Domain: {info['domain']}", f"Objective: {info['objective']}",
             f"Technologies: {', '.join(info['technologies']) or 'Not specified'}", ""]
    for level in ("Easy", "Medium", "Hard"):
        lines.append(f"{level.upper()} QUESTIONS")
        lines.append("-" * 40)
        items = [q for q in result["questions"] if q["difficulty"] == level]
        for number, item in enumerate(items, 1):
            lines += [f"{number}. {item['question']}", f"Answer: {item['answer']}", ""]
    return "\n".join(lines).rstrip() + "\n"


def _pdf_safe(value: str) -> str:
    # Helvetica is built into PDF readers but supports only Latin-1. Keep exports robust
    # without bundling a font; unsupported glyphs become a readable replacement.
    return value.encode("latin-1", errors="replace").decode("latin-1")


def make_pdf(result: dict) -> bytes:
    buffer = BytesIO()
    page_w, page_h = letter
    pdf = canvas.Canvas(buffer, pagesize=letter)
    left, right = 0.72 * inch, page_w - 0.72 * inch
    y = page_h - 0.75 * inch

    def ensure(height: float = 18) -> None:
        nonlocal y
        if y - height < 0.7 * inch:
            pdf.showPage()
            y = page_h - 0.75 * inch

    def wrapped(text: str, *, font: str = "Helvetica", size: float = 10,
                leading: float = 14, color=colors.HexColor("#243248")) -> None:
        nonlocal y
        text = _pdf_safe(text)
        words = text.split()
        line = ""
        pdf.setFont(font, size)
        pdf.setFillColor(color)
        for word in words:
            trial = f"{line} {word}".strip()
            if line and stringWidth(trial, font, size) > right - left:
                ensure(leading)
                pdf.drawString(left, y, line)
                y -= leading
                line = word
            else:
                line = trial
        if line:
            ensure(leading)
            pdf.drawString(left, y, line)
            y -= leading

    info = result["project_info"]
    pdf.setFillColor(colors.HexColor("#126E67"))
    pdf.roundRect(left, y - 42, right - left, 50, 8, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(left + 14, y - 11, "VivaPrep AI")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(left + 14, y - 29, "Project viva question set")
    y -= 68
    wrapped(f"Project: {info['title']}", font="Helvetica-Bold", size=12, leading=18)
    wrapped(f"Domain: {info['domain']}")
    wrapped(f"Objective: {info['objective']}")
    wrapped(f"Technologies: {', '.join(info['technologies']) or 'Not specified'}")
    y -= 12
    for level in ("Easy", "Medium", "Hard"):
        ensure(30)
        pdf.setFillColor(colors.HexColor("#126E67"))
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(left, y, f"{level} — 5 questions")
        y -= 23
        items = [q for q in result["questions"] if q["difficulty"] == level]
        for index, item in enumerate(items, 1):
            wrapped(f"{index}. {item['question']}", font="Helvetica-Bold", size=10, leading=15)
            wrapped(f"Answer: {item['answer']}", size=9.5, leading=14, color=colors.HexColor("#526176"))
            y -= 8
    pdf.save()
    return buffer.getvalue()

