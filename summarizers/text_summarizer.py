import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class TextSummarizer:
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
             """You are MenoSummarizer, an AI assistant specializing in summarizing medical research related to menopause. 

            You will be shown a short text from a scientific publication, along with relevant metadata such as section title, context, and source.

            **Your job is to write a concise, medically accurate summary of the provided content using the metadata.**

            Your summary must:
            1. Clearly convey the main points of the text.
            2. Incorporate metadata to improve context understanding (e.g., section title, context).
            3. Focus on menopause-related aspects such as symptoms, hormonal changes, or relevant interventions.
            4. Avoid introducing new information beyond the provided text and metadata.
            5. Be useful for determining relevance to menopause research queries.

            Keep your summary self-contained and avoid referring to the provided text explicitly."""),
            ("human", "{text}\n\\Metadata:"),
            ("human", "Metadata:\n{metadata}")
            ])

        self.summarizer_chain = self.prompt_template | self.llm | StrOutputParser()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, content: str, metadata: dict):
        self.logger.info("Generating summary for text...")

        try:
            metadata_text = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
            summary = self.summarizer_chain.invoke({
                "text": content,
                "metadata": metadata_text
            })
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    def summarize_texts(self, text_entries):
        summaries = []
        self.logger.info(f"Summarizing {len(text_entries)} text blocks.")

        for idx, entry in enumerate(text_entries, 1):
            self.logger.info(f"Processing text {idx}/{len(text_entries)}")

            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    self.logger.info(f"Rate limit hit. Sleeping for {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
                self.first_request_time = time.time()
                self.request_counter = 0

            try:
                content = entry.page_content
                metadata = entry.metadata
                summary = self.generate_summary(content, metadata)
                if summary:
                    summaries.append({
                        "summary": summary,
                        "metadata": metadata
                    })
                    self.logger.info(f"Summary for text {idx} completed.")
                else:
                    self.logger.warning(f"No summary generated for text {idx}.")
            except Exception as e:
                self.logger.error(f"Error summarizing text {idx}: {e}")

            self.request_counter += 1

        return summaries