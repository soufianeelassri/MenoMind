from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from models.vectorstore import vectorstore

docs = vectorstore.get()['documents']

tokenized_corpus = [word_tokenize(doc.lower()) for doc in docs]

bm25 = BM25Okapi(tokenized_corpus)