import os
from dotenv import load_dotenv
from huggingface_hub import login
import logging

from processors.pdf_processor import PDFProcessor
from utils.text_splitter import TextSplitter
from summarizers.table_summarizer import TableSummarizer
from summarizers.image_summarizer import ImageSummarizer

from config import SOURCE_PDF_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
hf_api_token = os.getenv("HF_API_TOKEN")

login(hf_api_token)
logger.info("Hugging Face login successful.")

logger.info(f"Starting PDF processing from: {SOURCE_PDF_DIR}")
pdf_processor = PDFProcessor(SOURCE_PDF_DIR)
text_elements, table_elements, images_elements = pdf_processor.process_pdfs()

logger.info("Splitting text elements...")
text_splitter = TextSplitter()
text_chunks = text_splitter.enforce_token_size(text_elements)

logger.info("Summarizing table elements...")
table_summarizer = TableSummarizer(gemini_api_key)
table_summaries = table_summarizer.summarize_tables(table_elements)

logger.info("Summarizing image elements...")
image_summarizer = ImageSummarizer(gemini_api_key)
image_summaries, img_base64_list = image_summarizer.summarize_images(images_elements)

logger.info("Document processing completed.")

documents = []

for text_chunk in text_chunks:
    documents.append({
        'type': 'text',
        'text_element': text_chunk.page_content,
        'metadata': text_chunk.metadata 
    })

for table_summary_entry, table_element_entry in zip(table_summaries, table_elements):
    documents.append({
        'type': 'table',
        'table_summary': table_summary_entry,
        'table_element': table_element_entry['content'], 
        'metadata': table_element_entry['metadata'] 
    })

for image_summary_entry, img_base64_string in zip(image_summaries, img_base64_list):
    documents.append({
        'type': 'image',
        'image_summary': image_summary_entry,
        'img_base64': img_base64_string,
        'metadata': image_summary_entry['metadata']
    })

logger.info(f"Processed {len(documents)} total document entries.")
