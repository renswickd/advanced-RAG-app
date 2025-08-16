from langchain_groq import ChatGroq
from utils.logger import setup_logger
from utils.memory import create_memory
from utils.prompt_templates import CONV_SYSTEM_TEMPLATE, CONV_USER_QUERY_TEMPLATE
from utils.exceptions import RetrievalError, RAGException
from chat.retriever import retrieve
from config.configs import LLM_MODEL_NAME, MAX_MEMORY_TOKENS, MAX_BUFFER_SIZE, TOP_K_DEFAULT, SCORE_THRESHOLD_DEFAULT

class ConversationalAgent:
    def __init__(self, session_id):
        self.logger = setup_logger(session_id)
        self.llm = ChatGroq(model_name=LLM_MODEL_NAME, temperature=0)
        self.memory = create_memory(self.llm, max_token_limit=MAX_MEMORY_TOKENS, max_buffer_size=MAX_BUFFER_SIZE)
        # self.memory.llm = self.llm

    def respond(self, user_query):
        try:
            # Retrieval step
            chunks = retrieve(user_query, top_k=TOP_K_DEFAULT, score_threshold=SCORE_THRESHOLD_DEFAULT, logger=self.logger)

            # Format retrieved snippets
            snippet_text = "\n".join(
                f"[{c['doc_id']} pg {c['page_num']}] {c['content']}"
                for c in chunks
            )

            # Render prompt
            prompt = CONV_USER_QUERY_TEMPLATE.format(
                query=user_query,
                chat_history=self.memory.load_memory_variables({})["chat_history"],
                retrieved_chunks=snippet_text
            )

            # Generation
            response = self.llm.invoke([("system", CONV_SYSTEM_TEMPLATE), ("human", prompt)])
            reply = response.content

            # Update memory
            self.memory.save_context({"input": user_query}, {"output": reply})

            return {"reply": reply, "retrieved": chunks}

        except Exception as e:
            self.logger.exception("Conversation failed.")
            raise RAGException("Conversational pipeline error") from e
