from llama_index.retrievers.bm25 import BM25Retriever

class BM25(BM25Retriever):
    
    @classmethod
    def from_defaults(cls, index = None, nodes = None, docstore = None, stemmer = None, language = "en", similarity_top_k = ..., verbose = False, tokenizer = None):
        return super().from_defaults(index, nodes, docstore, stemmer, language, similarity_top_k, verbose, tokenizer)
    