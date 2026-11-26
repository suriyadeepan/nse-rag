import json
from pathlib import Path


EVAL_FILE = Path(__file__).parents[1] / "eval" / "eval.jsonl"
QUERY_TYPES = {"exact_id", "keyword_phrase", "semantic", "multi_circular"}


def test_eval_queries_have_valid_shape_and_balanced_coverage():
    records = [json.loads(line) for line in EVAL_FILE.read_text().splitlines() if line.strip()]

    assert 20 <= len(records) <= 30
    assert {record["type"] for record in records} == QUERY_TYPES
    assert all(sum(record["type"] == query_type for record in records) == 6 for query_type in QUERY_TYPES)

    queries = set()
    for record in records:
        assert set(record) <= {"query", "type", "expected_ids", "expected_answer"}
        assert isinstance(record.get("query"), str) and record["query"].strip()
        assert record.get("type") in QUERY_TYPES
        assert isinstance(record.get("expected_ids"), list) and record["expected_ids"]
        assert all(isinstance(circular_id, str) and circular_id.strip() for circular_id in record["expected_ids"])
        assert len(record["expected_ids"]) == len(set(record["expected_ids"]))
        assert record["query"] not in queries
        queries.add(record["query"])

        if record["type"] == "multi_circular":
            assert len(record["expected_ids"]) >= 2
