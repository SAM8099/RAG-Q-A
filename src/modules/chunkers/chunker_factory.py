from src.modules.chunkers.recursive import Recursive
from src.modules.chunkers.semantic import Semantic
from src.modules.chunkers.heirarichal import Hierarchical

class ChunkerFactory:
    
    _REGISTRY = {
        "recursive": Recursive,
        "semantic": Semantic,
        "hierarchical": Hierarchical.from_defaults,
    }

    @staticmethod
    def get_chunker(strategy: str):

        clean_strategy = strategy.lower().strip()
        constructor = ChunkerFactory._REGISTRY.get(clean_strategy)
        
        if not constructor:
            supported = ", ".join(f"'{k}'" for k in ChunkerFactory._REGISTRY.keys())
            raise ValueError(
                f"Unknown chunking strategy: '{strategy}'. "
                f"Supported strategies are: {supported}"
            )
            
        return constructor()
