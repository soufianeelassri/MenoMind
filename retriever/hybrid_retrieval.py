from nltk.tokenize import word_tokenize
from langchain_core.documents import Document
from models.embedding_model import embedding_model
from models.bm25_model import bm25, docs, initialize_bm25
from retriever.reranker import DocumentReranker
from retriever.document_repacker import DocumentRepacker
from config import DEFAULT_RERANKING_ENABLED, DEFAULT_REPACKING_ENABLED, DEFAULT_REPACKING_METHOD, DEFAULT_MAX_TOKENS_PER_GROUP

# Initialize reranker and repacker
reranker = DocumentReranker()
repacker = DocumentRepacker(max_tokens_per_group=DEFAULT_MAX_TOKENS_PER_GROUP)

# Track if BM25 has been initialized
bm25_initialized = False

def hybrid_retrieve(query, vectorstore, k=10, 
                   use_reranking=DEFAULT_RERANKING_ENABLED, 
                   use_repacking=DEFAULT_REPACKING_ENABLED, 
                   repacking_method=DEFAULT_REPACKING_METHOD):
    """
    Hybrid retrieval combining dense and sparse retrievers with optional reranking and repacking
    
    Args:
        query: The search query
        vectorstore: The vector database for dense retrieval
        k: Number of documents to retrieve
        use_reranking: Whether to apply reranking to results
        use_repacking: Whether to repack documents
        repacking_method: Method for repacking ('similarity' or 'token_limit')
        
    Returns:
        List of retrieved documents
    """
    global bm25_initialized
    
    # Initialize BM25 if not done yet
    if not bm25_initialized:
        try:
            # Get documents from vectorstore
            result = vectorstore.get()
            if 'documents' in result and result['documents'] and len(result['documents']) > 0:
                initialize_bm25(result['documents'])
                bm25_initialized = True
        except Exception as e:
            print(f"Unable to initialize BM25: {e}")
    
    # Perform dense retrieval
    query_embedding = embedding_model.embed_query(query)
    dense_docs = vectorstore.similarity_search_by_vector(query_embedding, k=k*2 if not bm25 else k)
    
    # Check if BM25 is available and has documents
    if bm25 is not None and docs and len(docs) > 0:
        # Sparse retrieval with BM25
        try:
            bm25_query = word_tokenize(query.lower())
            sparse_scores = bm25.get_scores(bm25_query)
            
            # Only get top-k if we have enough results
            top_k = min(k, len(sparse_scores))
            if top_k > 0:
                top_k_indices = sorted(range(len(sparse_scores)), 
                                      key=lambda x: sparse_scores[x], 
                                      reverse=True)[:top_k]
                sparse_docs = [Document(page_content=docs[i]) for i in top_k_indices]
                
                # Combine and deduplicate results
                seen = set()
                combined_docs = []
                for doc in dense_docs + sparse_docs:
                    if doc.page_content not in seen:
                        combined_docs.append(doc)
                        seen.add(doc.page_content)
            else:
                combined_docs = dense_docs
        except Exception as e:
            print(f"Error in BM25 retrieval: {e}")
            combined_docs = dense_docs
    else:
        # Fall back to dense retrieval only
        combined_docs = dense_docs[:k]
    
    # Apply reranking if enabled
    if use_reranking and combined_docs:
        try:
            combined_docs = reranker.rerank(query, combined_docs, top_k=k)
        except Exception as e:
            print(f"Error in reranking: {e}")
    
    # Apply repacking if enabled
    if use_repacking and combined_docs:
        try:
            if repacking_method == "similarity":
                combined_docs = repacker.repack_by_similarity(combined_docs)
            elif repacking_method == "token_limit":
                combined_docs = repacker.repack_by_token_limit(combined_docs)
        except Exception as e:
            print(f"Error in repacking: {e}")
    
    # Ensure we don't exceed k documents
    return combined_docs[:k]