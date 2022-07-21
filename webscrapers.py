from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import dateutil.parser
from datetime import *
from dateutil.relativedelta import *
from tqdm import tqdm
from typing import List

from dataclasses import dataclass


@dataclass
class ArticleScraper:
    """
    Class which is instantiated with details of a news feed HTML page
    layout and supports scraping article details
    """
    # required
    url: str = None
    all_article_tag: str = None
    all_article_class: str = None
    article_tag: str = None
    date_tag: str = None
    date_class: str = None
    content_tag: str = None
    content_class: str = None

    # defined during run
    article_urls: List[str] = None
    article_details: List[dict] = None
    
    def __post_init__(self):
        self.base_url = re.match('^.+?[^\/:](?=[?\/]|$)', self.url).group(0)

    def _get_all_article_urls(self) -> None:
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')

        all_articles = soup.find(self.all_article_tag,
                                 attrs={'class': self.all_article_class})
        all_article_urls = all_articles.find_all(self.article_tag)
        return_urls = []
        for article_url in all_article_urls:
            if 'bbc' in self.base_url:
                return_urls.append(self.base_url + article_url.find('a')['href'])
            else:
                return_urls.append(article_url.find('a')['href'])
        print('number of article URLs found:', len(return_urls))
        self.article_urls = return_urls

    def _get_article_details(self) -> None:
        article_metadata = {}
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        article_metadata.update({'title': soup.title.text.strip()})
        try:
            article_date = soup.find(self.date_tag
                                     , attrs={'class': self.date_class})
            article_date = article_date.text.strip()
        except AttributeError:
            print('article date could not be found')
            article_date = ""

        try:
            post_content = soup.find(self.content_tag, attrs={'class': self.content_class})
        except AttributeError:
            print('error - article content could not be found')
            post_content = ""

        article_text = ""
        for para in post_content.find_all('p'):
            article_text += " " + para.text.strip()

        article_metadata.update(
            {
                'date': article_date,
                'content': post_content,
                'text': article_text
            }
        )
        self.article_details.append(article_metadata)

    def run(self) -> None:
        self._get_all_article_urls()
        self._get_article_details()


if __name__ == "__main__":

    article_scraper = ArticleScraper(
        url='https://www.optimistdaily.com/todays-solutions/',
        all_article_tag='div',
        all_article_class='single-post-content-sidebar-wrap',
        article_tag='article',
        date_tag='time',
        date_class='entry-time',
        content_tag='div',
        content_class='postContent'
    )
    article_scraper.run()
    pass