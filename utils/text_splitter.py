from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from transformers import AutoTokenizer
import logging

class TextSplitter:
    def __init__(self, chunk_size=512, chunk_overlap=50, model_name='BAAI/bge-large-en-v1.5'):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.logger = self.setup_logger()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def length_function(self, text):
        return len(self.tokenizer.encode(text, truncation=False))


    def enforce_token_size(self, text_elements):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=self.length_function
        )

        processed_docs = []

        for element in text_elements:
            original_text = element.get("content")
            metadata = element.get("metadata")

            split_texts = text_splitter.split_text(original_text)

            for chunk in split_texts:
                doc = Document(page_content=chunk, metadata=metadata)
                processed_docs.append(doc)

        self.logger.info(f"Number of input elements: {len(text_elements)}")
        self.logger.info(f"Number of text chunks after splitting: {len(processed_docs)}")

        return processed_docs