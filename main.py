from dotenv import load_dotenv
import os
from newsapi import NewsApiClient
load_dotenv()

api_key = os.getenv("NEWSAPI_KEY")

newsapi = NewsApiClient(api_key=api_key)

top_headlines = newsapi.get_top_headlines(q='bitcoin',
                                          sources='bbc-news,the-verge',
                                          language='en')

# /v2/everything
all_articles = newsapi.get_everything(q='bitcoin',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2025-06-05',
                                      to='2025-07-04',
                                      language='en',
                                      sort_by='relevancy',
                                      page=2)
print(all_articles)
# /v2/top-headlines/sources
sources = newsapi.get_sources()
