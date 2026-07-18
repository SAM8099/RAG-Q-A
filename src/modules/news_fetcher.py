from llama_index.core.schema import TextNode


def format_articles_to_nodes(articles: list[dict]) -> list[TextNode]:
    """
    Convert articles into LlamaIndex TextNodes with metadata.
    Metadata (source, title, url) is preserved through chunking
    and used later for source attribution in responses.
    """
    return [
        TextNode(
            text=f"Title: {a['title']}\nDescription: {a['description']}",
            metadata={
                "source": a["source"],
                "title": a["title"],
                "url": a["url"],
            },
        )
        for a in articles
        if a["title"] and a["description"]
    ]