"""
Reranker module for MenoMind
Implements cross-encoder based reranking functionality
"""

from typing import List
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

class DocumentReranker:
    """Class for reranking retrieved documents using a cross-encoder model"""
    
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """Initialize the reranker with a cross-encoder model"""
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: List[Document], top_k: int = None) -> List[Document]:
        """
        Rerank documents based on relevance to query
        
        Args:
            query: The query string
            documents: List of Document objects to rerank
            top_k: Number of documents to keep after reranking (defaults to all)
            
        Returns:
            Reranked list of Documents
        """
        if not documents:
            return []
            
        # Create document-query pairs for scoring
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Create documents with scores
        scored_docs = list(zip(documents, scores))
        
        # Sort by score in descending order
        reranked_docs = [doc for doc, score in sorted(scored_docs, key=lambda x: x[1], reverse=True)]
        
        # Return top_k documents if specified
        if top_k is not None and top_k < len(reranked_docs):
            return reranked_docs[:top_k]
        return reranked_docs 