# directory configurations
SOURCE_DIR = "data/source_data"
PROCESSED_DIR = "data/processed_data"
VECTOR_STORE_DIR = "vector_store/faiss_index"

# state file for tracking ingestion
STATE_FILE = "metadata/ingestion_state.json"

# Maximum number of session directories to keep and monitor
MAX_SESSIONS_TO_KEEP = 5

# LLM configuration
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

# Retrieval configuration
TOP_K_DEFAULT = 5
SCORE_THRESHOLD_DEFAULT = 0.5


