import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from models.prompt_templates import table_summarizer_prompt_template
from langchain_core.output_parsers import StrOutputParser

class TableSummarizer:
    def __init__(self, api_key, model="gemini-2.0-flash", max_requests_per_minute=14):
        self.api_key = api_key
        self.model = model
        self.max_requests_per_minute = max_requests_per_minute
        self.first_request_time = time.time()
        self.request_counter = 0

        self.llm = ChatGoogleGenerativeAI(api_key=self.api_key, model=self.model)
        self.summarizer_chain = table_summarizer_prompt_template | self.llm | StrOutputParser()

        self.logger = self.setup_logger()
        
    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, data: str, metadata: dict):
        self.logger.debug("Generating summary for table...")
        
        metadata_text = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
        summary = self.summarizer_chain.invoke({
            "table_data": data,
            "metadata": metadata_text
        })
        
        return summary

    def summarize_tables(self, table_entries):
        summaries = []
        self.logger.info(f"Started generating summaries for {len(table_entries)} tables.")

        for idx, entry in enumerate(table_entries, 1):
            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    self.logger.info(f"Rate limit hit. Sleeping for {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
                self.first_request_time = time.time()
                self.request_counter = 0

            self.logger.info(f"Processing table {idx}/{len(table_entries)}")

            content = entry.get("content")
            table_data_str = content.get("text", content.get("html"))
            metadata = entry.get("metadata")
            
            summary = self.generate_summary(table_data_str, metadata)
            summaries.append({
                "summary": summary,
                "metadata": metadata
            })
            self.logger.info(f"Summary for table {idx} completed.")
            
            self.request_counter += 1

        return summaries