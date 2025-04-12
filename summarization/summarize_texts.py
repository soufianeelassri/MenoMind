import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class TextSummarizer:
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
                You are MenoSummarizer, an AI assistant specializing in creating structured summaries of medical research texts related to menopause for use in a Retrieval-Augmented Generation (RAG) system.  Your goal is to generate summaries that are both concise and comprehensive, capturing key findings and supporting details for optimal retrieval.

                Task: Summarize the following text segment related to menopause research. The summary should:

                1.  **Identify the research question or objective addressed in the text.**
                2.  **Outline the study design or methodology (e.g., cohort study, randomized controlled trial, etc.).**
                3.  **Summarize the key findings and results.  Include specific data points, effect sizes, p-values, confidence intervals, or other relevant statistics whenever possible.** Highlight statistically significant results.
                4.  **State the authors' conclusions or interpretations of the findings.**
                5.  **Mention any limitations acknowledged by the authors, if present.**
                6.  **Use concise and medically accurate language.**
                7.  **Focus on aspects most relevant to understanding menopause and its management (symptoms, treatments, risk factors, etc.).**

                Text: {element}

                Summary:
                """
        )
        
        self.summarizer_chain = self.prompt_template | self.llm | StrOutputParser()

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def generate_summary(self, text):
        self.logger.info("Generating summary for text.")
        
        try:
            summary = self.summarizer_chain.invoke({"element": text})
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    def generate_text_summaries(self, texts):
        summaries = []
        self.logger.info(f"Started generating summaries for {len(texts)} texts.")
        
        for idx, text in enumerate(texts, start=1):
            self.logger.info(f"Processing text {idx}/{len(texts)}")

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
                    self.logger.info(f"Summary for text {idx} generated.")
                else:
                    self.logger.warning(f"No summary generated for text {idx}.")
            except Exception as e:
                self.logger.error(f"Error processing text {idx}: {e}")
            
            self.request_counter += 1
            
        return summaries