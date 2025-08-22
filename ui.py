import os
import streamlit as st
from chat.conversational_agent import ConversationalAgent
from utils.logger import generate_session_id, setup_logger
from utils.exceptions import (
    DocumentProcessingError, 
    SessionInitializationError,
)
from ingestion.ingest import main as ingest_main
from config.configs import SOURCE_DIR
import logging

# Initialize logging
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

try:
    logger = setup_logger(st.session_state.session_id)
except Exception as e:
    st.error(f"Failed to initialize logging: {str(e)}")
    st.stop()

PROMPT_TEMPLATES = [
    {
        "title": "Statement Modification",
        "prompt": "From my experience and understanding I have wriiten below as my project abstract \n attention refers to a mechanism where the output is produced by the dot product of the input, representing the similarity between locations in the input sequence\nWrite me expand my abstarct section for my thesis."
    },
    {
        "title": "Evidence Handling",
        "prompt": "Provide evidence for the following statement: 'Llama uses self-attention to compute a representation of the input sequence.'"
    },
    {
        "title": "Find Relevant Information",
        "prompt": "Help me to find relevant information about the following topic: 'The impact of attention mechanisms in neural networks'."
    }
]

# Initialize session state
def init_session_state():
    """Initialize all session state variables with error handling"""
    try:
        defaults = {
            "session_id": st.session_state.session_id,
            "chat_history": [],
            "agent": None,
            "current_prompt": "",  # Make sure this is initialized
            "max_references": 3
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
                logger.info(f"Initialized session state: {key}")

        if st.session_state.agent is None:
            logger.info("Initializing conversational agent")
            st.session_state.agent = ConversationalAgent(st.session_state.session_id)
            
    except Exception as e:
        logger.error(f"Session initialization error: {str(e)}")
        raise SessionInitializationError(f"Failed to initialize session: {str(e)}")

try:
    # Page configuration
    st.set_page_config(
        page_title="Internal Document Assistant",
        page_icon=":robot:",
        layout="wide"
    )

    # Initialize the app state
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.title("Doc Assistant")
        logger.debug("Rendering sidebar")

        # Navigation
        page = st.radio("", ["Chat", "Document Upload"])
        logger.info(f"Selected page: {page}")

        if page == "Chat":
            st.markdown("### Prompt Templates")
            
            for template in PROMPT_TEMPLATES:
                with st.expander(f"📋 {template['title']}", expanded=False):
                    st.markdown(f"*{template['prompt']}*")
                    if st.button("Use Template", key=f"btn_{template['title']}"):
                        logger.info(f"Template selected: {template['title']}")
                        # Update session state
                        if "current_prompt" not in st.session_state:
                            st.session_state.current_prompt = ""
                        st.session_state.current_prompt = template['prompt']
                        # Force a rerun to update the chat interface
                        st.rerun()

    # Main content
    if page == "Document Upload":
        st.header("Document Upload")
        logger.info("Accessing document upload page")

        uploaded_files = st.file_uploader(
            "Upload Documents to Update the Knowledge Base",
            type=["pdf"],
            accept_multiple_files=True
        )

        if uploaded_files:
            logger.info(f"Received {len(uploaded_files)} files for upload")
            
            if st.button("Process Documents", type="primary"):
                with st.spinner("Processing..."):
                    try:
                        for file in uploaded_files:
                            file_path = os.path.join(SOURCE_DIR, file.name)
                            logger.info(f"Processing file: {file.name}")
                            
                            try:
                                with open(file_path, "wb") as f:
                                    f.write(file.getbuffer())
                                logger.debug(f"Saved file: {file_path}")
                            except IOError as e:
                                logger.error(f"Failed to save file {file.name}: {str(e)}")
                                raise DocumentProcessingError(f"Failed to save {file.name}: {str(e)}")
                                
                        ingest_main()
                        logger.info("Document processing completed successfully")
                        st.success("Documents processed successfully!")
                        
                    except Exception as e:
                        logger.error(f"Document processing error: {str(e)}")
                        st.error(f"Error processing documents: {str(e)}")

    else:  # Chat interface
        st.header("Internal Document Assistant")
        logger.info("Accessing chat interface")

        # Chat messages area
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message.get("references"):
                    with st.expander("📚 View Sources", expanded=False):
                        try:
                            refs = sorted(
                                message["references"],
                                key=lambda x: float(x.get('score', 0)),
                                reverse=True
                            )[:st.session_state.max_references]

                            docs = {}
                            for ref in refs:
                                doc_id = ref["doc_id"]
                                if doc_id not in docs:
                                    docs[doc_id] = []
                                docs[doc_id].append(ref)

                            for doc_id, doc_refs in docs.items():
                                with st.expander(f"📄 {doc_id}", expanded=False):
                                    for idx, ref in enumerate(doc_refs, 1):
                                        with st.expander(f"Reference {idx} (Page {ref['page_num']})", expanded=False):
                                            try:
                                                score = float(ref.get('score', 0))
                                                score = min(max(score, 0), 1)
                                                st.markdown("**Relevance Score:**")
                                                st.progress(score)
                                                st.markdown(f"Score: {score:.2%}")
                                            except (ValueError, TypeError) as e:
                                                logger.warning(f"Invalid score format: {str(e)}")
                                                st.markdown("**Relevance Score:** Not available")

                                            st.markdown("**Content:**")
                                            st.markdown(f"```{ref['content']}```")
                        except Exception as e:
                            logger.error(f"Error displaying references: {str(e)}")
                            st.error("Error displaying references")

        # Chat input handling
        prompt = None
        
        # Check for template prompt
        if st.session_state.get("current_prompt"):
            prompt = st.session_state.current_prompt
            # Clear the current prompt after using it
            st.session_state.current_prompt = ""
            logger.info(f"Using template prompt: {prompt[:50]}...")
        else:
            # Regular chat input
            prompt = st.chat_input(placeholder="Ask about internal documents...")

        if prompt:
            logger.info(f"Processing prompt: {prompt[:50]}...")
            
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt
            })

            try:
                with st.spinner("Thinking..."):
                    response = st.session_state.agent.respond(prompt)
                    logger.info("Generated response successfully")

                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response["reply"],
                        "references": response.get("retrieved", [])
                    })
                    
                # Force UI refresh
                st.rerun()
                
            except Exception as e:
                logger.error(f"Chat processing error: {str(e)}")
                st.error(f"Error generating response: {str(e)}")
                # Remove failed interaction from chat history
                st.session_state.chat_history.pop()

except Exception as e:
    logger.critical(f"Application error: {str(e)}")
    st.error("An unexpected error occurred. Please refresh the page and try again.")
