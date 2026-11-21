from io import BytesIO

from PyPDF2 import PdfWriter
import pytest
from reportlab.pdfgen import canvas

from src.pdf_processor import PDFProcessingError, clean_text, extract_pdf


def make_pdf(text="Sample project report with CNN model"):
    output = BytesIO()
    page = canvas.Canvas(output)
    page.drawString(50, 250, text)
    page.save()
    return output.getvalue()


def test_valid_pdf_and_page_count():
    report = extract_pdf(make_pdf(), "sample.pdf")
    assert report.page_count == 1
    assert report.filename == "sample.pdf"
    assert report.has_readable_text
    assert "CNN model" in report.text


def test_pdf_without_pages():
    writer = PdfWriter()
    output = BytesIO()
    writer.write(output)
    with pytest.raises(PDFProcessingError, match="no pages"):
        extract_pdf(output.getvalue())


def test_image_only_style_pdf_gets_ocr_recommendation():
    report = extract_pdf(make_pdf(""), "scanned.pdf")
    assert not report.has_readable_text
    assert "OCR" in report.warnings[0]


def test_empty_pdf_bytes():
    with pytest.raises(PDFProcessingError, match="empty"):
        extract_pdf(b"")


def test_invalid_pdf():
    with pytest.raises(PDFProcessingError, match="could not be read"):
        extract_pdf(b"not a pdf")


def test_oversized_pdf():
    with pytest.raises(PDFProcessingError, match="larger"):
        extract_pdf(b"%PDF" + b"x" * 50, max_bytes=10)


def test_text_cleaning_preserves_technical_symbols():
    assert clean_text("neural-\n network\t α → β\x00") == "neuralnetwork α → β"

