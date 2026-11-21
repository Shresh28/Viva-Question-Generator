from src.exporters import format_txt, make_pdf
from tests.test_output_parser import valid_data


def test_txt_export_has_sections_and_answers():
    text = format_txt(valid_data())
    assert "EASY QUESTIONS" in text
    assert "HARD QUESTIONS" in text
    assert "Answer: The report says this." in text


def test_pdf_export_is_valid_pdf_bytes():
    pdf = make_pdf(valid_data())
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000

