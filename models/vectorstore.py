from langchain_chroma import Chroma
from models.embedding_model import embedding_model
from config import CHROMA_DB_DIR

vectorstore = Chroma(
    collection_name='menomind',
    embedding_function=embedding_model,
    persist_directory=CHROMA_DB_DIR
)

retriever = vectorstore.as_retriever()