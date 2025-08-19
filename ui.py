import os
import streamlit as st
from ingestion.ingest import main as ingest_main
from utils.logger import setup_logger, generate_session_id
from chat.conversational_agent import ConversationalAgent
from config.configs import SOURCE_DIR
import json
from datetime import datetime
import uuid

st.set_page_config(page_title="Advance-RAG Platform", layout="wide")

def set_user_query(prompt):
    st.session_state["pending_query"] = prompt

def save_reference_data(session_id: str, reference_id: str, references: list):
    """Save references to JSON file in reference_data/session_id directory"""
    ref_dir = os.path.join("data", "reference_data", session_id)
    os.makedirs(ref_dir, exist_ok=True)

    # Ensure references are complete before saving
    cleaned_references = []
    for ref in references:
        cleaned_ref = {
            "chunk_id": ref.get("chunk_id", ""),
            "doc_id": ref.get("doc_id", ""),
            "page_num": ref.get("page_num", 0),
            "content": ref.get("content", ""),
            "score": float(ref.get("score", 0.0))
        }
        cleaned_references.append(cleaned_ref)

    ref_file = os.path.join(ref_dir, f"{reference_id}.json")
    with open(ref_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_references, f, indent=2, ensure_ascii=False)

def load_reference_data(session_id: str, reference_id: str):
    """Load references from JSON file"""
    ref_file = os.path.join("data", "reference_data", session_id, f"{reference_id}.json")
    if os.path.exists(ref_file):
        with open(ref_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def generate_reference_id():
    """Generate a unique reference ID"""
    return f"ref_{datetime.now().strftime('%H%M%S')}_{uuid.uuid4().hex[:6]}"

tabs = st.tabs(["Ingestion", "Chat"])

# --- Ingestion Tab ---
with tabs[0]:
    st.header("Document Ingestion & Vector Store Management")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            file_path = os.path.join(SOURCE_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} file(s) to {SOURCE_DIR}")
    if st.button("Ingest Documents"):
        with st.spinner("Ingesting documents..."):
            try:
                ingest_main()
                st.success("Ingestion complete. Vector store updated.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")

# --- Chat Tab ---
with tabs[1]:
    st.header("Chat with Police Instructions Documents")

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    if "agent" not in st.session_state:
        st.session_state.agent = ConversationalAgent(st.session_state.session_id)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "reference_chunks" not in st.session_state:
        st.session_state.reference_chunks = []
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = ""
    if "current_reference_id" not in st.session_state:
        st.session_state.current_reference_id = None

    # Sample Questions
    with st.expander("Sample Prompt Templates", expanded=True):
        cols = st.columns(3)
        prompts = [
            "What is the use of Attention in Transformers?",
            "Summarize the main findings of the report.",
            "Which document discusses self-attention?",
        ]
        for i, prompt in enumerate(prompts):
            with cols[i]:
                if st.button(prompt, key=f"faq_{i}"):
                    st.session_state.pending_query = prompt

    # Layout: Chat and References
    chat_col, ref_col = st.columns([2, 1])

    # Chat Column
    with chat_col:
        st.subheader("Your Conversation History")

        # Input form for questions
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Ask your question...",
                value=st.session_state.pending_query,
                height=80,
                key="user_query",
                label_visibility="collapsed"
            )
            send = st.form_submit_button("Send", use_container_width=True)

        if send and user_input.strip():
            try:
                result = st.session_state.agent.respond(user_input)

                # Generate reference ID and save references
                reference_id = None
                if result.get("retrieved"):
                    reference_id = generate_reference_id()
                    save_reference_data(
                        st.session_state.session_id,
                        reference_id,
                        result["retrieved"]
                    )

                st.session_state.chat_history.append({
                    "sender": "user",
                    "message": user_input
                })
                st.session_state.chat_history.append({
                    "sender": "agent",
                    "message": result["reply"],
                    "reference_id": reference_id,
                    "references": result.get("retrieved", [])
                })
                st.session_state.reference_chunks = result.get("retrieved", [])
                st.session_state.pending_query = ""
                st.rerun()
            except Exception as e:
                st.error(f"Chat failed: {e}")

        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["sender"]):
                st.write(msg["message"])
                if msg["sender"] == "agent" and msg.get("reference_id"):
                    if st.button("📚 References", key=f"ref_{msg.get('reference_id')}", use_container_width=True):
                        st.session_state.current_reference_id = msg["reference_id"]
                        st.rerun()

    # Reference Column
    with ref_col:
        st.subheader("References")

        # Load and display references
        if st.session_state.current_reference_id:
            refs = load_reference_data(
                st.session_state.session_id,
                st.session_state.current_reference_id
            )
        else:
            refs = st.session_state.reference_chunks

        if refs:
            for ref in refs:
                with st.expander(f"{ref['doc_id']} - Page {ref['page_num']}", expanded=False):
                    st.write(ref['content'])
                    if 'score' in ref:
                        st.caption(f"Relevance Score: {ref['score']:.2f}")
        else:
            st.info("Click the reference button on any response to view its sources")
