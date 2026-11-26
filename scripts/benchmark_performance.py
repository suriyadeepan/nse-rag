"""Measure a small sequential latency and token-usage sample on the persisted index."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import tiktoken
from llama_index.core.schema import NodeWithScore
from llama_index.llms.openai import OpenAI

from nse_rag.answer import ANSWER_MODEL, answer_from_passages
from nse_rag.index_store import DEFAULT_INDEX_DIR, NODE_CORPUS_FILENAME, open_local_indexes
from nse_rag.retrieval import COHERE_RERANK_MODEL, RetrievalMode, RetrievalSettings, retrieve

EVAL_FILE = Path("eval/eval.jsonl")
OUTPUT_FILE = Path("eval/performance-results.json")
EXPECTED_NODES = 36_853
EXPECTED_SOURCE_PDFS = 7_591
MODES = (RetrievalMode.DENSE, RetrievalMode.HYBRID, RetrievalMode.HYBRID_RERANK)
SETTINGS = RetrievalSettings(candidate_top_k=20, top_k=5)
REPETITIONS = 3
COHERE_MIN_INTERVAL_SECONDS = 6.2
COHERE_MODEL = COHERE_RERANK_MODEL
GPT_INPUT_PRICE_PER_MILLION = 0.40
GPT_OUTPUT_PRICE_PER_MILLION = 1.60
EMBEDDING_PRICE_PER_MILLION = 0.02
OPENAI_PRICING_SOURCE = "https://developers.openai.com/api/docs/pricing"
COHERE_PRICING_SOURCE = "https://cohere.com/blog/rerank-5"

# Fixed, representative sample: two exact IDs, four keyword/phrase, four semantic.
SAMPLE_QUERY_LINES = (1, 2, 7, 8, 9, 10, 13, 14, 15, 16)
# Five answer samples drawn from the same benchmark sample, using the hybrid result.
ANSWER_SAMPLE_LINES = (1, 7, 8, 13, 15)


def load_sample(path: Path = EVAL_FILE) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = [rows[number - 1] for number in SAMPLE_QUERY_LINES]
    types = {"exact_id": 0, "keyword_phrase": 0, "semantic": 0}
    for row in selected:
        if row["type"] in types:
            types[row["type"]] += 1
    if len(selected) != 10 or types != {"exact_id": 2, "keyword_phrase": 4, "semantic": 4}:
        raise ValueError(f"Selected sample has unexpected types/counts: {types}")
    return selected


def inspect_inventory(index_dir: Path) -> dict[str, int]:
    node_file = Path(index_dir) / NODE_CORPUS_FILENAME
    nodes, paths, circular_ids = 0, set(), set()
    with node_file.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            item = json.loads(line)
            metadata = item.get("metadata", {})
            nodes += 1
            if metadata.get("pdf_path"):
                paths.add(os.path.normpath(str(metadata["pdf_path"])))
            if metadata.get("circular_id"):
                circular_ids.add(str(metadata["circular_id"]))
    return {"node_count": nodes, "source_pdf_count": len(paths), "circular_id_count": len(circular_ids)}


def verify_inventory(inventory: dict[str, int]) -> None:
    if inventory["node_count"] != EXPECTED_NODES or inventory["source_pdf_count"] != EXPECTED_SOURCE_PDFS:
        raise ValueError(
            "Persisted index does not match F001 baseline; expected "
            f"{EXPECTED_NODES} nodes / {EXPECTED_SOURCE_PDFS} PDFs, found "
            f"{inventory['node_count']} nodes / {inventory['source_pdf_count']} PDFs."
        )


class UsageCapture:
    """Wrap the existing answer model and retain its raw completion usage metadata."""

    def __init__(self) -> None:
        self.model = OpenAI(model=ANSWER_MODEL)
        self.response = None

    def complete(self, prompt: str):
        self.response = self.model.complete(prompt)
        return self.response


def response_usage(response: Any) -> dict[str, int] | None:
    additional = getattr(response, "additional_kwargs", {}) or {}
    usage = {
        "input_tokens": additional.get("prompt_tokens"),
        "output_tokens": additional.get("completion_tokens"),
    }
    if usage["input_tokens"] is None or usage["output_tokens"] is None:
        raw_usage = getattr(getattr(response, "raw", None), "usage", None)
        usage["input_tokens"] = getattr(raw_usage, "prompt_tokens", None)
        usage["output_tokens"] = getattr(raw_usage, "completion_tokens", None)
    if usage["input_tokens"] is None or usage["output_tokens"] is None:
        return None
    usage["total_tokens"] = int(usage["input_tokens"]) + int(usage["output_tokens"])
    return {key: int(value) for key, value in usage.items()}


def timed_retrieve(
    query: str,
    indexes: Any,
    mode: RetrievalMode,
    *,
    last_cohere_call: float | None,
) -> tuple[list[NodeWithScore], float, float | None]:
    if mode == RetrievalMode.HYBRID_RERANK and last_cohere_call is not None:
        delay = COHERE_MIN_INTERVAL_SECONDS - (time.monotonic() - last_cohere_call)
        if delay > 0:
            time.sleep(delay)
    start = time.perf_counter()
    result = retrieve(query, indexes, mode=mode, settings=SETTINGS)
    elapsed = time.perf_counter() - start
    if mode == RetrievalMode.HYBRID_RERANK:
        last_cohere_call = time.monotonic()
    return result, elapsed, last_cohere_call


def run_benchmark(index_dir: Path, eval_file: Path) -> dict[str, Any]:
    queries = load_sample(eval_file)
    inventory = inspect_inventory(index_dir)
    verify_inventory(inventory)
    indexes = open_local_indexes(index_dir)
    if indexes.node_count != inventory["node_count"]:
        raise ValueError("Opened index node count differs from persisted node inventory")

    timings: dict[str, dict[str, list[float]]] = {mode.value: {} for mode in MODES}
    measured_results: dict[tuple[int, str], list[NodeWithScore]] = {}
    warmups: dict[str, int] = {mode.value: 0 for mode in MODES}
    last_cohere_call = None
    for query_index, record in enumerate(queries):
        query = record["query"]
        for mode in MODES:
            results, _, last_cohere_call = timed_retrieve(
                query, indexes, mode, last_cohere_call=last_cohere_call
            )
            warmups[mode.value] += 1
            timings[mode.value][str(query_index)] = []
            for _ in range(REPETITIONS):
                results, elapsed, last_cohere_call = timed_retrieve(
                    query, indexes, mode, last_cohere_call=last_cohere_call
                )
                timings[mode.value][str(query_index)].append(elapsed)
                measured_results[(query_index, mode.value)] = results

    token_encoding = tiktoken.get_encoding("cl100k_base")
    answer_rows = []
    for line_number in ANSWER_SAMPLE_LINES:
        query_index = SAMPLE_QUERY_LINES.index(line_number)
        record = queries[query_index]
        nodes = measured_results[(query_index, RetrievalMode.HYBRID.value)]
        capture = UsageCapture()
        start = time.perf_counter()
        answer = answer_from_passages(record["query"], nodes, llm=capture)
        answer_elapsed = time.perf_counter() - start
        usage = response_usage(capture.response) if capture.response is not None else None
        answer_rows.append(
            {
                "query": record["query"],
                "source_line": line_number,
                "retrieval_mode": RetrievalMode.HYBRID.value,
                "answer_latency_seconds": answer_elapsed,
                "model": ANSWER_MODEL,
                "usage": usage,
                "answer_generated": bool(answer.answer),
            }
        )

    summary = {}
    for mode, per_query in timings.items():
        values = [elapsed for samples in per_query.values() for elapsed in samples]
        summary[mode] = {
            "measured_call_count": len(values),
            "average_seconds": statistics.mean(values),
            "p50_seconds": statistics.median(values),
            "per_query_seconds": per_query,
        }

    query_embedding_tokens = sum(
        len(token_encoding.encode(record["query"])) * REPETITIONS_PLUS_WARMUP * len(MODES)
        for record in queries
    )
    usages = [row["usage"] for row in answer_rows if row["usage"] is not None]
    answer_input_tokens = sum(row["input_tokens"] for row in usages)
    answer_output_tokens = sum(row["output_tokens"] for row in usages)
    pricing_date = datetime.now(UTC).date().isoformat()
    answer_cost = (
        answer_input_tokens * GPT_INPUT_PRICE_PER_MILLION
        + answer_output_tokens * GPT_OUTPUT_PRICE_PER_MILLION
    ) / 1_000_000
    query_embedding_cost = query_embedding_tokens * EMBEDDING_PRICE_PER_MILLION / 1_000_000

    return {
        "run_date_utc": pricing_date,
        "corpus": {
            **inventory,
            "expected_source_pdf_count": EXPECTED_SOURCE_PDFS,
            "expected_node_count": EXPECTED_NODES,
        },
        "benchmark": {
            "query_count": len(queries),
            "source_lines": list(SAMPLE_QUERY_LINES),
            "types": {key: sum(row["type"] == key for row in queries) for key in ("exact_id", "keyword_phrase", "semantic")},
            "warmup_calls_per_mode": warmups,
            "measured_repetitions_per_query_mode": REPETITIONS,
            "retrieval_limits": {"candidate_top_k": SETTINGS.candidate_top_k, "final_top_k": SETTINGS.top_k},
            "cohere_min_interval_seconds": COHERE_MIN_INTERVAL_SECONDS,
            "retrieval_models": {"embedding": "text-embedding-3-small", "reranker": COHERE_MODEL},
            "retrieval_latency": summary,
        },
        "answer_sample": {
            "count": len(answer_rows),
            "model": ANSWER_MODEL,
            "retrieval_mode": RetrievalMode.HYBRID.value,
            "average_latency_seconds": statistics.mean(row["answer_latency_seconds"] for row in answer_rows),
            "samples": answer_rows,
        },
        "cost": {
            "pricing_checked_date": pricing_date,
            "openai_pricing_source": OPENAI_PRICING_SOURCE,
            "cohere_pricing_source": COHERE_PRICING_SOURCE,
            "gpt_4_1_mini_usd_per_million": {
                "input": GPT_INPUT_PRICE_PER_MILLION,
                "output": GPT_OUTPUT_PRICE_PER_MILLION,
            },
            "answer_usage": {
                "input_tokens": answer_input_tokens if len(usages) == len(answer_rows) else None,
                "output_tokens": answer_output_tokens if len(usages) == len(answer_rows) else None,
                "cost_usd": answer_cost if len(usages) == len(answer_rows) else None,
                "available_sample_count": len(usages),
            },
            "query_embedding": {
                "token_count_estimated_with": "cl100k_base",
                "tokens": query_embedding_tokens,
                "price_usd_per_million_tokens": EMBEDDING_PRICE_PER_MILLION,
                "cost_usd_estimate": query_embedding_cost,
                "note": "Estimated from submitted query text and measured request count; not account usage.",
            },
            "cohere_rerank": {
                "model": COHERE_MODEL,
                "usage": "unavailable from the existing LlamaIndex CohereRerank wrapper; account usage not queried",
                "cost_usd": None,
            },
            "corpus_embedding_estimate_usd": 0.24,
            "corpus_embedding_estimate_note": "One-time F001 estimate; not incurred by this benchmark and not account billing.",
        },
    }


REPETITIONS_PLUS_WARMUP = REPETITIONS + 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    parser.add_argument("--eval-file", type=Path, default=EVAL_FILE)
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_benchmark(args.index_dir, args.eval_file)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Benchmarked {results['benchmark']['query_count']} queries; results: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
