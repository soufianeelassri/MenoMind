from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

class TextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = self.setup_logger()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def enforce_token_size(self, text_elements):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len
        )

        processed_texts = []
        for element in text_elements:
            split_texts = text_splitter.split_text(element["content"])
            for chunk in split_texts:
                processed_texts.append({"content": chunk})

        self.logger.info(f"No of Textual Elements: {len(text_elements)}")
        self.logger.info(f"No of Text Chunks after Splitting: {len(processed_texts)}")

        return processed_texts