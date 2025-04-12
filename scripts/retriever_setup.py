import os
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from document_processing import documents
from langchain.docstore.document import Document
from retriever.multi_vector_retriever import MultiVectorRetrieverBuilder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger.info("Initializing vector store...")
embeddings = HuggingFaceEmbeddings(model_name='BAAI/bge-large-en-v1.5')
chromadb_folder = "../outputs/chroma_db"
os.makedirs(chromadb_folder, exist_ok=True)

vectorstore = Chroma(
    collection_name="mm_rag_vectorstore",
    embedding_function=embeddings,
    persist_directory=chromadb_folder
)

logger.info("Adding documents to vector store...")
vector_docs = []
for doc in documents:
    if 'text_summary' in doc:
        summary = doc['text_summary']['summary'] if isinstance(doc['text_summary'], dict) else doc['text_summary']
        vector_docs.append(Document(page_content=summary, metadata={'type': 'text'}))
    elif 'table_summary' in doc:
        summary = doc['table_summary']['summary'] if isinstance(doc['table_summary'], dict) else doc['table_summary']
        vector_docs.append(Document(page_content=summary, metadata={'type': 'table'}))
    elif 'image_summary' in doc:
        summary = doc['image_summary']['summary'] if isinstance(doc['image_summary'], dict) else doc['image_summary']
        vector_docs.append(Document(page_content=summary, metadata={'type': 'image'}))

vectorstore.add_documents(vector_docs)

logger.info("Building multi-vector retriever...")
builder = MultiVectorRetrieverBuilder(
    vectorstore=vectorstore,
    text_summaries=[
        doc['text_summary']['summary'] if isinstance(doc['text_summary'], dict) else doc['text_summary']
        for doc in documents if 'text_summary' in doc
    ],
    text_elements=[
        doc['text_element'] for doc in documents if 'text_element' in doc
    ],
    table_summaries=[
        doc['table_summary']['summary'] if isinstance(doc['table_summary'], dict) else doc['table_summary']
        for doc in documents if 'table_summary' in doc
    ],
    table_elements=[
        doc['table_element'] for doc in documents if 'table_element' in doc
    ],
    image_summaries=[
        doc['image_summary']['summary'] if isinstance(doc['image_summary'], dict) else doc['image_summary']
        for doc in documents if 'image_summary' in doc
    ],
    img_base64_list=[
        doc['img_base64'] for doc in documents if 'img_base64' in doc
    ]
)

retriever = builder.create_retriever()
logger.info("Finished loading the Retriever.")