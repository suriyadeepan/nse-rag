import json
import importlib.util
import sys
from pathlib import Path

import pytest
from llama_index.core.schema import NodeWithScore, TextNode

EVALUATOR_PATH = Path(__file__).parents[1] / "scripts" / "evaluate_rag.py"
SPEC = importlib.util.spec_from_file_location("evaluate_rag", EVALUATOR_PATH)
EVALUATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EVALUATOR
SPEC.loader.exec_module(EVALUATOR)

aggregate_metrics = EVALUATOR.aggregate_metrics
deduplicate_circular_ids = EVALUATOR.deduplicate_circular_ids
evaluate_queries = EVALUATOR.evaluate_queries
inspect_index_inventory = EVALUATOR.inspect_index_inventory
query_metrics = EVALUATOR.query_metrics
verify_index_baseline = EVALUATOR.verify_index_baseline


def node(circular_id):
    return NodeWithScore(node=TextNode(text="passage", metadata={"circular_id": circular_id}))


def test_deduplicate_circular_ids_preserves_first_rank():
    assert deduplicate_circular_ids(["A", "A", None, "B", "A", "C"]) == ["A", "B", "C"]


def test_metrics_handle_multiple_expected_ids_and_first_relevant_rank():
    assert query_metrics(["X", "B", "B", "A"], ["A", "B"]) == {
        "recall@5": 1.0,
        "mrr": 0.5,
    }
    assert query_metrics(["X", "Y"], ["A", "B"]) == {
        "recall@5": 0.0,
        "mrr": 0.0,
    }


def test_metrics_respect_recall_cutoff_after_document_deduplication():
    assert query_metrics(["X", "X", "Y", "Z", "A"], ["A"], cutoff=3) == {
        "recall@3": 0.0,
        "mrr": 0.25,
    }


def test_aggregate_metrics_reports_overall_and_type_means():
    result = aggregate_metrics(
        [
            {"type": "semantic", "recall@5": 1.0, "mrr": 1.0},
            {"type": "semantic", "recall@5": 0.0, "mrr": 0.0},
            {"type": "exact_id", "recall@5": 1.0, "mrr": 0.5},
        ]
    )
    assert result == {
        "overall": {"query_count": 3, "recall@5": 2 / 3, "mrr": 0.5},
        "by_type": {
            "exact_id": {"query_count": 1, "recall@5": 1.0, "mrr": 0.5},
            "semantic": {"query_count": 2, "recall@5": 0.5, "mrr": 0.5},
        },
    }


def test_evaluate_queries_uses_same_query_and_settings_in_each_mode_sequentially():
    calls = []

    def fake_retrieve(query, indexes, *, mode, settings):
        calls.append((query, indexes, mode.value, settings.candidate_top_k, settings.top_k))
        return [node("A"), node("A"), node("B")]

    result = evaluate_queries(
        [{"query": "question", "type": "semantic", "expected_ids": ["B"]}],
        indexes="persisted",
        retrieve_fn=fake_retrieve,
    )
    assert calls == [
        ("question", "persisted", "dense", 20, 5),
        ("question", "persisted", "hybrid", 20, 5),
        ("question", "persisted", "hybrid-rerank", 20, 5),
    ]
    assert result["queries"][0]["modes"]["hybrid"]["ranked_ids"] == ["A", "B"]
    assert result["queries"][0]["modes"]["hybrid"]["retrieved_chunk_circular_ids"] == ["A", "A", "B"]
    assert json.loads(json.dumps(result))["metrics"]["dense"]["overall"]["query_count"] == 1


def test_inventory_counts_documents_separately_from_circular_ids(tmp_path):
    nodes = [
        {"metadata": {"pdf_path": "a.pdf", "circular_id": "A"}},
        {"metadata": {"pdf_path": "a.pdf", "circular_id": "A"}},
        {"metadata": {"pdf_path": "b.pdf", "circular_id": "A"}},
    ]
    (tmp_path / "nodes.jsonl").write_text("\n".join(json.dumps(item) for item in nodes))
    assert inspect_index_inventory(tmp_path) == {
        "node_count": 3,
        "source_pdf_count": 2,
        "circular_id_count": 1,
    }


def test_baseline_mismatch_stops_evaluation():
    with pytest.raises(ValueError, match="No evaluation was run"):
        verify_index_baseline({"node_count": 3, "source_pdf_count": 2})
