import logging

from pipeline.processing import documents
from langchain.docstore.document import Document
from retriever.multi_vector_retriever import MultiVectorRetrieverBuilder
from langchain_community.vectorstores.utils import filter_complex_metadata
from models.vectorstore import vectorstore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger.info("Initializing vector store...")

logger.info(f"Adding {len(documents)} documents to vector store...")
vector_docs_for_chroma = []

for doc_entry in documents:
    summary = None
    metadata = doc_entry['metadata']
    doc_type = doc_entry['type']

    if doc_type == 'text':
        summary = doc_entry['text_element']
    elif doc_type == 'table':
        summary = doc_entry['table_summary']['summary']
    elif doc_type == 'image':
        summary = doc_entry['image_summary']['summary']

    vector_docs_for_chroma.append(Document(page_content=summary, metadata={'type': doc_type, **metadata}))

filtered_docs = filter_complex_metadata(vector_docs_for_chroma)

logger.info(f"Adding {len(filtered_docs)} summaries to Chroma.")
vectorstore.add_documents(filtered_docs)
logger.info("Documents added to Chroma vector store.")

logger.info("Building multi-vector retriever...")

raw_text_elements = [doc['text_element'] for doc in documents if doc['type'] == 'text']
raw_table_summaries = [doc['table_summary']['summary'] for doc in documents if doc['type'] == 'table']
raw_table_elements = [doc['table_element']['text'] for doc in documents if doc['type'] == 'table']
raw_image_summaries = [doc['image_summary']['summary'] for doc in documents if doc['type'] == 'image']
raw_img_base64_list = [doc['img_base64'] for doc in documents if doc['type'] == 'image']

builder = MultiVectorRetrieverBuilder(
    vectorstore=vectorstore,
    text_elements=raw_text_elements,
    text_summaries=[],
    table_summaries=raw_table_summaries,
    table_elements=raw_table_elements,
    image_summaries=raw_image_summaries,
    img_base64_list=raw_img_base64_list,
)

retriever = builder.create_retriever()
logger.info("Multi-vector Retriever created successfully.")