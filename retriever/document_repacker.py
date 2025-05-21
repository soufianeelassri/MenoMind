"""
Document Repacker module for MenoMind
Implements functionality to repack retrieved documents for better context organization
"""

from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from langchain_core.documents import Document
from models.embedding_model import embedding_model

class DocumentRepacker:
    """Class for repacking documents based on semantic similarity"""
    
    def __init__(self, max_tokens_per_group=1000):
        """Initialize the repacker with configuration"""
        self.max_tokens_per_group = max_tokens_per_group
    
    def cluster_documents(self, documents: List[Document], n_clusters: int = 3) -> List[List[Document]]:
        """
        Cluster documents using K-means
        
        Args:
            documents: List of Document objects to cluster
            n_clusters: Number of clusters to create
            
        Returns:
            List of document clusters
        """
        if not documents or len(documents) < n_clusters:
            return [documents]
            
        # Get embeddings for all documents
        contents = [doc.page_content for doc in documents]
        embeddings = embedding_model.embed_documents(contents)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=min(n_clusters, len(documents)), random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        # Group documents by cluster
        grouped_docs = [[] for _ in range(max(clusters) + 1)]
        for i, doc in enumerate(documents):
            grouped_docs[clusters[i]].append(doc)
            
        return grouped_docs
        
    def repack_by_similarity(self, documents: List[Document]) -> List[Document]:
        """
        Repack documents by grouping similar content together
        
        Args:
            documents: List of Document objects to repack
            
        Returns:
            List of repacked Documents
        """
        if not documents:
            return []
            
        # For small document sets, no need to repack
        if len(documents) <= 2:
            return documents
            
        # Cluster documents
        n_clusters = min(3, len(documents) // 2)
        clusters = self.cluster_documents(documents, n_clusters)
        
        # Create new documents from clusters
        repacked_docs = []
        for i, cluster in enumerate(clusters):
            if not cluster:
                continue
                
            # Sort documents within cluster by metadata relevance if available
            if hasattr(cluster[0], "metadata") and "score" in cluster[0].metadata:
                cluster.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
                
            # Combine content from this cluster
            combined_content = f"Document Group {i+1}:\n\n"
            combined_content += "\n\n".join([doc.page_content for doc in cluster])
            
            # Create a new document
            metadata = {"source": f"repacked_group_{i+1}", "group_size": len(cluster)}
            repacked_doc = Document(page_content=combined_content, metadata=metadata)
            repacked_docs.append(repacked_doc)
            
        return repacked_docs
        
    def repack_by_token_limit(self, documents: List[Document], max_tokens: int = None) -> List[Document]:
        """
        Repack documents by token limit constraints
        
        Args:
            documents: List of Document objects to repack
            max_tokens: Maximum tokens per group (defaults to self.max_tokens_per_group)
            
        Returns:
            List of repacked Documents with token constraints
        """
        if max_tokens is None:
            max_tokens = self.max_tokens_per_group
            
        if not documents:
            return []
            
        # Rough approximation of token count
        def estimate_tokens(text):
            return len(text.split()) * 1.3
            
        repacked_docs = []
        current_group = []
        current_token_count = 0
        
        for doc in documents:
            doc_tokens = estimate_tokens(doc.page_content)
            
            # If this document would exceed our token limit, create a new group
            if current_token_count + doc_tokens > max_tokens and current_group:
                # Create a document from the current group
                combined_content = "\n\n".join([d.page_content for d in current_group])
                metadata = {"source": f"token_group_{len(repacked_docs)+1}", "group_size": len(current_group)}
                repacked_docs.append(Document(page_content=combined_content, metadata=metadata))
                
                # Start a new group with this document
                current_group = [doc]
                current_token_count = doc_tokens
            else:
                # Add this document to the current group
                current_group.append(doc)
                current_token_count += doc_tokens
                
        # Don't forget to add the last group
        if current_group:
            combined_content = "\n\n".join([d.page_content for d in current_group])
            metadata = {"source": f"token_group_{len(repacked_docs)+1}", "group_size": len(current_group)}
            repacked_docs.append(Document(page_content=combined_content, metadata=metadata))
            
        return repacked_docs 