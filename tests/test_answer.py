from types import SimpleNamespace

from llama_index.core.schema import NodeWithScore, TextNode

from nse_rag.answer import (
    ANSWER_MODEL,
    INSUFFICIENT_EVIDENCE,
    answer_from_passages,
)


class FakeLLM:
    def __init__(self, response: str):
        self.response = response
        self.prompt = None

    def complete(self, prompt: str):
        self.prompt = prompt
        return SimpleNamespace(text=self.response)


def retrieved(text: str, **metadata) -> NodeWithScore:
    return NodeWithScore(node=TextNode(text=text, metadata=metadata), score=0.9)


def test_answers_only_from_retrieved_context_and_returns_actual_page_reference():
    llm = FakeLLM("Trading is suspended for the stated reason [S1].")
    node = retrieved(
        "Trading is suspended after the stated event.",
        circular_id="NSE/CMTR/123",
        page_number=7,
        page=99,
        title="Suspension notice",
    )

    result = answer_from_passages("Why was trading suspended?", [node], llm=llm)

    assert ANSWER_MODEL == "gpt-4.1-mini"
    assert "Trading is suspended after the stated event." in llm.prompt
    assert "Question:\nWhy was trading suspended?" in llm.prompt
    assert "metadata listing" not in llm.prompt
    assert "PDF page: 7" in llm.prompt
    assert "PDF page: 99" not in llm.prompt
    assert result.answer == "Trading is suspended for the stated reason [S1]."
    assert result.insufficient_evidence is False
    assert len(result.references) == 1
    reference = result.references[0]
    assert reference.circular_id == "NSE/CMTR/123"
    assert reference.page_number == 7
    assert reference.passage == "Trading is suspended after the stated event."


def test_explicit_insufficient_evidence_has_no_citations():
    llm = FakeLLM("INSUFFICIENT_EVIDENCE")
    result = answer_from_passages(
        "What was the settlement price?",
        [retrieved("This notice discusses trading hours.", circular_id="C-1", page_number=2)],
        llm=llm,
    )

    assert result.answer == INSUFFICIENT_EVIDENCE
    assert result.insufficient_evidence is True
    assert result.references == []


def test_no_usable_retrieved_passages_returns_insufficient_evidence():
    llm = FakeLLM("Some ungrounded model response")
    result = answer_from_passages(
        "What happened?",
        [retrieved("No page metadata", circular_id="C-1", page=42)],
        llm=llm,
    )

    assert result.answer == INSUFFICIENT_EVIDENCE
    assert result.insufficient_evidence is True
    assert result.references == []
    assert llm.prompt is None


def test_rejects_unknown_or_missing_source_tags():
    source = retrieved("Notice text", circular_id="C-2", page_number=4)

    unknown = answer_from_passages("Question?", [source], llm=FakeLLM("Claim [S9]."))
    missing = answer_from_passages("Question?", [source], llm=FakeLLM("Unsupported claim."))

    assert unknown.insufficient_evidence is True
    assert missing.insufficient_evidence is True
    assert unknown.references == missing.references == []
