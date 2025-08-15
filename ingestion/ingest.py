import os
import json
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.logger import generate_session_id, setup_logger
from utils.file_utils import list_pdf_files
from utils.exceptions import IngestionError
from config.configs import SOURCE_DIR, PROCESSED_DIR

from utils.metadata_tracker import (
    load_ingestion_state,
    save_ingestion_state,
    is_already_ingested,
    update_ingestion_record,
)
from utils.file_utils import calculate_file_md5

def generate_doc_id(filename):
    return os.path.splitext(filename)[0].replace(" ", "_")

def ingest_pdf(file_path, doc_id, session_dir, logger):
    try:
        loader = PyMuPDFLoader(file_path)
        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "],
        )
        all_chunks = []
        for page_num, page in enumerate(pages, start=1):
            chunks = splitter.split_documents([page])
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_id": f"{doc_id}_pg{page_num}_ch{i+1}",
                    "doc_id": doc_id,
                    "page_num": page_num,
                    "source": file_path
                })
                all_chunks.append(chunk)

        # Save processed chunks
        output_path = os.path.join(session_dir, f"{doc_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([doc.dict() for doc in all_chunks], f, indent=2, ensure_ascii=False)

        logger.info(f"Processed {file_path} - {len(all_chunks)} chunks.")
        return all_chunks

    except Exception as e:
        logger.exception(f"Failed to ingest {file_path}")
        raise IngestionError(f"Failed to process {file_path}") from e


def main():
    session_id = generate_session_id()
    logger = setup_logger(session_id)
    logger.info(f"Starting ingestion session: {session_id}")

    state = load_ingestion_state()
    updated = False

    pdf_files = list_pdf_files(SOURCE_DIR)
    if not pdf_files:
        logger.warning("No PDF files found in source directory.")
        return

    session_dir = os.path.join(PROCESSED_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    for filename in pdf_files:
        file_path = os.path.join(SOURCE_DIR, filename)
        checksum = calculate_file_md5(file_path)

        if is_already_ingested(filename, checksum, state):
            logger.info(f"Skipping (no change): {filename}")
            continue

        doc_id = generate_doc_id(filename)
        try:
            ingest_pdf(file_path, doc_id, session_dir, logger)
            update_ingestion_record(filename, checksum, session_id, state)
            updated = True
        except IngestionError as e:
            logger.warning(f"Skipped due to error: {filename}")

    if updated:
        save_ingestion_state(state)
        logger.info("Updated ingestion_state.json")

    logger.info("Ingestion session complete.")


if __name__ == "__main__":
    main()
