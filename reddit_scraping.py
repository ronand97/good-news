from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type
import praw
import datetime
import pandas as pd
import re

@dataclass
class RedditScraper:
    # auth vars
    username: str = None
    password: str = None
    client_id: str = None
    client_secret: str = None
    user_agent: str = None

    # config vars
    subreddit: str = "upliftingnews"
    time_period: str = "day"
    top_n: int = 5

    # defined during run
    reddit: praw.Reddit = None
    data: pd.DataFrame = None

    def __enter__(self):
        self.reddit_auth()
        return self

    def __exit__(self, exctype: Optional[Type[BaseException]],
                 excinst: Optional[BaseException],
                 exctb: Optional[TracebackType]) -> bool:
        pass

    def reddit_auth(self):
        """
        auth to reddit giving a usable client to perform queries
        :return:
        """
        self.reddit = praw.Reddit(
            username=self.username,
            password=self.password,
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

    def get_top_reddit_posts(self):
        posts = (self.reddit
                 .subreddit(self.subreddit)
                 .top(self.time_period))
        dfs = []
        cols = ['url', 'title', 'date', 'text', 'root_url']
        for post in posts:
            utc = post.created_utc
            fmt = '%B %d, %Y'
            date = datetime.datetime.utcfromtimestamp(utc).strftime(fmt)
            root_url = re.match('^.+?[^\/:](?=[?\/]|$)', post.url).group(0)
            data = [post.url, post.title, date, '', root_url]
            dfs.append(pd.DataFrame([data], columns=cols))
        self.data = pd.concat(dfs).head(self.top_n)

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    reddit_scraper = RedditScraper(
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD"),
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT")
    )


    with reddit_scraper as rc:
        rc.get_top_reddit_posts()
    pass