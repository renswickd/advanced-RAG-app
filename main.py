from utils.logger import generate_session_id, setup_logger
# from utils.exceptions import IngestionError
from chat.retriever import retrieve
from utils.exceptions import RetrievalError

def main():
    session_id = generate_session_id()
    logger = setup_logger(session_id)

    logger.info("Starting RAG pipeline session.")

    # --- Test Ingestion ---
    # try:
    #     # Simulate ingestion error
    #     raise IngestionError("Mock ingestion failure", details={"file": "FILE-DOES-NOT-EXISTS.pdf"})
    # except IngestionError as e:
    #     logger.exception(e)

    # --- Test Retrieval ---
    logger.info("Starting retrieval process...")
    # user_query = input("Enter your query: ")
    user_query = "What is the use of Attention in Transformers?"
    try:
        results = retrieve(user_query, top_k=5, score_threshold=0.4, logger=logger)
        print("\nRetrieved Chunks:")
        # print(f"\n\n{len(results)} results found for query: '{user_query}'\n")
        # print(f"\n\nResults:\n{results}\n")
        for idx, r in enumerate(results, 1):
            print(f"{idx}. [Doc: {r['doc_id']} | Page: {r['page_num']} | Score: {r['score']}]")
            print(f"   {r['content']}\n")
    except RetrievalError as e:
        logger.error(f"Retrieval error: {e}")
        return

    # Placeholder: Future step to call LLM with retrieved chunks for answer generation
    logger.info("Retrieval complete. Ready for next step (generation).")

if __name__ == "__main__":
    main()
