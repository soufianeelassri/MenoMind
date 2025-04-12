import os
import time
import base64
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

class ImageSummarizer:
    def __init__(self, api_key, model="gemini-2.0-flash-lite", max_requests_per_minute=15):
        self.api_key = api_key
        self.model = model
        self.max_requests_per_minute = max_requests_per_minute
        self.first_request_time = time.time()
        self.request_counter = 0
        self.logger = self.setup_logger()

        self.llm = ChatGoogleGenerativeAI(api_key=self.api_key, model=self.model)

        self.prompt_template = PromptTemplate(
            input_variables=["element"],
            template = """
                You are MenoVision, an AI assistant specializing in describing and summarizing images from medical research papers related to menopause for a Retrieval-Augmented Generation (RAG) system. Your goal is to create summaries that allow users to quickly understand the content of the image and determine its relevance.

                Task:  Describe and summarize the following image from a menopause research paper. The summary should:

                1.  **State the type of image (e.g., "Lateral cephalometric radiograph," "Scatter plot," "Bar graph," "Schematic diagram").**
                2.  **Identify the key anatomical structures, variables, or data points displayed in the image.** Be specific (e.g., "Cervical vertebrae C2-C7," "Nasion-Sella line," "aBMD," "Neck Disability Index").
                3.  **Explain the purpose or message the image is intended to convey.** What relationship, trend, or finding is being illustrated?
                4.  **If the image contains data, describe the general trend or relationship visualized.** For example, "The scatter plot shows a negative correlation between BMD and Neck Disability Index."
                5.  **If the image contains statistical information (e.g., regression lines, confidence intervals), mention it.**
                6.  **Provide enough detail to allow a user to determine if the image is relevant to their search query about menopause, its symptoms, or its management.**
                7.  **Focus on medically-relevant aspects.**

                Image: {element}

                Summary:
                """
        )

        self.summarizer_chain = self.prompt_template | self.llm | StrOutputParser()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_image_summary(self, img_base64):
        self.logger.info("Generating summary for image.")

        try:
            summary = self.summarizer_chain.invoke({"element": img_base64})
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    def generate_image_summaries(self, image_folder):
        image_summaries = []
        img_base64_list = []

        try:
            for img_filename in os.listdir(image_folder):
                img_path = os.path.join(image_folder, img_filename)
                try:
                    with open(img_path, "rb") as img_file:
                        encoded = base64.b64encode(img_file.read()).decode("utf-8")
                        img_base64_list.append(encoded)
                except Exception as e:
                    self.logger.error(f"Error reading image {img_filename}: {e}")

        except FileNotFoundError:
            self.logger.error(f"Image folder not found: {image_folder}")
            return [], [] 

        self.logger.info(f"Started generating summaries for {len(img_base64_list)} images.")

        for idx, img_base64 in enumerate(img_base64_list, start=1):
            self.logger.info(f"Processing image {idx}/{len(img_base64_list)}")

            # Rate limiting
            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    sleep_time = 60 - elapsed
                    self.logger.info(f"Request limit reached, waiting for {sleep_time:.2f} seconds.")
                    time.sleep(sleep_time)
                self.request_counter = 0
                self.first_request_time = time.time()

            try:
                summary = self.generate_image_summary(img_base64)
                if summary:
                    image_summaries.append(summary)
                    self.logger.info(f"Summary for image {idx} generated.")
                else:
                    self.logger.warning(f"No summary generated for image {idx}.")
            except Exception as e:
                self.logger.error(f"Error processing image {idx}: {e}")

            self.request_counter += 1

        self.logger.info(f"Image summarization completed. {len(image_summaries)} summaries generated.")
        return image_summaries, img_base64_list