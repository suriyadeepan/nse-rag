from types import SimpleNamespace

from llama_index.core.schema import NodeWithScore, TextNode

from nse_rag.answer import (
    ANSWER_MODEL,
    ClaimStatus,
    INSUFFICIENT_EVIDENCE,
    answer_from_passages,
)


class FakeLLM:
    def __init__(self, *responses: str):
        self.responses = list(responses)
        self.prompt = None
        self.prompts = []

    def complete(self, prompt: str):
        self.prompt = prompt
        self.prompts.append(prompt)
        response = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        return SimpleNamespace(text=response)


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
        date="2026-04-09",
    )

    result = answer_from_passages("Why was trading suspended?", [node], llm=llm)

    assert ANSWER_MODEL == "gpt-4.1-mini"
    answer_prompt, validation_prompt = llm.prompts
    assert "Trading is suspended after the stated event." in answer_prompt
    assert "Question:\nWhy was trading suspended?" in answer_prompt
    assert "metadata listing" not in answer_prompt
    assert "PDF page: 7" in answer_prompt
    assert "PDF page: 99" not in answer_prompt
    assert "Title: Suspension notice" in answer_prompt
    assert "Publication date: 2026-04-09" in answer_prompt
    assert "without deciding" in answer_prompt
    assert "Trading is suspended after the stated event." in validation_prompt
    assert result.answer == "Trading is suspended for the stated reason [S1]."
    assert result.insufficient_evidence is False
    assert len(result.references) == 1
    reference = result.references[0]
    assert reference.circular_id == "NSE/CMTR/123"
    assert reference.page_number == 7
    assert reference.passage == "Trading is suspended after the stated event."
    assert reference.title == "Suspension notice"
    assert reference.date == "2026-04-09"
    assert len(result.claims) == 1
    assert result.claims[0].status == ClaimStatus.NEEDS_REVIEW


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


def test_validates_claim_against_only_its_mapped_cited_passage():
    llm = FakeLLM(
        "Suspension was revoked on April 9, 2026 [S1].",
        '{"claims":[{"claim":"Suspension was revoked on April 9, 2026",'
        '"source_ids":["S1"],"status":"Supported"}]}',
    )
    first = retrieved(
        "Trading suspension will be revoked effective April 09, 2026.",
        circular_id="NSE/CMTR/123",
        page_number=2,
    )
    second = retrieved(
        "Trading hours are extended until 5 PM.",
        circular_id="NSE/CMTR/456",
        page_number=3,
    )

    result = answer_from_passages("When was it revoked?", [first, second], llm=llm)

    assert result.claims[0].status == ClaimStatus.SUPPORTED
    assert [ref.circular_id for ref in result.claims[0].references] == ["NSE/CMTR/123"]
    assert result.references[0].title is None
    assert result.references[0].date is None
    assert "Trading suspension will be revoked effective April 09, 2026." in llm.prompts[1]
    assert "Trading hours are extended until 5 PM." not in llm.prompts[1]
    assert "automated" in result.validation_note.lower()


def test_unsupported_claim_is_returned_with_its_cited_evidence():
    llm = FakeLLM(
        "Trading resumes on April 10, 2026 [S1].",
        '{"claims":[{"claim":"Trading resumes on April 10, 2026",'
        '"source_ids":["S1"],"status":"Unsupported"}]}',
    )
    result = answer_from_passages(
        "When does trading resume?",
        [retrieved("Suspension ends April 9, 2026.", circular_id="C-1", page_number=1)],
        llm=llm,
    )

    assert result.claims[0].status == ClaimStatus.UNSUPPORTED
    assert result.claims[0].references[0].passage == "Suspension ends April 9, 2026."


def test_invalid_validator_output_fails_closed_and_unknown_ids_do_not_map():
    malformed = FakeLLM("A factual claim [S1].", "not JSON")
    result = answer_from_passages(
        "Question?",
        [retrieved("Evidence", circular_id="C-1", page_number=1)],
        llm=malformed,
    )
    assert result.claims[0].status == ClaimStatus.NEEDS_REVIEW
    assert result.claims[0].references[0].circular_id == "C-1"

    unknown_id = FakeLLM(
        "A factual claim [S1].",
        '{"claims":[{"claim":"A factual claim","source_ids":["S9"],'
        '"status":"Supported"}]}',
    )
    result = answer_from_passages(
        "Question?",
        [retrieved("Evidence", circular_id="C-1", page_number=1)],
        llm=unknown_id,
    )
    assert result.claims[0].status == ClaimStatus.NEEDS_REVIEW
