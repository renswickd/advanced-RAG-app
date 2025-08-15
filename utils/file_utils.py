import os
import hashlib

def list_pdf_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

def calculate_file_md5(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
