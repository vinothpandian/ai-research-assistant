from typing import List, Iterable

from pydantic import AwareDatetime, BaseModel, RootModel


class Author(BaseModel):
    name: str


class ArxivArticle(BaseModel):
    id: str
    title: str
    summary: str
    link: str
    authors: List[Author]
    published: AwareDatetime


class ArxivArticlesList(RootModel):
    root: List[ArxivArticle]

    def __iter__(self) -> Iterable[ArxivArticle]:
        return iter(self.root)

    def __getitem__(self, item) -> ArxivArticle:
        return self.root[item]
