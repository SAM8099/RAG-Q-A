
class NewsFetcher:

    @staticmethod
    def fetch_news(topic: str, num_articles: int = 5) -> list[dict]:
        """
        Simulate fetching news articles for a given topic.
        Returns a list of article dicts with 'source', 'title', and 'description'.
        """
        # Simulated articles
        return [
            {
                "source": f"Source {i+1}",
                "title": f"{topic.capitalize()} News Article {i+1}",
                "description": f"This is a description of {topic} news article {i+1}.",
            }
            for i in range(num_articles)
        ]