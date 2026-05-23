"""Tests for document parsing utilities."""
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import parser as doc_parser


def test_clean_strips_excess_whitespace():
    raw = "Hello   world\n\n\n\nFoo bar"
    result = doc_parser._clean(raw)
    assert "   " not in result
    assert result.count("\n\n\n") == 0


def test_parse_text_returns_cleaned_string():
    raw = "  Software Engineer   \n\n\n  Python, SQL  "
    result = doc_parser.parse_text(raw)
    assert "Software Engineer" in result
    assert "Python" in result


def test_parse_pdf_extracts_text():
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Senior Python Developer\n5+ years required"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader

    with patch.dict("sys.modules", {"pypdf": mock_pypdf}):
        result = doc_parser.parse_pdf(b"fake-pdf-bytes")

    assert "Senior Python Developer" in result
    assert "5+ years required" in result


def test_parse_docx_extracts_text():
    mock_para1 = MagicMock()
    mock_para1.text = "Software Engineer"
    mock_para2 = MagicMock()
    mock_para2.text = "Python and SQL required"
    mock_doc = MagicMock()
    mock_doc.paragraphs = [mock_para1, mock_para2]

    mock_docx = MagicMock()
    mock_docx.Document.return_value = mock_doc

    with patch.dict("sys.modules", {"docx": mock_docx}):
        result = doc_parser.parse_docx(b"fake-docx-bytes")

    assert "Software Engineer" in result
    assert "Python and SQL required" in result


def test_parse_pdf_handles_empty_pages():
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader

    with patch.dict("sys.modules", {"pypdf": mock_pypdf}):
        result = doc_parser.parse_pdf(b"fake-pdf-bytes")

    assert result == ""
