from utils.logger import generate_session_id, setup_logger
from utils.exceptions import IngestionError

def main():
    session_id = generate_session_id()
    logger, session_dir = setup_logger(session_id)

    logger.info("Starting RAG pipeline session.")
    logger.debug(f"Session directory: {session_dir}")

    try:
        # Simulate ingestion error
        raise IngestionError("Mock ingestion failure", details={"file": "FILE-DOES-NOT-EXISTS.pdf"})
    except IngestionError as e:
        logger.exception(e)

    logger.info("RAG pipeline session complete.")

if __name__ == "__main__":
    main()
