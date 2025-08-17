import streamlit as st
from ingestion.ingest import main as ingest_main
from chat.conversational_agent import ConversationalAgent

st.set_page_config(page_title="Advance-RAG Platform", layout="wide")

tabs = st.tabs(["Ingestion", "Chat"])

# --- Ingestion Tab ---
with tabs[0]:
    st.header("Document Ingestion & Vector Store Management")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    if st.button("Ingest Documents"):
        # Save files to SOURCE_DIR, then run ingestion
        # (Implement file saving logic here)
        ingest_main()
        st.success("Ingestion complete. Vector store updated.")
    # Optionally show ingestion logs/status

# --- Chat Tab ---
with tabs[1]:
    st.header("Chat with Your Documents")
    st.markdown("Ask questions and get answers from your ingested documents.")
    # Sample FAQ/Prompt Cards
    st.subheader("Sample Questions")
    faq_prompts = [
        "What is the use of Attention in Transformers?",
        "Summarize the main findings of the report.",
        "Which document discusses self-attention?",
    ]
    cols = st.columns(len(faq_prompts))
    for i, prompt in enumerate(faq_prompts):
        with cols[i]:
            if st.button(prompt, key=f"faq_{i}"):
                st.session_state["user_query"] = prompt

    # Chat interface
    if "agent" not in st.session_state:
        st.session_state.agent = ConversationalAgent("streamlit_session")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.text_input("Your question:", key="user_query")
    allow_search = st.checkbox("Allow web search", value=True)
    if st.button("Send"):
        result = st.session_state.agent.respond(user_query)
        st.session_state.chat_history.append(("user", user_query))
        st.session_state.chat_history.append(("agent", result["reply"]))
        # Optionally display retrieved chunks

    # Display chat history (ChatGPT style)
    chat_html = "<div style='height:400px;overflow-y:auto;'>"
    for sender, msg in st.session_state.chat_history:
        align = "flex-end" if sender == "user" else "flex-start"
        bg = "#e3f2fd" if sender == "user" else "#f1f8e9"
        chat_html += f"<div style='display:flex;justify-content:{align};'><div style='background:{bg};padding:0.9em 1.2em;border-radius:16px;margin-bottom:0.5em;max-width:70%;'><b>{sender.capitalize()}:</b> {msg}</div></div>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)