from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core import Settings

class Semantic(SemanticSplitterNodeParser):
    def __init__(self, buffer_size: int = 1, breakpoint_percentile_threshold: float = 95.0, embed_model = None):
        embed_model = embed_model or Settings.embed_model
        super().__init__(
            embed_model=embed_model,
            buffer_size=buffer_size,
            breakpoint_percentile_threshold=breakpoint_percentile_threshold
        )