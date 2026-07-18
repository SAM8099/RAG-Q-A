from newsapi import NewsApiClient
from src.modules.config import NEWSAPI_KEY
from src.utils.singleton import Singleton


class NewsService(metaclass=Singleton):
    """
    Singleton service for NewsAPI client.
    Initialized once and reused across all requests.
    """

    def __init__(self) -> None:
        self._client = NewsApiClient(api_key=NEWSAPI_KEY)

    def get_client(self) -> NewsApiClient:
        return self._client

    def fetch_headlines(self, topic: str = "", page_size: int = 15) -> list[dict]:
        """
        Fetch top headlines from NewsAPI.
        Returns plain list of dicts — response shaping is handled in routes.py.
        Raises RuntimeError if the request fails.
        """
        try:
            if topic:
                response = self._client.get_top_headlines(
                    category=topic,
                    language="en",
                    page_size=page_size,
                )
            else:
                response = self._client.get_top_headlines(
                    language="en",
                    page_size=page_size,
                )

            return [
                {
                    "title": a["title"],
                    "description": a["description"],
                    "url": a["url"],
                    "source": a["source"]["name"],
                }
                for a in response["articles"]
                if a["title"] and a["description"]
            ]

        except Exception as e:
            raise RuntimeError(f"Failed to fetch news: {e}")