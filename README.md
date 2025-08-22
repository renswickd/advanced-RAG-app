# Advance-RAG: Advanced Retrieval-Augmented Generation Platform

## Overview

Advance-RAG is a modular, building, deploying, and managing retrieval-augmented generation (RAG) applications. It enables users to ingest large collections of documents, index them into a vector store, and interact with the content through a conversational AI interface. The system is designed for extensibility, observability, and ease of use for both administrators (content providers) and end-users.

---

## Features

- **Document Ingestion:** Upload and process PDF documents, chunk text, and update the vector store (FAISS).
- **Semantic Search:** Retrieve relevant document chunks using vector similarity and metadata filtering.
- **Conversational Agent:** ChatGPT-like interface for users to ask questions and receive answers grounded in ingested documents.
- **Reference Display:** Shows source document chunks used to generate each answer.
- **Admin & User Modes:** Separate tabs for ingestion (admin) and chat (user).
- **Modern UI:** Streamlit-based, scrollable chat and reference panels, sample prompt cards, and responsive design.

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** (Frontend UI)
- **FAISS** (Vector store for semantic search)
- **LangChain** (LLM and agent orchestration)
- **PyMuPDF** (PDF parsing)
- **Custom Logging & Exception Handling**

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- (Optional) API keys for LLM providers if using external LLMs
- (Optional) Docker for containerized deployment

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/advance-rag.git
   cd advance-rag
   ```
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set environment variables**

Create a `.env` file in the root directory and add Groq API key or configuration.

### Running the Application
Start the Streamlit UI:
    ```bash
    streamlit run ui.py
    ```
 - The UI will open in your browser (default: `http://localhost:8501`)

### Usage

#### Ingestion Tab (Admin/Content Provider)
 - Upload one or more PDF files.
 - Click "Ingest Documents" to process and index them into the vector store.
 - View ingestion status and logs.

#### Chat Tab (User)
 - Use sample prompt cards or type your own question.
 - View the conversation in a scrollable chat window (most recent at the top).
 - See references for each answer in the right column, including document, page,  - score, and chunk content.

