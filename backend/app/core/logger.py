import logging
import sys
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate logs
    if logger.hasHandlers():
        return logger

    # Log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler("logs/ollama.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

llm_logger = setup_logger("llm_service")
