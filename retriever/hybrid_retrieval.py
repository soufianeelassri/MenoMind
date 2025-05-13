from nltk.tokenize import word_tokenize
from langchain_core.documents import Document
from models.embedding_model import embedding_model
from models.bm25_model import bm25, docs

def hybrid_retrieve(query, vectorstore, k=10):
    if not docs:
        query_embedding = embedding_model.embed_query(query)
        dense_docs = vectorstore.similarity_search_by_vector(query_embedding, k=k*2)
        return dense_docs[:k]

    query_embedding = embedding_model.embed_query(query)
    dense_docs = vectorstore.similarity_search_by_vector(query_embedding, k=k)

    bm25_query = word_tokenize(query.lower())
    sparse_scores = bm25.get_scores(bm25_query)
    top_k_indices = sorted(range(len(sparse_scores)), key=lambda x: sparse_scores[x], reverse=True)[:k]
    sparse_docs = [Document(page_content=docs[i]) for i in top_k_indices]

    seen = set()
    unique_docs = []
    for doc in dense_docs + sparse_docs:
        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)

    return unique_docs[:k]