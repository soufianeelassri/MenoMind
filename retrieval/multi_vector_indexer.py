import uuid
import logging
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document

class MultiVectorRetrieverBuilder:
    def __init__(self, vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, images):
        self.vectorstore = vectorstore
        self.text_summaries = text_summaries
        self.texts = texts
        self.table_summaries = table_summaries
        self.tables = tables
        self.image_summaries = image_summaries
        self.images = images
        self.store = InMemoryStore()
        self.id_key = "doc_id"
        self.logger = self.setup_logger()
        
    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def add_documents(self, doc_summaries, doc_contents):
        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [Document(page_content=s, metadata={self.id_key: doc_ids[i]}) for i, s in enumerate(doc_summaries)]
        
        try:
            self.retriever.vectorstore.add_documents(summary_docs)
            self.retriever.docstore.mset(list(zip(doc_ids, doc_contents)))
            self.logger.info(f"Added {len(doc_summaries)} documents to the retriever.")
        except Exception as e:
            self.logger.error(f"Failed to add documents: {e}")

    def create_retriever(self):
        try:
            self.retriever = MultiVectorRetriever(
                vectorstore=self.vectorstore,
                docstore=self.store,
                id_key=self.id_key,
            )
            
            self.logger.info("Adding text documents to retriever.")
            self.add_documents(self.text_summaries, self.texts)
            
            self.logger.info("Adding table documents to retriever.")
            self.add_documents(self.table_summaries, self.tables)
            
            self.logger.info("Adding image documents to retriever.")
            self.add_documents(self.image_summaries, self.images)
            
            self.logger.info("Retriever created successfully.")
            return self.retriever
        
        except Exception as e:
            self.logger.error(f"Failed to create retriever: {e}")
            return None