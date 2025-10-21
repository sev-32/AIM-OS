from __future__ import annotations

import json
from pathlib import Path

from packages.doc_builder.generator import DocumentBuildResult, generate_document


def test_generate_document_creates_markdown(tmp_path: Path) -> None:
    seed_path = Path('Testing/samples/document_seed_sample.json').resolve()
    assert seed_path.exists(), "Sample seed missing"

    result = generate_document(seed_path, output_dir=tmp_path)
    assert isinstance(result, DocumentBuildResult)
    assert result.output_path.exists()
    text = result.output_path.read_text(encoding='utf-8')

    assert '# AIM-OS Architecture Overview' in text
    assert '## Context Memory Core (CMC)' in text
    assert 'Provenance' in text
    assert str(seed_path) in text
    assert result.word_count > 40
    assert result.section_count >= 3


def test_generate_document_with_inline_seed(tmp_path: Path) -> None:
    seed = {
        'title': 'Inline Seed Document',
        'summary': 'Generated from inline payload.',
        'sections': [
            {
                'heading': 'Section A',
                'body': 'Body content for section A.',
            }
        ],
    }
    result = generate_document(seed, output_dir=tmp_path, filename='inline-doc.md')
    text = result.output_path.read_text(encoding='utf-8')
    assert 'Inline Seed Document' in text
    assert result.output_path.name == 'inline-doc.md'
    assert '<inline seed>' in text
