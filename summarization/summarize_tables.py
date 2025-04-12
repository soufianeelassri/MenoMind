import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

class TableSummarizer:
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
            You are MenoTableMaster, an AI expert in summarizing medical research tables related to menopause for a Retrieval-Augmented Generation (RAG) system. Your goal is to create summaries that enable accurate and efficient retrieval of the table's content.

            Task: Summarize the following table from a menopause research paper. The summary must:

            1.  **State the central topic or purpose of the table (e.g., "Demographic characteristics of study participants," "Comparison of treatment outcomes").**
            2.  **Clearly list the independent and dependent variables displayed in the table, including units of measurement where applicable (e.g., "Age (years)," "BMD (g/cm^2)," "NDI (score)").**
            3.  **Describe the groups or categories being compared (e.g., "Normal BMD," "Osteopenia," "Osteoporosis").**
            4.  **Identify the key summary statistics used (e.g., mean, standard deviation, median, interquartile range).**
            5.  **Highlight the most important numerical values and trends observed in the table.** For example, "Women with osteoporosis had a significantly lower mean BMD (0.67 g/cm^2) compared to those with normal BMD (0.99 g/cm^2), p < 0.001."
            6.  **Explicitly state any statistically significant differences observed between groups, including p-values or confidence intervals, if available.** Mention the specific statistical test used, if known (e.g., ANOVA, Chi-square).
            7.  **Condense the table information to be easily searchable and retrievable, focusing on answering potential research questions related to menopause.**

            Table: {element}

            Summary:
            """
        )

        self.summarizer_chain = self.prompt_template | self.llm | StrOutputParser()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, text):
        self.logger.info("Generating summary for table.")

        try:
            summary = self.summarizer_chain.invoke({"element": text})
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    def generate_table_summaries(self, texts):
        summaries = []
        self.logger.info(f"Started generating summaries for {len(texts)} tables.")

        for idx, text in enumerate(texts, start=1):
            self.logger.info(f"Processing table {idx}/{len(texts)}")

            if self.request_counter >= self.max_requests_per_minute:
                elapsed = time.time() - self.first_request_time
                if elapsed < 60:
                    self.logger.info(f"Request limit reached, waiting for {60 - elapsed:.2f} seconds.")
                    time.sleep(60 - elapsed)
                self.request_counter = 0
                self.first_request_time = time.time()

            try:
                summary = self.generate_summary(text)
                if summary:
                    summaries.append(summary)
                    self.logger.info(f"Summary for table {idx} generated.")
                else:
                    self.logger.warning(f"No summary generated for table {idx}.")
            except Exception as e:
                self.logger.error(f"Error processing table {idx}: {e}")

            self.request_counter += 1

        return summaries