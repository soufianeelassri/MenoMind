import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCE_PDF_DIR = os.path.join(DATA_DIR, "test_pdfs")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHROMA_DB_DIR = os.path.join(OUTPUT_DIR, "chroma_db")

# Retrieval Settings
DEFAULT_RERANKING_ENABLED = True
DEFAULT_REPACKING_ENABLED = False
DEFAULT_REPACKING_METHOD = "similarity"  # options: "similarity" or "token_limit"
DEFAULT_MAX_TOKENS_PER_GROUP = 1500

os.makedirs(CHROMA_DB_DIR, exist_ok=True)