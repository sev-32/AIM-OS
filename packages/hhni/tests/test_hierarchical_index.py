"""Tests for the hierarchical HHNI index."""

from __future__ import annotations

import json

import pytest

from hhni.hierarchical_index import (
    HierarchicalIndex,
    IndexLevel,
)


SAMPLE_DOC = """AIM-OS Architecture

Context Memory Core (CMC)
The CMC stores every observation as an atom and enables perfect recall.

Hierarchical Hypergraph Neural Index (HHNI)
HHNI provides context retrieval with multiple zoom levels.

Vision Tensor
The vision tensor propagates policies throughout the system.

Policy-Oriented Orchestration Engine
Orchestration composes agents with policies, gates, and safeguards.
"""


def test_index_document_creates_full_hierarchy():
    index = HierarchicalIndex()

    root_id = index.index_document(SAMPLE_DOC, doc_id="aimos-architecture")

    # Root exists and is at system level
    assert root_id in index.nodes
    root = index.nodes[root_id]
    assert root.level == IndexLevel.SYSTEM
    assert root.children_ids  # has sections

    # Section nodes should exist
    section_nodes = index.zoom_in(root_id)
    assert section_nodes
    assert all(node.level == IndexLevel.SECTION for node in section_nodes)

    # Paragraph nodes per section
    paragraph_nodes = [
        child
        for section in section_nodes
        for child in index.zoom_in(section.id)
        if child.level == IndexLevel.PARAGRAPH
    ]
    assert paragraph_nodes
    assert all(IndexLevel.PARAGRAPH == para.level for para in paragraph_nodes)

    # Sentence nodes exist
    sentence_nodes = [
        child
        for paragraph in paragraph_nodes
        for child in index.zoom_in(paragraph.id)
        if child.level == IndexLevel.SENTENCE
    ]
    assert sentence_nodes

    # Token nodes exist
    token_nodes = [
        child
        for sentence in sentence_nodes
        for child in index.zoom_in(sentence.id)
        if child.level == IndexLevel.SUBWORD
    ]
    assert token_nodes
    # embeddings should be present (length > 0)
    assert all(node.embeddings and len(node.embeddings) > 0 for node in token_nodes)


def test_query_returns_expected_granularity():
    index = HierarchicalIndex()
    index.index_document(SAMPLE_DOC, doc_id="aimos-architecture")

    results = index.query("context retrieval", target_level=IndexLevel.PARAGRAPH)
    assert results
    assert all(res.level == IndexLevel.PARAGRAPH for res in results)
    assert any("HHNI" in res.content for res in results)


def test_zoom_and_context_navigation():
    index = HierarchicalIndex()
    root_id = index.index_document(SAMPLE_DOC, doc_id="aimos")
    section = index.zoom_in(root_id)[0]
    paragraph = index.zoom_in(section.id)[0]

    # Zoom out from paragraph -> section
    parent = index.zoom_out(paragraph.id)
    assert parent and parent.id == section.id

    # get contextual nodes including siblings
    context = index.get_context(paragraph.id, include_parent=True, include_siblings=True)
    ids = {node.id for node in context}
    assert section.id in ids
    assert paragraph.id in ids
    assert len(ids) >= 2  # contains at least node + parent


def test_serialization_roundtrip():
    index = HierarchicalIndex()
    index.index_document(SAMPLE_DOC, doc_id="aimos")

    payload = index.to_dict()
    serialized = json.dumps(payload)  # ensure JSON serializable
    rehydrated = HierarchicalIndex.from_dict(json.loads(serialized))

    assert len(rehydrated) == len(index)
    assert rehydrated.root_id == index.root_id
    # spot check one node
    original_section = next(node for node in index.nodes.values() if node.level == IndexLevel.SECTION)
    restored = rehydrated.nodes[original_section.id]
    assert restored.summary == original_section.summary


def test_query_requires_non_empty_input():
    index = HierarchicalIndex()
    index.index_document(SAMPLE_DOC, doc_id="aimos")
    with pytest.raises(ValueError):
        index.query("", IndexLevel.PARAGRAPH)
