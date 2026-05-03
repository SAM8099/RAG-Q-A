from newsapi import NewsApiClient

from src.responses.news import NewsResponse, NewsListResponse
from src.modules.config import NEWSAPI_KEY
from src.utils.singleton import Singleton


class NewsService(metaclass=Singleton):

    def __init__(self) -> None:
        self._client = NewsApiClient(api_key=NEWSAPI_KEY)

    def get_client(self) -> NewsApiClient:
        return self._client

    def fetch_headlines(self, topic: str = "", page_size: int = 15) -> NewsListResponse:

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

            return NewsListResponse(
                news=[
                    NewsResponse(
                        title=a["title"],
                        description=a["description"],
                        url=a["url"],
                        source=a["source"]["name"],
                    )
                    for a in response["articles"]
                    if a["title"] and a["description"]
                ]
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch news: {e}")