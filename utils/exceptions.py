class RAGException(Exception):
    """Base exception class for RAG application."""
    pass

class DocumentProcessingError(RAGException):
    """Exception raised when document processing fails."""
    pass

class ChatProcessingError(RAGException):
    """Exception raised when chat processing fails."""
    pass

class SessionInitializationError(RAGException):
    """Exception raised when session initialization fails."""
    pass

class IngestionError(RAGException):
    """Exception raised when document ingestion fails."""
    pass

class RetrievalError(RAGException):
    """Exception raised when document retrieval fails."""
    pass

class ConfigurationError(RAGException):
    """Exception raised when configuration is invalid."""
    pass
