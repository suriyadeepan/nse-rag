"""Compatibility smoke coverage for the selected F001 integrations."""

def test_selected_integrations_import():
    import chromadb
    import cohere
    import openai
    import pymupdf
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI
    from llama_index.postprocessor.cohere_rerank import CohereRerank
    from llama_index.retrievers.bm25 import BM25Retriever
    from llama_index.vector_stores.chroma import ChromaVectorStore

    assert all((chromadb, cohere, openai, pymupdf))
    assert all(
        (
            SentenceSplitter,
            OpenAIEmbedding,
            OpenAI,
            CohereRerank,
            BM25Retriever,
            ChromaVectorStore,
        )
    )
