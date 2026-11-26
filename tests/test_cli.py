from types import SimpleNamespace

from llama_index.core.schema import NodeWithScore, TextNode

import nse_rag.cli as cli


def test_ingest_cli_uses_full_local_corpus_defaults_and_reports_summary(monkeypatch, capsys):
    calls = {}
    summary = SimpleNamespace(
        pdfs_found=7614,
        metadata_records_loaded=7612,
        documents_indexed=7600,
        documents_skipped=14,
        nodes_indexed=123456,
    )

    def fake_build(pdf_dir, metadata_dir, index_dir, *, batch_size):
        calls.update(
            pdf_dir=pdf_dir,
            metadata_dir=metadata_dir,
            index_dir=index_dir,
            batch_size=batch_size,
        )
        return SimpleNamespace(summary=summary)

    monkeypatch.setattr(cli, "build_local_indexes", fake_build)

    assert cli.main(["ingest"]) == 0

    output = capsys.readouterr().out
    assert calls["pdf_dir"] == cli.DEFAULT_PDF_DIR
    assert calls["metadata_dir"] == cli.DEFAULT_METADATA_DIR
    assert calls["index_dir"] == cli.DEFAULT_INDEX_DIR
    assert calls["batch_size"] == 128
    assert "PDFs found=7614" in output
    assert "documents indexed=7600" in output
    assert "documents skipped=14" in output


def test_query_cli_selects_mode_limits_and_prints_page_citations(monkeypatch, capsys):
    calls = {}
    passage = NodeWithScore(
        node=TextNode(
            text="Trading hours are extended.",
            metadata={"circular_id": "NSE/CMTR/4", "page_number": 3},
        ),
        score=1,
    )

    monkeypatch.setattr(cli, "open_local_indexes", lambda path: "indexes")

    def fake_retrieve(question, indexes, *, mode, settings):
        calls.update(question=question, indexes=indexes, mode=mode, settings=settings)
        return [passage]

    monkeypatch.setattr(cli, "retrieve", fake_retrieve)

    class FakeAnswer:
        answer = "Trading hours are extended [S1]."
        insufficient_evidence = False
        references = [
            SimpleNamespace(
                source_id="S1",
                circular_id="NSE/CMTR/4",
                page_number=3,
                passage="Trading hours are extended.",
                title="Trading Hours",
                date="2026-01-01",
            )
        ]
        claims = [
            SimpleNamespace(
                status=cli.ClaimStatus.SUPPORTED,
                claim="Trading hours are extended.",
                references=[
                    SimpleNamespace(
                        circular_id="NSE/CMTR/4",
                        page_number=3,
                        passage="Trading hours are extended.",
                        title="Trading Hours",
                        date="2026-01-01",
                    )
                ],
            )
        ]
        validation_note = "Automated checks are an aid, not a guarantee."

    def fake_answer(question, nodes):
        calls["answer_question"] = question
        calls["answer_nodes"] = nodes
        return FakeAnswer()

    monkeypatch.setattr(cli, "answer_from_passages", fake_answer)

    assert cli.main(
        ["query", "What changed?", "--mode", "hybrid-rerank", "--candidate-top-k", "12", "--top-k", "3"]
    ) == 0

    output = capsys.readouterr().out
    assert calls["question"] == "What changed?"
    assert calls["mode"] == "hybrid-rerank"
    assert calls["settings"].candidate_top_k == 12
    assert calls["settings"].top_k == 3
    assert calls["answer_question"] == "What changed?"
    assert "Circular ID: NSE/CMTR/4 | Title: Trading Hours" in output
    assert "Date: 2026-01-01 | PDF page: 3" in output
    assert "Trading hours are extended." in output
    assert "Title: Trading Hours" in output
    assert "Date: 2026-01-01" in output
    assert "[Supported] Trading hours are extended." in output
    assert "Automated checks are an aid, not a guarantee." in output


def test_cli_help_lists_ingest_and_query(capsys):
    try:
        cli.main(["--help"])
    except SystemExit as error:
        assert error.code == 0
    else:
        raise AssertionError("--help should exit")

    output = capsys.readouterr().out
    assert "ingest" in output
    assert "query" in output
