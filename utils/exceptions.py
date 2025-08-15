class RAGException(Exception):
    """
    Base class for all custom exceptions in the RAG pipeline.
    Provides a standard structure for logging and debugging errors.
    """
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} | Details: {self.details}"


class IngestionError(RAGException):
    """
    Raised when there is a failure in document ingestion.
    Example causes:
    - Invalid or corrupted PDF
    - File format not supported
    - Read permission denied
    """
    pass


class MetadataError(RAGException):
    """
    Raised when metadata extraction or validation fails.
    Example causes:
    - Missing required fields like doc_id, page number
    - Incorrect metadata format
    - Inconsistent or conflicting metadata
    """
    pass


class VectorStoreError(RAGException):
    """
    Raised when issues occur with vector store operations.
    Example causes:
    - FAISS index not found or corrupt
    - Failure to save/load index
    - Inconsistent dimension of embeddings
    """
    pass


class RetrievalError(RAGException):
    """
    Raised when the retriever fails to fetch relevant documents.
    Example causes:
    - Query leads to zero results
    - Retriever misconfiguration
    - Backend store unreachable
    """
    pass


class SessionInitializationError(RAGException):
    """
    Raised during issues initializing session directories or loggers.
    Example causes:
    - Filesystem permission errors
    - UUID collisions (rare)
    - Path not found
    """
    pass


class ConfigurationError(RAGException):
    """
    Raised when system or model configuration is invalid.
    Example causes:
    - Missing API keys or environment variables
    - Invalid chunk size or tokenizer errors
    """
    pass
