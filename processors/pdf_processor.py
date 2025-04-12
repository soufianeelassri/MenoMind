import os
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import CompositeElement, Table
import logging

class PDFProcessor:
    def __init__(self, pdf_folder):
        self.pdf_folder = pdf_folder
        self.logger = self.setup_logger()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def extract_pdf_elements(self, pdf_path):
        self.logger.info(f"Starting extraction for {pdf_path}")
        elements = partition_pdf(
            filename=pdf_path,
            extract_images_in_pdf=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=None,
            extract_image_block_to_payload=False,
            extract_image_block_output_dir="./data/images"
        )
        self.logger.info(f"Extraction completed for {pdf_path}")

        text_elements = []
        table_elements = []
        for element in elements:
            if isinstance(element, CompositeElement):
                for sub_element in element.metadata.orig_elements:
                    if isinstance(sub_element, Table):
                        table_elements.append({
                            "content": sub_element.text
                        })
                    elif hasattr(sub_element, "text"):
                        text_elements.append({
                            "content": sub_element.text
                        })

        return text_elements, table_elements

    def process_pdfs(self):
        all_text_elements = []
        all_table_elements = []

        for file_name in os.listdir(self.pdf_folder):
            if file_name.endswith('.pdf'):
                pdf_path = os.path.join(self.pdf_folder, file_name)
                self.logger.info(f"Processing {file_name}")
                text_elements, table_elements = self.extract_pdf_elements(pdf_path)
                all_text_elements.extend(text_elements)
                all_table_elements.extend(table_elements)

        return all_text_elements, all_table_elements