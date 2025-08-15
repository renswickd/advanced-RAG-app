import os
from typing import List
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from config.configs import VECTOR_STORE_DIR

def _get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def _vector_store_exists():
    return os.path.exists(os.path.join(VECTOR_STORE_DIR, "index.faiss"))

def _load_vector_store():
    embeddings = _get_embedding_model()
    return FAISS.load_local(VECTOR_STORE_DIR, embeddings, allow_dangerous_deserialization=True)

def _save_vector_store(vector_store: FAISS):
    vector_store.save_local(VECTOR_STORE_DIR)

def create_or_update_vector_store(new_documents: List[Document]):
    if not new_documents:
        return None

    if _vector_store_exists():
        db = _load_vector_store()
        db.add_documents(new_documents)
    else:
        db = FAISS.from_documents(new_documents, _get_embedding_model())

    _save_vector_store(db)
    return db
