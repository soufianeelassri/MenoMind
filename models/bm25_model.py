"""
BM25 Model for sparse retrieval in MenoMind
"""

from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize

# Initialize with empty data
docs = []
tokenized_corpus = []
bm25 = None 

def initialize_bm25(documents):
    """Initialize BM25 with documents from the vectorstore"""
    global docs, tokenized_corpus, bm25
    docs = documents
    
    if docs and len(docs) > 0:
        try:
            tokenized_corpus = [word_tokenize(doc.lower()) for doc in docs]
            bm25 = BM25Okapi(tokenized_corpus)
            return bm25
        except Exception as e:
            print(f"Error initializing BM25: {e}")
            # If tokenization fails, set to None
            bm25 = None
    else:
        # If no docs, set to None
        bm25 = None
    
    return bm25