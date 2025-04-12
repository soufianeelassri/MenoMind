import os
from dotenv import load_dotenv
from huggingface_hub import login
from processors.pdf_processor import PDFProcessor
from utils.text_splitter import TextSplitter
from summarizers.text_summarizer import TextSummarizer
from summarizers.table_summarizer import TableSummarizer
from summarizers.image_summarizer import ImageSummarizer
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
hf_api_token = os.getenv("HF_API_TOKEN")

login(hf_api_token)

pdf_processor = PDFProcessor("../data/test_pdfs")
text_elements, table_elements, images_elements = pdf_processor.process_pdfs()

text_splitter = TextSplitter()
text_tokens = text_splitter.enforce_token_size(text_elements)

text_summarizer = TextSummarizer(gemini_api_key)
text_summaries = text_summarizer.summarize_texts(text_tokens)

table_summarizer = TableSummarizer(gemini_api_key)
table_summaries = table_summarizer.summarize_tables(table_elements)

image_summarizer = ImageSummarizer(gemini_api_key)
image_summaries, img_base64_list = image_summarizer.summarize_images(images_elements)

logger.info("Document processing completed.")

documents = []
for i, (text_summary, text_element) in enumerate(zip(text_summaries, text_elements)):
    documents.append({
        'text_summary': text_summary,
        'text_element': text_tokens,
    })

for i, (table_summary, table_element) in enumerate(zip(table_summaries, table_elements)):
    documents.append({
        'table_summary': table_summary,
        'table_element': table_element,
    })

for i, (image_summary, img_base64) in enumerate(zip(image_summaries, img_base64_list)):
    documents.append({
        'image_summary': image_summary,
        'img_base64': img_base64,
    })

logger.info("Documents processed and ready for retriever setup.")