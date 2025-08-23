# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/source_documents \
    data/processed_documents \
    data/vector_store \
    data/reference_data \
    logs

# Expose Streamlit port
EXPOSE 8501

# Set environment variables
ENV SOURCE_DIR=/app/data/source_documents
ENV PROCESSED_DIR=/app/data/processed_documents
ENV VECTOR_STORE_DIR=/app/data/vector_store
ENV REFERENCE_DATA_DIR=/app/data/reference_data
ENV LOGS_DIR=/app/logs

# Command to run the application
CMD ["streamlit", "run", "ui.py", "--server.address=0.0.0.0"]