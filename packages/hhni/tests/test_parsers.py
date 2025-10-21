# goals: [KR-2.2, KR-2.3, KR-3.1]
from __future__ import annotations

from hhni.parsers import parse_paragraphs, parse_sentences


def test_parse_paragraphs_mixed_newlines() -> None:
    text = "Paragraph one.\r\n\r\nParagraph two.\n\nParagraph three."
    result = parse_paragraphs(text)
    assert result == ["Paragraph one.", "Paragraph two.", "Paragraph three."]


def test_parse_paragraphs_empty_input() -> None:
    assert parse_paragraphs("\n\n\n") == []


def test_parse_sentences_basic() -> None:
    paragraph = "Hello world. This is HHNI! Are we ready? Yes."
    result = parse_sentences(paragraph)
    assert result == ["Hello world.", "This is HHNI!", "Are we ready?", "Yes."]


def test_parse_sentences_handles_whitespace() -> None:
    paragraph = "   Leading space.  And more   spaces!   "
    result = parse_sentences(paragraph)
    assert result == ["Leading space.", "And more   spaces!"]
