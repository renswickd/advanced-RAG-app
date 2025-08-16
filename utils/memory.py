from langchain.memory import ConversationSummaryBufferMemory
from langchain_groq import ChatGroq
from utils.logger import setup_logger
from config.configs import MAX_BUFFER_SIZE, MAX_MEMORY_TOKENS

def create_memory(llm, max_buffer_size=MAX_BUFFER_SIZE, max_token_limit=MAX_MEMORY_TOKENS):
    """
    Returns a hybrid ConversationSummaryBufferMemory:
    - Keeps the last max_buffer_size messages intact
    - Summarizes older history when exceeding max_token_limit tokens
    """
    return ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=max_token_limit,
        max_buffer_size=max_buffer_size,
        memory_key="chat_history"
    )