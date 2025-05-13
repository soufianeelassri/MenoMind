import os
import json
import logging
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import CompositeElement, Element

os.environ["TABLE_IMAGE_CROP_PAD"] = "1"
os.environ["EXTRACT_IMAGE_BLOCK_CROP_HORIZONTAL_PAD"] = "20"
os.environ["EXTRACT_IMAGE_BLOCK_CROP_VERTICAL_PAD"] = "10"

class PDFProcessor:
    def __init__(self, pdf_folder):
        self.pdf_folder = pdf_folder
        self.logger = self.setup_logger()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        return logging.getLogger(__name__)

    def extract_pdf_elements(self, pdf_path):
        self.logger.info(f"Starting extraction for {pdf_path}")
        try:
            elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",
                languages=["eng"],
                infer_table_structure=True,
                extract_images_in_pdf=True,
                extract_image_block_types=["Image", "Table"],
                extract_image_block_to_payload=True,
                chunking_strategy="by_title",
                max_characters=1500,
                new_after_n_chars=1000,
                combine_text_under_n_chars=500
            )
        except Exception as e:
            self.logger.error(f"Error extracting from {pdf_path}: {e}")
            return [], [], []

        text_elements = []
        table_elements = []
        image_elements = []

        for element in elements:
            if isinstance(element, CompositeElement):
                 if hasattr(element.metadata, 'orig_elements') and element.metadata.orig_elements is not None:
                     for sub_element in element.metadata.orig_elements:
                         self._process_element(sub_element, pdf_path, text_elements, table_elements, image_elements)
                 else:
                      self._process_element(element, pdf_path, text_elements, table_elements, image_elements)
            else:
                self._process_element(element, pdf_path, text_elements, table_elements, image_elements)


        self.logger.info(f"Extraction completed for {pdf_path}")
        return text_elements, table_elements, image_elements

    def _process_element(self, element: Element, pdf_path, text_list, table_list, image_list):
        raw_metadata = vars(element.metadata) if element.metadata else {}
        raw_metadata["source_pdf"] = os.path.basename(pdf_path)
        raw_metadata["page_number"] = element.metadata.page_number if element.metadata and hasattr(element.metadata, 'page_number') else None
        metadata = self.serialize_metadata(raw_metadata)

        category = getattr(element, 'category', None)

        if category == "Table":
            table_data = {"text": element.text}
            if hasattr(element.metadata, "text_as_html") and element.metadata.text_as_html is not None:
                 table_data["html"] = element.metadata.text_as_html
            table_list.append({
                "content": table_data,
                "metadata": metadata
            })
        elif category == "Image":
            if hasattr(element.metadata, "image_base64") and element.metadata.image_base64 is not None:
                image_entry = {
                    "content": element.metadata.image_base64,
                    "metadata": metadata,
                }
                image_list.append(image_entry)
        elif hasattr(element, "text"):
            text_list.append({
                "content": element.text,
                "metadata": metadata
            })


    def serialize_metadata(self, metadata):
        clean_metadata = {}
        for key, value in metadata.items():
            try:
                json.dumps(value)
                clean_metadata[key] = value
            except TypeError:
                if hasattr(value, "to_dict"):
                    clean_metadata[key] = value.to_dict()
                else:
                    clean_metadata[key] = str(value)
        return clean_metadata


    def process_pdfs(self):
        all_text_elements = []
        all_table_elements = []
        all_image_elements = []

        if not os.path.isdir(self.pdf_folder):
             self.logger.error(f"PDF folder not found: {self.pdf_folder}")
             return [], [], []

        for file_name in os.listdir(self.pdf_folder):
            if file_name.endswith(".pdf"):
                pdf_path = os.path.join(self.pdf_folder, file_name)
                self.logger.info(f"Processing {file_name}")

                try:
                    text, tables, images = self.extract_pdf_elements(pdf_path)
                    all_text_elements.extend(text)
                    all_table_elements.extend(tables)
                    all_image_elements.extend(images)
                except Exception as e:
                    self.logger.error(f"Skipping {file_name} due to error: {e}")

        self.logger.info(f"Extracted {len(all_text_elements)} text elements, {len(all_table_elements)} table elements and {len(all_image_elements)} images elements.")

        return all_text_elements, all_table_elements, all_image_elements