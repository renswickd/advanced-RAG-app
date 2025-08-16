import os
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from utils.logger import setup_logger
from utils.exceptions import RetrievalError
from utils.vector_store import load_vector_store
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Setup (Groq)
def get_llm():
    return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

# Extract metadata filters via LLM
def extract_filters_from_query(query: str, llm: ChatGroq, logger) -> Dict[str, str]:
    prompt = f"""
You are an highly skilled helpful assistant that reads user search queries and extracts metadata filters.
Return a JSON object with optional keys: doc_id, page_num, date.

For example, from "in document report1 page 3", return:
{{ "doc_id": "report1", "page_num": "3" }}

User query: \"{query}\"
"""
    try:
        resp = llm.invoke([("system", "Extract metadata filters."), ("human", prompt)])
        # naive parsing
        import json
        filters = json.loads(resp.content)
        return filters
    except Exception as e:
        logger.warning(f"Failed to extract filters via LLM: {e}")
        return {}

# Main retrieval function
def retrieve(query: str, top_k: int = 5, score_threshold: float = 0.3, logger=None) -> List[Dict[str, Any]]:
    if logger is None:
        logger = setup_logger("retrieval")

    try:
        llm = get_llm()
        filters = extract_filters_from_query(query, llm, logger)
        logger.debug(f"Metadata filters extracted: {filters}")

        # Load vector store
        embeddings = load_vector_store()
        retriever = embeddings.as_retriever(search_kwargs={"k": top_k * 2})

        # Perform semantic search
        # docs_and_scores = retriever.get_relevant_documents(query)
        # docs_and_scores = retriever.invoke(query) ####
        docs_and_scores = embeddings.similarity_search_with_score(query, k=top_k * 2)
        # logger.debug(f"Retrieved {len(docs_and_scores)} documents before filtering.")
        # logger.debug(f"Retrieved documents: {docs_and_scores}")
        # docs_and_scores: list of Document with metadata and score

        # Filter by metadata and threshold
        results = []
        for doc, score in docs_and_scores:
            if score is not None and score < score_threshold:
                continue
            # metadata match
            matched = True
            for key, val in filters.items():
                if key in doc.metadata and str(doc.metadata[key]) != str(val):
                    matched = False
                    break
            if matched:
                results.append({
                    "chunk_id": doc.metadata.get("chunk_id"),
                    "doc_id": doc.metadata.get("doc_id"),
                    "page_num": doc.metadata.get("page_num"),
                    "content": doc.page_content,
                    "score": score,
                })
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

        logger.info(f"Retrieved {len(results)} chunks for query: {query}")
        return results

    except Exception as e:
        logger.exception("Retrieval pipeline failed.")
        raise RetrievalError("Failed to retrieve relevant documents.") from e
