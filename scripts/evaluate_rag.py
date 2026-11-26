"""Evaluate dense, hybrid, and reranked retrieval on the persisted NSE index."""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

from llama_index.core.schema import NodeWithScore

from nse_rag.index_store import DEFAULT_INDEX_DIR, NODE_CORPUS_FILENAME, open_local_indexes
from nse_rag.retrieval import RetrievalMode, RetrievalSettings, retrieve

EVAL_FILE = Path("eval/eval.jsonl")
RESULT_FILE = Path("eval/results.json")
EXPECTED_NODES = 36_853
EXPECTED_SOURCE_PDFS = 7_591
MODES = (RetrievalMode.DENSE, RetrievalMode.HYBRID, RetrievalMode.HYBRID_RERANK)
SETTINGS = RetrievalSettings(candidate_top_k=20, top_k=5)
COHERE_MIN_INTERVAL_SECONDS = 6.2


def load_queries(path: Path = EVAL_FILE) -> list[dict[str, Any]]:
    """Read and minimally validate the labelled JSONL query set."""
    queries = []
    with Path(path).open(encoding="utf-8") as query_file:
        for line_number, line in enumerate(query_file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}") from error
            if not isinstance(record, dict):
                raise ValueError(f"Query on line {line_number} must be a JSON object")
            if not isinstance(record.get("query"), str) or not record["query"].strip():
                raise ValueError(f"Query on line {line_number} has no non-empty query")
            if not isinstance(record.get("type"), str) or not record["type"].strip():
                raise ValueError(f"Query on line {line_number} has no non-empty type")
            expected = record.get("expected_ids")
            if not isinstance(expected, list) or not expected or not all(
                isinstance(item, str) and item.strip() for item in expected
            ):
                raise ValueError(f"Query on line {line_number} has invalid expected_ids")
            queries.append(record)
    if not queries:
        raise ValueError(f"No evaluation queries found in {path}")
    return queries


def deduplicate_circular_ids(circular_ids: Iterable[str | None]) -> list[str]:
    """Keep each circular once, in its first retrieved position."""
    unique_ids = []
    seen = set()
    for circular_id in circular_ids:
        if circular_id and circular_id not in seen:
            seen.add(circular_id)
            unique_ids.append(circular_id)
    return unique_ids


def query_metrics(
    ranked_ids: Iterable[str], expected_ids: Iterable[str], *, cutoff: int = 5
) -> dict[str, float]:
    """Compute document-level Recall@cutoff and reciprocal rank."""
    ranked = deduplicate_circular_ids(ranked_ids)
    expected = set(expected_ids)
    if not expected:
        raise ValueError("expected_ids must not be empty")
    relevant_rank = next(
        (rank for rank, circular_id in enumerate(ranked, start=1) if circular_id in expected),
        None,
    )
    recalled = len(set(ranked[:cutoff]) & expected)
    return {
        f"recall@{cutoff}": recalled / len(expected),
        "mrr": 1 / relevant_rank if relevant_rank is not None else 0.0,
    }


def aggregate_metrics(
    rows: Iterable[Mapping[str, Any]], *, cutoff: int = 5
) -> dict[str, Any]:
    """Average per-query metrics overall and for each query type."""
    records = list(rows)

    def average(group: list[Mapping[str, Any]]) -> dict[str, float | int]:
        if not group:
            return {"query_count": 0, f"recall@{cutoff}": 0.0, "mrr": 0.0}
        return {
            "query_count": len(group),
            f"recall@{cutoff}": sum(row[f"recall@{cutoff}"] for row in group) / len(group),
            "mrr": sum(row["mrr"] for row in group) / len(group),
        }

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[str(row["type"])].append(row)
    return {
        "overall": average(records),
        "by_type": {query_type: average(group) for query_type, group in sorted(grouped.items())},
    }


def evaluate_queries(
    queries: list[dict[str, Any]],
    indexes,
    *,
    retrieve_fn: Callable[..., list[NodeWithScore]] | None = None,
) -> dict[str, Any]:
    """Run identical queries sequentially through all configured retrieval modes."""
    retrieval = retrieve_fn or retrieve
    per_mode: dict[str, list[dict[str, Any]]] = {mode.value: [] for mode in MODES}
    per_query = []
    last_cohere_call_at: float | None = None

    for record in queries:
        query = record["query"]
        expected_ids = record["expected_ids"]
        mode_results = {}
        for mode in MODES:
            # Deliberately serial: hybrid-rerank makes one Cohere request per query.
            if mode == RetrievalMode.HYBRID_RERANK:
                now = time.monotonic()
                if last_cohere_call_at is not None:
                    delay = COHERE_MIN_INTERVAL_SECONDS - (now - last_cohere_call_at)
                    if delay > 0:
                        time.sleep(delay)
                last_cohere_call_at = time.monotonic()
            passages = retrieval(query, indexes, mode=mode, settings=SETTINGS)
            raw_ranked_ids = [
                node.node.metadata.get("circular_id") for node in passages
            ]
            ranked_ids = deduplicate_circular_ids(raw_ranked_ids)
            metrics = query_metrics(ranked_ids, expected_ids)
            mode_result = {
                "ranked_ids": ranked_ids,
                "retrieved_chunk_circular_ids": raw_ranked_ids,
                **metrics,
            }
            mode_results[mode.value] = mode_result
            per_mode[mode.value].append({"type": record["type"], **metrics})
        per_query.append(
            {
                "query": query,
                "type": record["type"],
                "expected_ids": expected_ids,
                "modes": mode_results,
            }
        )

    return {
        "query_count": len(queries),
        "settings": {
            "candidate_top_k": SETTINGS.candidate_top_k,
            "top_k": SETTINGS.top_k,
            "cohere_min_interval_seconds": COHERE_MIN_INTERVAL_SECONDS,
        },
        "queries": per_query,
        "metrics": {
            mode: aggregate_metrics(rows) for mode, rows in per_mode.items()
        },
    }


def inspect_index_inventory(index_dir: Path) -> dict[str, int]:
    """Count persisted nodes, source PDFs, and circular IDs without rebuilding."""
    node_path = Path(index_dir) / NODE_CORPUS_FILENAME
    node_count = 0
    source_paths = set()
    circular_ids = set()
    with node_path.open(encoding="utf-8") as node_file:
        for line in node_file:
            if not line.strip():
                continue
            node = json.loads(line)
            metadata = node.get("metadata", {})
            node_count += 1
            if metadata.get("pdf_path"):
                source_paths.add(os.path.normpath(str(metadata["pdf_path"])))
            if metadata.get("circular_id"):
                circular_ids.add(str(metadata["circular_id"]))
    return {
        "node_count": node_count,
        "source_pdf_count": len(source_paths),
        "circular_id_count": len(circular_ids),
    }


def verify_index_baseline(inventory: Mapping[str, int]) -> None:
    """Stop before evaluation if the persisted index differs from F001's baseline."""
    if inventory["node_count"] != EXPECTED_NODES or inventory["source_pdf_count"] != EXPECTED_SOURCE_PDFS:
        raise ValueError(
            "Persisted index does not match F001 baseline "
            f"(expected {EXPECTED_NODES} nodes / {EXPECTED_SOURCE_PDFS} source PDFs; "
            f"found {inventory['node_count']} nodes / {inventory['source_pdf_count']} source PDFs). "
            "No evaluation was run; do not rebuild as part of F002."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    parser.add_argument("--eval-file", type=Path, default=EVAL_FILE)
    parser.add_argument("--output", type=Path, default=RESULT_FILE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    queries = load_queries(args.eval_file)
    inventory = inspect_index_inventory(args.index_dir)
    verify_index_baseline(inventory)
    indexes = open_local_indexes(args.index_dir)
    if indexes.node_count != inventory["node_count"]:
        raise ValueError(
            "Opened index/node corpus count mismatch "
            f"(opened={indexes.node_count}, corpus={inventory['node_count']})"
        )

    results = evaluate_queries(queries, indexes)
    results["index"] = inventory
    results["modes"] = [mode.value for mode in MODES]
    results["distinct_circular_ids_in_index"] = inventory["circular_id_count"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Evaluated {len(queries)} queries in {len(MODES)} modes; results: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
