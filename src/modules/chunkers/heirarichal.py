from llama_index.core.node_parser import HierarchicalNodeParser

class Hierarchical(HierarchicalNodeParser):
    @classmethod
    def from_defaults(cls, chunk_sizes=[2048, 512, 128], chunk_overlap=20):
        return super().from_defaults(chunk_sizes, chunk_overlap)
