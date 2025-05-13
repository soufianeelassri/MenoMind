import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCE_PDF_DIR = os.path.join(DATA_DIR, "test_pdfs")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHROMA_DB_DIR = os.path.join(OUTPUT_DIR, "chroma_db")

os.makedirs(CHROMA_DB_DIR, exist_ok=True)