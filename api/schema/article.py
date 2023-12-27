from typing import List

from pydantic import AwareDatetime, BaseModel, RootModel


class CreateArticle(BaseModel):
    arxiv_id: str
    title: str
    abstract: str
    link: str
    published: AwareDatetime
    authors: List[str]


class Article(CreateArticle):
    id: str | None = None
    ai_summary: str = ""
    vector_id: str = ""


class ArticlesList(RootModel):
    root: List[Article]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]
