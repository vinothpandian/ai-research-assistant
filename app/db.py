import pocketbase

from app.settings import settings


class DB:
    def __init__(self):
        self.db = pocketbase.PocketBase(settings.POCKETBASE_URL)

    def save_article(self, article):
        return self.db.collection('articles').create(article.model_dump())

    def remove_article(self, article):
        return self.db.collection('articles').delete(article.id)

    def get_articles(self):
        return self.db.collection('articles').get_full_list(query_params={'sort': '-created'})


db = DB()
