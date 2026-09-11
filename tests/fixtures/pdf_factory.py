"""Helpers that generate minimal in-memory PDFs for tests."""

import base64
from collections.abc import Sequence
from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import (
    ContentStream,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)


def _font_resource() -> DictionaryObject:
    """Return a minimal Type1 Helvetica font dictionary."""
    return DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )


def _add_text_page(writer: PdfWriter, text: str) -> None:
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    stream = DecodedStreamObject()
    stream.set_data(content)
    page = writer.add_blank_page(width=612, height=792)
    page[NameObject("/Contents")] = ContentStream(stream, page)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): _font_resource()})}
    )


def _build_writer(pages_text: Sequence[str]) -> PdfWriter:
    writer = PdfWriter()
    for text in pages_text:
        _add_text_page(writer, text)
    return writer


def build_pdf_bytes(pages_text: Sequence[str]) -> bytes:
    """Build a minimal multi-page PDF, one page per string in ``pages_text``."""
    return _write(_build_writer(pages_text))


def build_encrypted_pdf_bytes(pages_text: Sequence[str]) -> bytes:
    """Build a password-protected PDF requiring a user password to open."""
    writer = _build_writer(pages_text)
    writer.encrypt(user_password="secret", owner_password="secret")
    return _write(writer)


def build_no_text_pdf_bytes() -> bytes:
    """Build a PDF whose pages have no text content stream at all."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    return _write(writer)


def _write(writer: PdfWriter) -> bytes:
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def pdf_to_base64(data: bytes) -> str:
    """Encode PDF bytes as a standard (non-urlsafe) Base64 string."""
    return base64.b64encode(data).decode("ascii")
