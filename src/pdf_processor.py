"""Safe PDF text extraction and cleanup."""

from dataclasses import dataclass
from io import BytesIO
import re
from typing import BinaryIO

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError


@dataclass(frozen=True)
class PDFReport:
    filename: str
    page_count: int
    text: str
    warnings: tuple[str, ...] = ()

    @property
    def has_readable_text(self) -> bool:
        return bool(self.text.strip())


class PDFProcessingError(ValueError):
    """Raised when an uploaded file cannot be processed as a PDF."""


def clean_text(text: str) -> str:
    """Normalize PDF extraction artifacts while retaining technical symbols."""
    text = text.replace("\x00", " ").replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Join words split by a PDF line-wrap hyphen, while leaving ordinary hyphens.
    text = re.sub(r"(?<=[A-Za-z])[-\u2010]\s*\n\s*(?=[a-z])", "", text)
    text = re.sub(r"[\t\f\v ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(file: bytes | bytearray | BinaryIO, filename: str = "report.pdf",
                max_bytes: int = 25 * 1024 * 1024) -> PDFReport:
    """Extract text, reporting empty/scanned documents without throwing."""
    if hasattr(file, "getvalue"):
        data = file.getvalue()  # Streamlit UploadedFile
    elif isinstance(file, (bytes, bytearray)):
        data = bytes(file)
    else:
        data = file.read()
    if not data:
        raise PDFProcessingError("The uploaded file is empty.")
    if len(data) > max_bytes:
        raise PDFProcessingError(f"The PDF is larger than the {max_bytes // (1024 * 1024)} MB upload limit.")
    try:
        reader = PdfReader(BytesIO(data), strict=False)
        if reader.is_encrypted:
            try:
                if reader.decrypt("") == 0:
                    raise PDFProcessingError("This PDF is password-protected. Upload an unlocked copy.")
            except PdfProcessingError:
                raise
            except Exception as exc:
                raise PDFProcessingError("This PDF is password-protected. Upload an unlocked copy.") from exc
        pages = list(reader.pages)
        if not pages:
            raise PDFProcessingError("This PDF contains no pages.")
        chunks: list[str] = []
        for page in pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                chunks.append("")
        text = clean_text("\n\n".join(chunks))
        warnings = () if text else (
            "No selectable text was found. This may be a scanned PDF; run OCR on it and upload the searchable PDF.",
        )
        return PDFReport(filename=filename, page_count=len(pages), text=text, warnings=warnings)
    except PDFProcessingError:
        raise
    except (PdfReadError, OSError, ValueError, TypeError) as exc:
        raise PDFProcessingError("The PDF could not be read. Check that it is a valid, uncorrupted PDF.") from exc
    except Exception as exc:
        raise PDFProcessingError("Text extraction failed for this PDF. Try exporting it again as a searchable PDF.") from exc

