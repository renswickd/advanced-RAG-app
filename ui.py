import os
import streamlit as st
from ingestion.ingest import main as ingest_main
from chat.conversational_agent import ConversationalAgent
from config.configs import SOURCE_DIR

st.set_page_config(page_title="Advance-RAG Platform", layout="wide")

def set_user_query(prompt):
    st.session_state["pending_query"] = prompt

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
    st.header("Chat with Your Documents")

    # Session state defaults
    defaults = {
        "agent": ConversationalAgent("streamlit_session"),
        "chat_history": [],
        "reference_chunks": [],
        "pending_query": ""
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Sample Questions
    with st.expander("Sample Questions", expanded=True):
        cols = st.columns(3)
        prompts = [
            "What is the use of Attention in Transformers?",
            "Summarize the main findings of the report.",
            "Which document discusses self-attention?",
        ]
        for i, prompt in enumerate(prompts):
            with cols[i]:
                st.button(prompt, key=f"faq_{i}", on_click=set_user_query, args=(prompt,))

    # Layout: Chat and References
    chat_col, ref_col = st.columns([2, 1])

    with chat_col:
        st.subheader("Chat History")

        # BEGIN: Scrollable chat window
        chat_html = "<div style='height:400px; overflow-y:auto; padding:10px; border:1px solid #e0e0e0; border-radius:8px; background-color:#f8fafc;'>"
        for entry in st.session_state.chat_history:
            sender = entry["sender"]
            message = entry["message"]
            align = "right" if sender == "user" else "left"
            bg = "#e3f2fd" if sender == "user" else "#f1f8e9"
            chat_html += f"<div style='text-align:{align}; background:{bg}; padding:8px; border-radius:10px; margin-bottom:5px;'>"
            chat_html += f"<strong>{sender.capitalize()}:</strong> {message}</div>"
        chat_html += "</div>"

        st.markdown(chat_html, unsafe_allow_html=True)

        # --- Input Field with Send Button on Right ---
        st.markdown("**Your question:**")
        with st.form("chat_form", clear_on_submit=True):
            input_col, send_col = st.columns([9, 1])
            with input_col:
                user_input = st.text_area(
                    label="Ask your question...",
                    key="user_query",
                    label_visibility="collapsed",
                    value=st.session_state.pending_query,
                    height=80
                )
            with send_col:
                send = st.form_submit_button(label="Send", icon="⬆️", use_container_width=True)

        if send and user_input.strip():
            st.session_state.pending_query = user_input
            try:
                result = st.session_state.agent.respond(user_input)
                st.session_state.chat_history.append({"sender": "user", "message": user_input})
                st.session_state.chat_history.append({"sender": "agent", "message": result["reply"]})
                st.session_state.reference_chunks = result.get("retrieved", [])
            except Exception as e:
                st.error(f"Chat failed: {e}")
            finally:
                st.session_state.pending_query = ""
                st.rerun()

    # --- References ---
    with ref_col:
        st.subheader("References")

        refs = st.session_state.reference_chunks
        ref_html = "<div style='height:550px; overflow-y:auto; padding:10px; border:1px solid #e0e0e0; border-radius:8px; background-color:#f8fafc;'>"

        if refs:
            for ref in refs:
                doc = f"<strong>Document:</strong> {ref['doc_id']}<br>"
                page = f"<strong>Page:</strong> {ref['page_num']}<br>"
                score = f"<strong>Score:</strong> {ref.get('score', '')}<br>"
                content = f"<pre style='white-space: pre-wrap; word-wrap: break-word;'>{ref['content']}</pre><hr>"

                ref_html += doc + page + score + content
        else:
            ref_html += "<i>References for the latest answer will appear here.</i>"

        ref_html += "</div>"

        st.markdown(ref_html, unsafe_allow_html=True)
