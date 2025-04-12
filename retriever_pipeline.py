import os
from dotenv import load_dotenv
from huggingface_hub import login
from processors.pdf_processor import PDFProcessor
from processors.image_cleaner import ImageCleaner
from processors.text_splitter import TextSplitter
from summarization.summarize_texts import TextSummarizer
from summarization.summarize_tables import TableSummarizer
from summarization.summarize_images import ImageSummarizer
from langchain_huggingface import HuggingFaceEmbeddings
from retrieval.multi_vector_indexer import MultiVectorRetrieverBuilder
from langchain_chroma import Chroma
from langchain.docstore.document import Document
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
hf_api_token = os.getenv("HF_API_TOKEN")

login(hf_api_token)

logger.info("Processing PDFs...")
pdf_processor = PDFProcessor("./data/test_pdfs")
text_elements, table_elements = pdf_processor.process_pdfs()
logger.info(f"Extracted {len(text_elements)} text elements and {len(table_elements)} table elements")

logger.info("Processing tables...")
table_summarizer = TableSummarizer(gemini_api_key)
table_summaries = table_summarizer.generate_table_summaries(table_elements)
logger.info(f"Generated {len(table_summaries)} table summaries")

logger.info("Processing images...")
image_folder = "./data/images"
os.makedirs(image_folder, exist_ok=True)
image_processor = ImageCleaner(image_folder)
image_processor.process_images()

image_summarizer = ImageSummarizer(gemini_api_key)
image_summaries, img_base64_list = image_summarizer.generate_image_summaries(image_folder)
logger.info(f"Generated {len(image_summaries)} image summaries")

logger.info("Processing text...")
text_splitter = TextSplitter()
texts_token = text_splitter.enforce_token_size(text_elements)
logger.info(f"Split text into {len(texts_token)} chunks")

logger.info("Generating text summaries...")
text_summarizer = TextSummarizer(gemini_api_key)
text_summaries = text_summarizer.generate_text_summaries(texts_token)
logger.info("Text summary generated")

logger.info("Initializing vector store...")
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
chromadb_folder = "./outputs/chroma_db"
os.makedirs(chromadb_folder, exist_ok=True)
vectorstore = Chroma(collection_name="mm_rag_vectorstore", embedding_function=embeddings, persist_directory="./outputs/chroma_db")

documents = []
for i in range(len(texts_token)):
    if i < len(text_summaries):
        documents.append(
            Document(
                page_content=text_summaries[i],
                id=str(i)
            )
        )

for i, table_summary in enumerate(table_summaries):
    documents.append(
        Document(
            page_content=table_summary,
            id=str(i + len(texts_token))
        )
    )

logger.info(f"Created {len(documents)} documents for vector storage")

logger.info("Adding documents to vector store...")
vectorstore.add_documents(documents=documents)

logger.info("Documents added successfully")

logger.info("Building multi-vector retriever...")
builder = MultiVectorRetrieverBuilder(
    vectorstore, 
    text_summaries, 
    texts_token, 
    table_summaries, 
    table_elements, 
    image_summaries, 
    img_base64_list
)
retriever = builder.create_retriever()

logger.info("Finished Loading the Retriever")