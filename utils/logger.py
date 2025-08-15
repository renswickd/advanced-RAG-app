import os
import uuid
import logging
import shutil
from datetime import datetime
from utils.exceptions import SessionInitializationError
from config.configs import MAX_SESSIONS_TO_KEEP

def generate_session_id():
    """
    Generates a unique session ID based on timestamp and UUID.
    """
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def prune_old_sessions(folder_path: str, keep_last_n: int = MAX_SESSIONS_TO_KEEP):
    if not os.path.exists(folder_path):
        return

    # Sort folders/files by modified time (newest first)
    entries = sorted(
        [(entry, os.path.getmtime(os.path.join(folder_path, entry)))
         for entry in os.listdir(folder_path)],
        key=lambda x: x[1],
        reverse=True
    )

    # Delete older entries
    for entry, _ in entries[keep_last_n:]:
        full_path = os.path.join(folder_path, entry)
        try:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            elif os.path.isfile(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Warning: Failed to delete {full_path}: {e}")

def setup_directories(session_id: str):
    log_dir = os.path.join("logs")
    source_dir = os.path.join("data", "source_data")
    processed_dir = os.path.join("data", "processed_data")

    session_dir = os.path.join(processed_dir, session_id)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(source_dir, exist_ok=True)

    # Prune old logs and processed_data
    prune_old_sessions(log_dir)
    prune_old_sessions(processed_dir)

    return log_dir, session_dir

def setup_logger(session_id: str):
    """
    Sets up a session-specific logger that logs to both console and file.
    """
    try:
        log_dir, session_dir = setup_directories(session_id)
        log_path = os.path.join(log_dir, f"{session_id}.log")

        logger = logging.getLogger(session_id)
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers on reruns
        if logger.hasHandlers():
            logger.handlers.clear()

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File Handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        logger.info(f"Logger initialized for session: {session_id}")
        return logger #, session_dir

    except Exception as e:
        raise SessionInitializationError(
            "Failed to initialize logger.",
            details={"session_id": session_id, "error": str(e)}
        )
