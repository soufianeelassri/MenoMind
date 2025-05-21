"""
Embedding Model for MenoMind
Uses sentence-transformers for generating embeddings
"""

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

class EmbeddingModel:
    """
    Wrapper class for embedding model to provide LangChain compatible interface
    """
    
    def __init__(self, model=model):
        self.model = model
        
    def embed_query(self, text):
        """Generate embeddings for a single text query"""
        return self.model.encode(text, show_progress_bar=False)
        
    def embed_documents(self, documents):
        """Generate embeddings for a list of documents"""
        return self.model.encode(documents, show_progress_bar=False)

# Create a singleton instance
embedding_model = EmbeddingModel()