import uuid
import logging
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.documents import Document

class MultiVectorRetrieverBuilder:
    def __init__(self, vectorstore, text_elements, text_summaries, table_elements, table_summaries, img_base64_list, image_summaries):
        self.vectorstore = vectorstore
        self.text_elements = text_elements
        self.text_summaries = text_summaries or []
        self.table_elements = table_elements
        self.table_summaries = table_summaries
        self.img_base64_list = img_base64_list
        self.image_summaries = image_summaries
        self.store = InMemoryStore()
        self.id_key = "doc_id"
        self.logger = self.setup_logger()
        self.retriever = None

    def setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def chunk_list(self, lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    def add_documents(self, doc_summaries, doc_contents, batch_size=5000):
        if len(doc_summaries) != len(doc_contents):
            self.logger.error(f"Mismatch between summary count ({len(doc_summaries)}) and content count ({len(doc_contents)}). Skipping adding documents.")
            return

        if not doc_summaries:
            self.logger.info("No documents to add.")
            return

        doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
        summary_docs = [Document(page_content=s, metadata={self.id_key: doc_ids[i]}) for i, s in enumerate(doc_summaries)]
        content_tuples = list(zip(doc_ids, doc_contents))

        try:
            for doc_chunk, content_chunk in zip(self.chunk_list(summary_docs, batch_size), self.chunk_list(content_tuples, batch_size)):
                self.vectorstore.add_documents(doc_chunk)
                self.store.mset(content_chunk)
                self.logger.info(f"Added chunk of {len(doc_chunk)} documents.")
            self.logger.info(f"Successfully added {len(doc_summaries)} documents and their contents to the retriever stores.")
        except Exception as e:
            self.logger.error(f"Failed to add documents to retriever stores: {e}")

    def create_retriever(self):
        if self.vectorstore is None:
            self.logger.error("Vectorstore is not initialized.")
            return None

        try:
            self.retriever = MultiVectorRetriever(
                vectorstore=self.vectorstore,
                docstore=self.store,
                id_key=self.id_key,
            )
            
            if self.text_summaries:
                self.logger.info("Indexing text summaries and storing text content.")
                self.add_documents(self.text_summaries, self.text_elements)
            else:
                self.logger.info("No text summaries provided. Indexing text chunks directly.")
                self.add_documents(self.text_elements, self.text_elements)

            self.logger.info("Adding table documents to retriever.")
            self.add_documents(self.table_summaries, self.table_elements)

            self.logger.info("Adding image documents to retriever.")
            self.add_documents(self.image_summaries, self.img_base64_list)

            self.logger.info("Retriever created successfully.")
            return self.retriever

        except Exception as e:
            self.logger.error(f"Failed to create retriever: {e}")
            return None