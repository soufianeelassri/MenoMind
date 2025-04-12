import os
from langchain_chroma import Chroma
from models.embedding_model import embedding_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "outputs", "chroma_db")

vectorstore = Chroma(
    collection_name="mm_rag_vectorstore",
    embedding_function=embedding_model,
    persist_directory=CHROMA_DB_DIR
)

retriever = vectorstore.as_retriever()
