import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ImageSummarizer:
    def __init__(self, api_key, model="gemini-2.0-flash", max_requests_per_minute=15):
        self.api_key = api_key
        self.model = model
        self.max_requests_per_minute = max_requests_per_minute
        self.first_request_time = time.time()
        self.request_counter = 0
        self.logger = self.setup_logger()

        self.llm = ChatGoogleGenerativeAI(api_key=self.api_key, model=self.model)

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", 
            """You are MenoVision, an AI assistant specializing in summarizing medical research figures for a Retrieval-Augmented Generation (RAG) system focused on menopause-related literature.

            You will be shown an image extracted from a scientific publication, along with relevant metadata such as figure number, caption, and source context.

            **Your job is to write a concise and medically relevant summary based on the image and metadata.**

            Your summary must:
            1. Identify the type of figure (e.g., scatter plot, radiograph).
            2. Highlight key data points, variables, or anatomical structures.
            3. Describe any trends or relationships visualized.
            4. Include statistical indicators (if any).
            5. Be useful for determining relevance to menopause research queries.

            Keep your summary self-contained and do not refer to “the image” or “this figure.”"""),
            ("human", "{image}\n\\Metadata:"),
            ("human", "Metadata:\n{metadata}")
        ])

        self.summarizer_chain = self.prompt_template | self.llm | StrOutputParser()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, base64_str, metadata: dict):
        self.logger.info("Generating image summary...")

        try:
            content = {
                "mime_type": "image/jpeg",
                "data": base64_str
            }
            metadata_text = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
            summary = self.summarizer_chain.invoke({
                "image": content,
                "metadata": metadata_text
            })
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    def summarize_images(self, image_entries):
        summaries = []

        self.logger.info(f"Summarizing {len(image_entries)} images.")

        for idx, entry in enumerate(image_entries, 1):
            self.logger.info(f"Processing image {idx}/{len(image_entries)}")

            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    self.logger.info(f"Rate limit hit. Sleeping for {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
                self.first_request_time = time.time()
                self.request_counter = 0

            try:
                base64_img = entry["content"]
                metadata = entry["metadata"]
                summary = self.generate_summary(base64_img, metadata)
                if summary:
                    summaries.append({
                        "summary": summary,
                        "metadata": metadata
                    })
                    self.logger.info(f"Summary for image {idx} completed.")
                else:
                    self.logger.warning(f"Summary for image {idx} was not generated.")
            except Exception as e:
                self.logger.error(f"Error summarizing image {idx}: {e}")

            self.request_counter += 1

        return summaries, [entry["content"] for entry in image_entries]