from llama_index.core.node_parser import SentenceSplitter

class Recursive(SentenceSplitter):
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 60):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        