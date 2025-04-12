import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class TableSummarizer:
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
             """You are MenoTableMaster, an AI assistant specializing in interpreting and summarizing medical research tables related to menopause. 

            You will be shown table data along with relevant metadata such as the table's context, title, and source.

            **Your job is to write a concise, medically accurate summary based on the provided table and its metadata.**

            Your summary must:
            1. Focus on the key data points, trends, and relationships shown in the table.
            2. Incorporate relevant metadata to inform the understanding of the table's context (e.g., table title, context).
            3. Highlight any statistical information or significant findings presented in the table.
            4. Be concise and medically relevant, focusing on aspects related to menopause, its symptoms, treatments, or relevant findings.
            5. Avoid referencing the input directly; keep the summary self-contained.

            Keep your summary medically accurate and relevant to menopause-related research."""),
            ("human", "{table_data}\n\\Metadata:"),
            ("human", "Metadata:\n{metadata}")
        ])

        self.summarizer_chain = self.prompt_template | self.llm | StrOutputParser()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, data: str, metadata: dict):
        self.logger.info("Generating summary for table...")

        try:
            metadata_text = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
            summary = self.summarizer_chain.invoke({
                "table_data": data,
                "metadata": metadata_text
            })
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    def summarize_tables(self, table_entries):
        summaries = []
        self.logger.info(f"Started generating summaries for {len(table_entries)} tables.")

        for idx, entry in enumerate(table_entries, 1):
            self.logger.info(f"Processing table {idx}/{len(table_entries)}")

            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    self.logger.info(f"Rate limit hit. Sleeping for {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
                self.first_request_time = time.time()
                self.request_counter = 0

            try:
                data = entry["content"].get("text", entry["content"].get("html"))
                metadata = entry.get("metadata")
                summary = self.generate_summary(data, metadata)
                if summary:
                    summaries.append({
                        "summary": summary,
                        "metadata": metadata
                    })
                    self.logger.info(f"Summary for table {idx} completed.")
                else:
                    self.logger.warning(f"No summary generated for table {idx}.")
            except Exception as e:
                self.logger.error(f"Error summarizing table {idx}: {e}")

            self.request_counter += 1

        return summaries