import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from models.prompt_templates import image_summarizer_prompt_template
from langchain_core.output_parsers import StrOutputParser

class ImageSummarizer:
    def __init__(self, api_key, model="gemini-2.0-flash", max_requests_per_minute=14):
        self.api_key = api_key
        self.model = model
        self.max_requests_per_minute = max_requests_per_minute
        self.first_request_time = time.time()
        self.request_counter = 0

        self.llm = ChatGoogleGenerativeAI(api_key=self.api_key, model=self.model)
        self.summarizer_chain = image_summarizer_prompt_template | self.llm | StrOutputParser()

        self.logger = self.setup_logger()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, base64_str: str, metadata: dict):
        self.logger.debug("Generating image summary...")

        metadata_text = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
        summary = self.summarizer_chain.invoke({
            "image": base64_str,
            "metadata": metadata_text
        })
        return summary

    def summarize_images(self, image_entries):
        summaries = []
        img_base64_list = []

        self.logger.info(f"Summarizing {len(image_entries)} images.")

        for idx, entry in enumerate(image_entries, 1):
            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    self.logger.info(f"Rate limit hit. Sleeping for {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
                self.first_request_time = time.time()
                self.request_counter = 0

            self.logger.info(f"Processing image {idx}/{len(image_entries)}")

            base64_img = entry.get("content")
            metadata = entry.get("metadata")

            summary = self.generate_summary(base64_img, metadata)
            summaries.append({
                "summary": summary,
                "metadata": metadata
            })
            img_base64_list.append(base64_img)
            self.logger.info(f"Summary for image {idx} completed.")

            self.request_counter += 1

        return summaries, img_base64_list